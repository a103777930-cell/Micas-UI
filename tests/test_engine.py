import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile
import posixpath
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from PIL import Image
from micas_ppt.engine import convert, ROOT


class ConversionTests(unittest.TestCase):
    def test_native_round_trip(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prs = Presentation()
            s = prs.slides.add_slide(prs.slide_layouts[1])
            s.shapes.title.text = '技术说明'
            tf = s.placeholders[1].text_frame
            tf.text = '第一段'
            for i in range(45):
                tf.add_paragraph().text = f'记录 {i}: ERROR --verbose 日志和技术内容，保留完整内容。' * 3
            s.notes_slide.notes_text_frame.text = '讲者备注需要保留'
            s = prs.slides.add_slide(prs.slide_layouts[5])
            s.shapes.title.text = '数据'
            table = s.shapes.add_table(3, 2, Inches(1), Inches(1), Inches(4), Inches(2)).table
            table.cell(0, 0).text = '指标'
            table.cell(1, 1).text = '42'
            chart = CategoryChartData()
            chart.categories = ['A', 'B']
            chart.add_series('销量', [10, 20])
            s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6), Inches(1), Inches(4), Inches(3), chart)
            s = prs.slides.add_slide(prs.slide_layouts[5])
            s.shapes.title.text = '图片'
            Image.new('RGB', (400, 200), 'red').save(tmp/'image.png')
            s.shapes.add_picture(str(tmp/'image.png'), Inches(1), Inches(1))
            s.shapes.add_textbox(Inches(6), Inches(1), Inches(3), Inches(2)).text = '截图说明'
            src, out = tmp/'input.pptx', tmp/'output.pptx'
            prs.save(src)
            template = ROOT/'templates/presentations/micas-official-ppt/v1.0.0/PPT_Template_2026.pptx'
            digest = hashlib.sha256(template.read_bytes()).hexdigest()
            result = convert(src, out)
            self.assertFalse(result['integrity']['missing_text'])
            self.assertFalse(result['integrity']['missing_objects'])
            self.assertFalse(result['integrity']['changed_binary_payloads'])
            self.assertGreater(result['integrity']['binary_payloads_checked'], 0)
            self.assertFalse(any('content_object_overlap' in s['checks'] for s in result['slides']))
            self.assertGreater(result['integrity']['output_slides'], 3)
            self.assertGreaterEqual(len(set(s['layout'] for s in result['slides'])), 3)
            reopened = Presentation(out)
            shapes = [sh for s in reopened.slides for sh in s.shapes]
            self.assertTrue(any(sh.has_table and sh.table.cell(1, 1).text == '42' for sh in shapes))
            charts = [sh.chart for sh in shapes if sh.has_chart]
            self.assertEqual(list(charts[0].series[0].values), [10, 20])
            self.assertTrue(any(s.has_notes_slide and '讲者备注' in s.notes_slide.notes_text_frame.text for s in reopened.slides))
            self.assertEqual(digest, hashlib.sha256(template.read_bytes()).hexdigest())
            with ZipFile(out) as z:
                self.assertIsNone(z.testzip())
                for name in z.namelist():
                    if not name.endswith('.rels'):
                        continue
                    base = posixpath.dirname(posixpath.dirname(name))
                    for rel in etree.fromstring(z.read(name)):
                        if rel.get('TargetMode') == 'External':
                            continue
                        target = rel.get('Target')
                        path = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(base, target))
                        self.assertIn(path, z.namelist(), (name, target))

    def test_risk_blocks_and_reports(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prs = Presentation()
            s = prs.slides.add_slide(prs.slide_layouts[6])
            etree.SubElement(s._element, '{http://schemas.openxmlformats.org/presentationml/2006/main}timing')
            prs.save(tmp/'in.pptx')
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                convert(tmp/'in.pptx', tmp/'out.pptx')
            self.assertFalse((tmp/'out.pptx').exists())
            self.assertEqual(json.loads((tmp/'out.report.json').read_text())['status'], 'blocked_unsupported_objects')
            result = convert(tmp/'in.pptx', tmp/'out.pptx', allow_risk=True)
            self.assertTrue(result['warnings'])

    def test_two_pictures_do_not_overlap(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            Image.new('RGB', (100, 60), 'blue').save(tmp/'image.png')
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            for x in (1, 5):
                slide.shapes.add_picture(str(tmp/'image.png'), Inches(x), Inches(1))
            prs.save(tmp/'in.pptx')
            result = convert(tmp/'in.pptx', tmp/'out.pptx')
            self.assertEqual(result['slides'][0]['layout'], 7)
            self.assertNotIn('content_object_overlap', result['slides'][0]['checks'])

    def test_indivisible_paragraph_reports_overflow(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(3)).text = '日志' * 4000
            prs.save(tmp/'in.pptx')
            result = convert(tmp/'in.pptx', tmp/'out.pptx')
            self.assertFalse(result['integrity']['missing_text'])
            self.assertTrue(any('estimated_text_overflow' in check for check in result['slides'][0]['checks']))

    def test_refuse_overwrite_input(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)/'input.pptx'
            Presentation().save(p)
            before = p.read_bytes()
            with self.assertRaises(ValueError):
                convert(p, p)
            self.assertEqual(before, p.read_bytes())


if __name__ == '__main__':
    unittest.main()
