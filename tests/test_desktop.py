import json
from pathlib import Path
from queue import Queue
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pptx import Presentation
from micas_ppt.desktop import Job, run_job, DesktopApp, resource_root, _publish_new


class DesktopWorkerTests(unittest.TestCase):
    def test_conversion_no_overwrite_and_repeated_runs(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp/'员工 演示.pptx'
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = '标题'
            slide.placeholders[1].text = '保留的文字'
            prs.save(source)
            original = source.read_bytes()
            existing = tmp/'员工 演示_Micas.pptx'; existing.write_bytes(b'previous')
            for suffix in ('_2', '_3'):
                events = Queue(); run_job(Job(source, tmp), events)
                records = []
                while not events.empty():
                    records.append(events.get())
                self.assertEqual(records[-1][0], 'done')
                result = records[-1][1]
                self.assertEqual(result['output'].name, f'员工 演示_Micas{suffix}.pptx')
                self.assertEqual(json.loads(result['report'].read_text(encoding='utf-8'))['integrity']['missing_text'], {})
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(existing.read_bytes(), b'previous')

    def test_failure_report_and_safe_mode(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp/'input.pptx'; source.write_bytes(b'fixture')
            calls = []
            def reject(source, output, report, **kwargs):
                calls.append(kwargs)
                report.write_text('{"status":"blocked_unsupported_objects","warnings":["OLE"]}', encoding='utf-8')
                raise ValueError('Unsupported objects detected')
            events = Queue(); run_job(Job(source, tmp), events, reject)
            events.get(); kind, payload = events.get()
            self.assertEqual(kind, 'error')
            self.assertTrue(payload['report'].exists())
            self.assertFalse((tmp/'input_Micas.pptx').exists())
            self.assertFalse(calls[0]['allow_risk'])
            self.assertIn('停止转换', DesktopApp.friendly_error(payload['message']))

    def test_invalid_input_and_exclusive_output(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            with self.assertRaises(ValueError):
                Job(tmp/'missing.pptx', tmp).validate()
            a, b = tmp/'a', tmp/'b'; a.write_bytes(b'a'); b.write_bytes(b'b')
            with self.assertRaises(FileExistsError):
                _publish_new(a, b)
            self.assertEqual(b.read_bytes(), b'b')
            events = Queue(); run_job(Job(a, tmp), events)
            self.assertEqual(events.get()[0], 'error')

    def test_frozen_resource_resolution(self):
        with patch('sys._MEIPASS', '/bundled/app', create=True):
            self.assertEqual(resource_root(), Path('/bundled/app'))


class WidgetTests(unittest.TestCase):
    def setUp(self):
        import tkinter as tk
        try:
            self.root = tk.Tk(); self.root.withdraw()
        except tk.TclError as exc:
            self.skipTest(f'No GUI display: {exc}')
        self.app = DesktopApp(self.root)

    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_status_and_success_controls(self):
        self.app.busy = True
        self.app.events.put(('done', {'output': Path('/tmp/output.pptx'), 'report': Path('/tmp/report.json'), 'result': {'integrity': {'output_slides': 2}}}))
        self.app.poll()
        self.assertFalse(self.app.busy)
        self.assertEqual(str(self.app.open_button['state']), 'normal')
        self.assertEqual(str(self.app.report_button['state']), 'normal')
        self.assertIn('2 页', self.app.status.get())

    def test_worker_does_not_block_tk_and_prevents_duplicate_start(self):
        from threading import Event
        entered, release = Event(), Event()
        def fake_worker(job, events):
            entered.set(); release.wait(5)
            events.put(('done', {'output': Path('/tmp/test.pptx'), 'report': Path('/tmp/test.json'), 'result': {}}))
        with TemporaryDirectory() as tmp:
            source = Path(tmp)/'sample.pptx'; source.write_bytes(b'fixture')
            self.app.selected(source)
            with patch('micas_ppt.desktop.run_job', side_effect=fake_worker) as worker:
                try:
                    self.app.begin()
                    self.assertTrue(entered.wait(2))
                    self.assertTrue(self.app.busy)
                    self.app.begin()
                    self.assertEqual(worker.call_count, 1)
                    tick = []; self.root.after(0, lambda: tick.append(True)); self.root.update()
                    self.assertEqual(tick, [True])
                    self.assertEqual(str(self.app.start['state']), 'disabled')
                finally:
                    release.set()

    def test_drop_path_with_spaces(self):
        from types import SimpleNamespace
        with TemporaryDirectory() as tmp:
            source = Path(tmp)/'员工 test.pptx'; source.write_bytes(b'fixture')
            self.app.drop(SimpleNamespace(data=self.root.tk.call('list', str(source))))
            self.assertEqual(self.app.source.get(), str(source.resolve()))
