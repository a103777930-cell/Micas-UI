"""Conservative native-object conversion; no rendering or model API required."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import posixpath
import re
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

ROOT = Path(__file__).resolve().parents[1]
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
PREFIX = 'micas-source/'
LIMITATIONS = [
    'No rendered validation: text capacity and geometry checks are estimates; verify fonts and appearance in PowerPoint.',
    'No OCR or semantic interpretation of screenshots; pictures remain pictures.',
    'SmartArt, OLE, media, animation, transitions and special charts are not reliably supported.',
    'Theme-dependent source objects can change appearance under the official theme; object data is retained.',
    'Slide links, comments, custom shows and slide-level behavior are not migrated to the new slide sequence.',
    'Source master/layout decorations and backgrounds are replaced by the official template; source-only inherited content requires review.',
    'Tables are kept as whole objects; dense tables and indivisible long paragraphs require manual review rather than destructive splitting.',
    'Reading order is inferred top-to-bottom then left-to-right; author intent and semantic grouping require review.',
]


def _texts(root):
    return [x.text or '' for x in root.xpath('.//*[local-name()="t"]')]


def _tokens(prs):
    return Counter(t for s in prs.slides for sh in s.shapes for t in _texts(sh._element) if t)


def _box(shape):
    return tuple(int(v or 0) for v in (shape.left, shape.top, shape.width, shape.height))


def _risk(slide):
    xml = etree.tostring(slide._element).decode()
    risks = [name for name, pattern in {
        'SmartArt': 'drawingml/2006/diagram', 'OLE': 'oleObj',
        'animation': '<p:timing', 'transition': '<p:transition',
        'media': 'videoFile|audioFile|media', 'alternate content': 'AlternateContent',
        'connector topology': 'cxnSp', 'group geometry': '<p:grpSp[ >]',
    }.items() if re.search(pattern, xml)]
    for sh in slide.shapes:
        if sh.has_chart:
            try:
                if int(sh.chart.chart_type) not in (4, 5, 51, 52, 53, 57, 58, 59, 63, 64, 65, 66, 67, 69):
                    risks.append('special chart')
            except (ValueError, NotImplementedError):
                risks.append('unknown chart')
    return sorted(set(risks))


def _technical(text):
    return bool(re.search(r'(^\s*[$>#]|Traceback|\bERROR\b|```|\bdef |\bSELECT |https?://|--\w)', text, re.M))


def _chunks(shape, width=11.9, height=5.25):
    """Split only text-only shapes, at paragraph boundaries, preserving run XML."""
    if not shape.has_text_frame or shape.shape_type not in (1, 14, 17):
        return [deepcopy(shape._element)]
    text = shape.text
    font = 16 if _technical(text) else 20
    # Conservative CJK-aware width and line-height estimate.
    capacity = max(1, int(height * 72 / (font * 1.4)))
    columns = max(1, int(width * 72 / font))
    paragraphs = list(shape._element.xpath('.//p:txBody/a:p'))
    groups, current, used = [], [], 0
    for p in paragraphs:
        value = ''.join(_texts(p))
        units = sum(1 if ord(c) > 255 else .6 for c in value)
        lines = max(1, math.ceil(units / columns))
        if current and used + lines > capacity:
            groups.append(current)
            current, used = [], 0
        current.append(p)
        used += lines
    if current:
        groups.append(current)
    result = []
    for group in groups:
        el = deepcopy(shape._element)
        body = el.find('{http://schemas.openxmlformats.org/presentationml/2006/main}txBody')
        if body is None:
            return [deepcopy(shape._element)]
        for p in list(body):
            if etree.QName(p).localname == 'p':
                body.remove(p)
        for p in group:
            body.append(deepcopy(p))
        result.append(el)
    return result or [deepcopy(shape._element)]


def _style(shape, title=False):
    if not shape.has_text_frame:
        return
    technical = _technical(shape.text)
    size = 28 if title else (16 if technical else 20)
    shape.text_frame.word_wrap = True
    for p in shape.text_frame.paragraphs:
        p.space_after = Pt(5)
        for run in p.runs:
            run.font.name = 'Consolas' if technical else 'Arial'
            run.font.size = Pt(size)
            run.font.color.rgb = RGBColor.from_string('4D5E69')
    # Explicit East Asian font avoids inheriting inappropriate Latin-only fonts.
    for rp in shape._element.xpath('.//a:rPr'):
        ea = rp.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
        if ea is None:
            ea = etree.SubElement(rp, '{http://schemas.openxmlformats.org/drawingml/2006/main}ea')
        ea.set('typeface', '微软雅黑')


def _import_package(base, source, output, relationships):
    """Namespace source parts, preserving opaque dependency graphs and native data."""
    with ZipFile(base) as dst, ZipFile(source) as src, ZipFile(output, 'w') as out:
        ctypes = etree.fromstring(dst.read('[Content_Types].xml'))
        source_ct = etree.fromstring(src.read('[Content_Types].xml'))
        defaults = {el.get('Extension') for el in ctypes if etree.QName(el).localname == 'Default'}
        for el in source_ct:
            item = deepcopy(el)
            if etree.QName(el).localname == 'Override':
                item.set('PartName', '/' + PREFIX + el.get('PartName').lstrip('/'))
                ctypes.append(item)
            elif el.get('Extension') not in defaults:
                ctypes.append(item)
                defaults.add(el.get('Extension'))
        for name in dst.namelist():
            if name == '[Content_Types].xml':
                out.writestr(name, etree.tostring(ctypes, xml_declaration=True, encoding='UTF-8'))
            elif name in relationships:
                root = etree.fromstring(dst.read(name))
                for rid, target, reltype, external in relationships[name]:
                    attrs = dict(Id=rid, Type=reltype, Target=target)
                    if external:
                        attrs['TargetMode'] = 'External'
                    etree.SubElement(root, '{'+P+'}Relationship', **attrs)
                out.writestr(name, etree.tostring(root, xml_declaration=True, encoding='UTF-8'))
            else:
                out.writestr(name, dst.read(name))
        for name in src.namelist():
            if name == '[Content_Types].xml' or name.endswith('/'):
                continue
            data = src.read(name)
            if name.endswith('.rels'):
                root = etree.fromstring(data)
                for rel in root:
                    if rel.get('TargetMode') != 'External' and rel.get('Target', '').startswith('/'):
                        rel.set('Target', '/' + PREFIX + rel.get('Target').lstrip('/'))
                data = etree.tostring(root, xml_declaration=True, encoding='UTF-8')
            out.writestr(PREFIX + name, data)


def convert(source, output, report=None, *, repo_root=None, allow_risk=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    report = Path(report).resolve() if report else output.with_suffix('.report.json')
    root = Path(repo_root).resolve() if repo_root else ROOT
    entry = next(e for e in json.loads((root/'templates/catalog.json').read_text(encoding='utf-8'))['templates'] if e['id'] == 'micas-official-ppt')
    template = root / entry['path']
    mapping = template.parent.parent / 'layout-mapping.md'
    protected = {source, template.resolve(), mapping.resolve(), (root/'templates/catalog.json').resolve()}
    if output in protected or report in protected or output == report:
        raise ValueError('Input, template, mapping, catalog, output and report must use distinct paths')
    if sha256(template.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Official template checksum mismatch')
    if 'L15' not in mapping.read_text(encoding='utf-8') or 'L7' not in mapping.read_text(encoding='utf-8'):
        raise ValueError('Unsupported layout mapping')
    original = Presentation(source)
    target = Presentation(template)
    if len(target.slide_layouts) != 23:
        raise ValueError('Unexpected official layout structure')
    result = dict(engine_version='0.1.0', source=str(source), template_sha256=entry['sha256'],
                  mapping_sha256=sha256(mapping.read_bytes()).hexdigest(), limitations=LIMITATIONS,
                  slides=[], warnings=[], status='pending', source_structure=[])
    for i, slide in enumerate(original.slides, 1):
        result['source_structure'].append(dict(source_slide=i,
            size_emu=[original.slide_width, original.slide_height],
            shapes=[dict(id=sh.shape_id, bounds_emu=_box(sh),
                         text=sh.has_text_frame, table=sh.has_table, chart=sh.has_chart,
                         xml_type=etree.QName(sh._element).localname) for sh in slide.shapes]))
        risks = _risk(slide)
        if risks:
            result['warnings'].append(dict(source_slide=i, risks=risks))
    report.parent.mkdir(parents=True, exist_ok=True)
    if result['warnings'] and not allow_risk:
        result['status'] = 'blocked_unsupported_objects'
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        raise ValueError(f'Unsupported objects detected; see {report}; use --allow-risk only after reviewing limitations')
    # Remove demonstration slides, retain official master/layout/theme and decorations.
    for sid in list(target.slides._sldIdLst):
        target.part.drop_rel(sid.rId)
        target.slides._sldIdLst.remove(sid)
    relations = {}
    for index, slide in enumerate(original.slides, 1):
        title = slide.shapes.title
        objects = sorted([sh for sh in slide.shapes if sh != title], key=lambda sh: (sh.top or 0, sh.left or 0))
        pages = []
        for sh in objects:
            chunks = _chunks(sh)
            pages.extend([(sh, el) for el in chunks])
        # Pair compact independent objects; complex native diagrams stay intact as objects.
        batches = []
        while pages:
            first = pages.pop(0)
            if pages and sum(map(len, _texts(first[1]))) < 350 and sum(map(len, _texts(pages[0][1]))) < 350 and first[0] is not pages[0][0]:
                batches.append([first, pages.pop(0)])
            else:
                batches.append([first])
        batches = batches or [[]]
        for continuation, batch in enumerate(batches):
            picture = sum(sh.shape_type == 13 for sh, _ in batch) == 1 and any(sh.has_text_frame for sh, _ in batch)
            cover = index == 1 and not batch and title is not None
            layout_index = 1 if cover else (14 if picture and len(batch) == 2 else (6 if len(batch) == 2 else 4))
            dest = target.slides.add_slide(target.slide_layouts[layout_index])
            for sh in list(dest.shapes):
                dest.shapes._spTree.remove(sh._element)
            record = dict(source_slide=index, output_slide=len(target.slides), continuation=continuation,
                          layout=layout_index+1, objects=[], checks=[])
            rel_list = []
            rel_path = f'ppt/slides/_rels/slide{len(target.slides)}.xml.rels'
            def clone(el, source_shape, bounds, is_title=False):
                el = deepcopy(el)
                for ph in el.xpath('.//p:ph'):
                    ph.getparent().remove(ph)
                if el.tag.endswith('}sp') and not el.xpath('./p:spPr/a:prstGeom | ./p:spPr/a:custGeom'):
                    props = el.find('.//{http://schemas.openxmlformats.org/presentationml/2006/main}cNvSpPr')
                    if props is not None:
                        props.set('txBox', '1')
                for node in el.iter():
                    for attr, rid in list(node.attrib.items()):
                        if attr.startswith('{'+R+'}'):
                            rel = slide.part.rels[rid]
                            new_id = f'rIdMicas{len(rel_list)+1}'
                            node.set(attr, new_id)
                            external = rel.is_external
                            link = rel.target_ref if external else posixpath.relpath(PREFIX + str(rel.target_part.partname).lstrip('/'), 'ppt/slides')
                            rel_list.append((new_id, link, rel.reltype, external))
                used_ids = [int(n.get('id', '0')) for n in dest._element.xpath('.//p:cNvPr')]
                next_id = max(used_ids, default=1) + 1
                for offset, nv in enumerate(el.xpath('.//p:cNvPr')):
                    nv.set('id', str(next_id + offset))
                dest.shapes._spTree.insert_element_before(el, 'p:extLst')
                new = dest.shapes[-1]
                new.left, new.top, new.width, new.height = [Inches(v) for v in bounds]
                # Preserve picture aspect ratio/crop; native chart/table XML stays editable.
                if new.shape_type == 13:
                    _, _, sw, sh = _box(source_shape)
                    if sw and sh:
                        ratio = min(bounds[2]/sw, bounds[3]/sh)
                        new.width, new.height = Inches(sw*ratio), Inches(sh*ratio)
                        new.left = Inches(bounds[0] + (bounds[2]-sw*ratio)/2)
                        new.top = Inches(bounds[1] + (bounds[3]-sh*ratio)/2)
                _style(new, is_title)
                if not is_title:
                    record['objects'].append(dict(source_shape_id=source_shape.shape_id, type=str(source_shape.shape_type), text_nodes=len(_texts(el))))
                return new
            if title is not None:
                clone(title._element, title, (4.986, 3.02, 7.60, 1.69) if cover else (0.65, .25, 11.9, .65), True)
            for k, (sh, el) in enumerate(batch):
                if len(batch) == 1:
                    bounds = (.65, 1.1, 11.9, 5.25)
                elif layout_index == 14:
                    bounds = (.65, 1.1 if sh.shape_type != 13 else 3.25, 11.9, 2.0 if sh.shape_type != 13 else 3.0)
                else:
                    bounds = (.65 + k*6.1, 1.1, 5.8, 5.25)
                new = clone(el, sh, bounds)
                if new.has_table:
                    # Resize grid as well as frame; retain merged cells and cell XML.
                    total = sum(c.width for c in new.table.columns)
                    for col in new.table.columns:
                        col.width = int(col.width * new.width / total)
                    total_h = sum(r.height for r in new.table.rows)
                    for row in new.table.rows:
                        row.height = int(row.height * new.height / total_h)
                    record['checks'].append('table_font_and_cell_overflow_require_visual_review')
                if new.has_text_frame:
                    units = sum(1 if ord(c)>255 else .6 for c in new.text)
                    capacity = bounds[2]*72/20 * bounds[3]*72/28
                    if units > capacity:
                        record['checks'].append('estimated_text_overflow: oversized paragraph or narrow column; manual review required')
                x,y,w,h = _box(new)
                if min(x,y) < 0 or x+w > target.slide_width or y+h > target.slide_height:
                    record['checks'].append('out_of_bounds')
            if slide.has_notes_slide:
                note_rel = next(r for r in slide.part.rels.values() if r.reltype.endswith('/notesSlide'))
                rel_list.append(('rIdMicasNotes', posixpath.relpath(PREFIX+str(note_rel.target_part.partname).lstrip('/'), 'ppt/slides'), note_rel.reltype, False))
            # Geometry checks concern generated content, not intentional master decorations.
            content_boxes = [_box(sh) for sh in dest.shapes]
            for a in range(len(content_boxes)):
                for b in range(a+1, len(content_boxes)):
                    x,y,w,h = content_boxes[a]
                    xx,yy,ww,hh = content_boxes[b]
                    if min(x+w,xx+ww)-max(x,xx) > 9144 and min(y+h,yy+hh)-max(y,yy) > 9144:
                        record['checks'].append('content_object_overlap')
            if title is not None and len(title.text) > 65:
                record['checks'].append('long_title_requires_visual_review')
            relations[rel_path] = rel_list
            result['slides'].append(record)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as tmp:
        intermediate = Path(tmp)/'base.pptx'
        final = Path(tmp)/'final.pptx'
        target.save(intermediate)
        _import_package(intermediate, source, final, relations)
        reopened = Presentation(final)
        before, after = _tokens(original), _tokens(reopened)
        missing = before - after
        result['integrity'] = dict(input_text_nodes=sum(before.values()), output_text_nodes=sum(after.values()), missing_text=dict(missing),
                                   input_slides=len(original.slides), output_slides=len(reopened.slides),
                                   source_package_archived=True)
        expected_objects = {(i, sh.shape_id) for i, sl in enumerate(original.slides, 1) for sh in sl.shapes if sh != sl.shapes.title}
        actual_objects = {(sl['source_slide'], ob['source_shape_id']) for sl in result['slides'] for ob in sl['objects']}
        missing_objects = sorted(expected_objects - actual_objects)
        result['integrity']['missing_objects'] = missing_objects
        # Binary payloads must survive byte-for-byte, including chart workbooks and pictures.
        with ZipFile(source) as zin, ZipFile(final) as zout:
            payloads = [n for n in zin.namelist() if not n.endswith(('.xml', '.rels', '/')) and n != '[Content_Types].xml']
            changed_payloads = [n for n in payloads if zin.read(n) != zout.read(PREFIX+n)]
        broken_relationships = []
        with ZipFile(final) as package:
            names = set(package.namelist())
            for name in names:
                if not name.endswith('.rels'):
                    continue
                base = posixpath.dirname(posixpath.dirname(name))
                for rel in etree.fromstring(package.read(name)):
                    if rel.get('TargetMode') == 'External':
                        continue
                    link = rel.get('Target', '')
                    resolved = link.lstrip('/') if link.startswith('/') else posixpath.normpath(posixpath.join(base, link))
                    if resolved not in names:
                        broken_relationships.append(dict(part=name, target=link))
            corrupt_part = package.testzip()
        result['integrity']['broken_relationships'] = broken_relationships
        result['integrity']['corrupt_part'] = corrupt_part
        result['integrity']['binary_payloads_checked'] = len(payloads)
        result['integrity']['changed_binary_payloads'] = changed_payloads
        if missing or missing_objects or changed_payloads or broken_relationships or corrupt_part:
            result['status'] = 'failed_integrity'
            report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            raise ValueError('Text integrity check failed; output not published')
        result['status'] = 'completed_with_review_required'
        output.write_bytes(final.read_bytes())
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result
