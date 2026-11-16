"""Local desktop adapter. Tk widgets are touched only by the main thread."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
from tempfile import TemporaryDirectory
import threading

from .engine import convert


def resource_root():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))


def open_local(path):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f'文件不存在：{path}')
    if sys.platform == 'win32':
        os.startfile(str(path))
    else:
        subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)])


@dataclass(frozen=True)
class Job:
    source: Path
    output_dir: Path

    def validate(self):
        source = self.source.resolve()
        directory = self.output_dir.resolve()
        if source.suffix.lower() != '.pptx' or not source.is_file():
            raise ValueError('请选择存在的 .pptx 文件。')
        if not directory.is_dir():
            raise ValueError('输出目录不存在，请重新选择。')
        return Job(source, directory)


def _publish_new(source, destination):
    """Exclusive creation: never overwrite an existing file, even in a race."""
    created = False
    try:
        with destination.open('xb') as out:
            created = True
            with source.open('rb') as inp:
                import shutil
                shutil.copyfileobj(inp, out)
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise


def run_job(job, events, converter=convert):
    """Worker contract: one terminal event, report available even on rejection."""
    report_path = None
    try:
        job = job.validate()
        events.put(('status', '正在分析并转换；复杂文件可能需要几分钟……'))
        # mkdtemp gives every task its own output directory, avoiding file collisions.
        with TemporaryDirectory(prefix='.micas-', dir=job.output_dir) as temp:
            temp = Path(temp)
            pptx = temp/'converted.pptx'
            report = temp/'report.json'
            failure = None
            try:
                result = converter(job.source, pptx, report, repo_root=resource_root(), allow_risk=False)
            except Exception as exc:
                failure = str(exc)
                if not report.exists():
                    report.write_text(json.dumps({'status': 'failed', 'error': failure}, ensure_ascii=False, indent=2), encoding='utf-8')
            # Claim a unique pair without ever overwriting input or prior conversions.
            for number in range(1, 10001):
                suffix = '' if number == 1 else f'_{number}'
                output = job.output_dir/f'{job.source.stem}_Micas{suffix}.pptx'
                candidate_report = output.with_suffix('.report.json')
                if output.exists() or candidate_report.exists() or output == job.source:
                    continue
                try:
                    _publish_new(report, candidate_report)
                except FileExistsError:
                    continue
                report_path = candidate_report
                break
            else:
                raise ValueError('输出文件名过多，请选择其他目录。')
            if failure:
                events.put(('error', {'message': failure, 'report': report_path}))
                return
            _publish_new(pptx, output)
            events.put(('done', {'output': output, 'report': report_path, 'result': result}))
    except Exception as exc:
        events.put(('error', {'message': str(exc), 'report': report_path}))


class DesktopApp:
    def __init__(self, root):
        import tkinter as tk
        from tkinter import ttk
        self.root = root
        self.busy = False
        self.events = queue.Queue()
        self.output = None
        self.report = None
        root.title('Micas Document Converter')
        root.geometry('760x560')
        root.minsize(650, 500)
        self.source = tk.StringVar()
        self.directory = tk.StringVar()
        self.status = tk.StringVar(value='请选择 PPTX 文件。所有转换均在本机完成。')
        style = ttk.Style(root)
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'))
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Micas Document Converter', style='Title.TLabel').pack(anchor='w')
        ttk.Label(frame, text='本地 PPT 转换 · 官方模板 · 无需上传').pack(anchor='w', pady=(4, 20))
        ttk.Label(frame, text='原始 PPTX').pack(anchor='w')
        row = ttk.Frame(frame); row.pack(fill='x', pady=6)
        self.file_entry = ttk.Entry(row, textvariable=self.source, state='readonly')
        self.file_entry.pack(side='left', fill='x', expand=True)
        self.choose = ttk.Button(row, text='选择文件', command=self.select_file); self.choose.pack(side='left', padx=(10, 0))
        ttk.Label(frame, text='输出目录（默认与原文件相同）').pack(anchor='w', pady=(10, 0))
        row = ttk.Frame(frame); row.pack(fill='x', pady=6)
        ttk.Entry(row, textvariable=self.directory, state='readonly').pack(side='left', fill='x', expand=True)
        self.folder = ttk.Button(row, text='选择目录', command=self.select_folder); self.folder.pack(side='left', padx=(10, 0))
        self.start = ttk.Button(frame, text='开始转换', command=self.begin); self.start.pack(anchor='w', pady=(16, 10))
        self.progress = ttk.Progressbar(frame, mode='indeterminate'); self.progress.pack(fill='x')
        ttk.Label(frame, textvariable=self.status, wraplength=680).pack(anchor='w', pady=10)
        row = ttk.Frame(frame); row.pack(fill='x', pady=8)
        self.open_button = ttk.Button(row, text='打开输出文件', command=lambda: self.open_path(self.output), state='disabled'); self.open_button.pack(side='left')
        self.folder_button = ttk.Button(row, text='打开所在文件夹', command=lambda: self.open_path(self.output.parent if self.output else self.report.parent), state='disabled'); self.folder_button.pack(side='left', padx=8)
        self.report_button = ttk.Button(row, text='查看报告与风险', command=self.show_report, state='disabled'); self.report_button.pack(side='left')
        ttk.Label(frame, wraplength=680, text='V1 提示：不支持的复杂对象将阻止转换。成功生成仍需在 PowerPoint 中复核；已有文件不会被覆盖。').pack(anchor='w', pady=(12, 0))
        if hasattr(self.file_entry, 'drop_target_register'):
            from tkinterdnd2 import DND_FILES
            self.file_entry.drop_target_register(DND_FILES)
            self.file_entry.dnd_bind('<<Drop>>', self.drop)
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.after(100, self.poll)

    def selected(self, path):
        if self.busy:
            return
        path = Path(path)
        if path.suffix.lower() != '.pptx' or not path.is_file():
            self.status.set('请选择存在的 .pptx 文件；不支持 .ppt 或多个文件。')
            return
        self.source.set(str(path.resolve()))
        self.directory.set(str(path.resolve().parent))
        self.status.set(f'已选择：{path.name}')

    def drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if len(files) == 1:
            self.selected(files[0])
        else:
            self.status.set('一次请选择一个 PPTX 文件。')
        return 'copy'

    def select_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[('PowerPoint', '*.pptx')])
        if path:
            self.selected(path)

    def select_folder(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self.directory.get() or None)
        if path:
            self.directory.set(path)

    def begin(self):
        from tkinter import messagebox
        if self.busy:
            return
        try:
            job = Job(Path(self.source.get()), Path(self.directory.get())).validate()
        except Exception as exc:
            messagebox.showerror('无法开始转换', str(exc), parent=self.root)
            return
        self.output = self.report = None
        for button in (self.open_button, self.folder_button, self.report_button):
            button.configure(state='disabled')
        self.busy = True
        for button in (self.start, self.choose, self.folder):
            button.configure(state='disabled')
        self.progress.start(15)
        self.status.set('正在启动转换……')
        threading.Thread(target=run_job, args=(job, self.events), daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == 'status':
                    self.status.set(payload)
                    continue
                self.busy = False
                self.progress.stop()
                for button in (self.start, self.choose, self.folder):
                    button.configure(state='normal')
                self.report = payload.get('report')
                if self.report:
                    self.report_button.configure(state='normal')
                    self.folder_button.configure(state='normal')
                if kind == 'done':
                    self.output = payload['output']
                    self.open_button.configure(state='normal')
                    result = payload['result']
                    n = result.get('integrity', {}).get('output_slides', '?')
                    self.status.set(f'已生成 {n} 页：{self.output.name}。请查看报告，并在 PowerPoint 中检查版式。')
                else:
                    self.status.set('转换未完成：' + self.friendly_error(payload['message']))
                    from tkinter import messagebox
                    messagebox.showerror('转换未完成', self.friendly_error(payload['message']), parent=self.root)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    @staticmethod
    def friendly_error(message):
        if 'Unsupported objects detected' in message:
            return '检测到不支持的对象（如连接线、组合对象、SmartArt、OLE 或动画），已停止转换。请查看报告中的 warnings；原文件未修改。'
        if 'Permission denied' in message or 'Access is denied' in message:
            return '无法写入文件，请选择有写入权限的输出目录并关闭已打开的输出文件。'
        if 'checksum' in message.lower():
            return '内置官方模板校验失败，请重新安装应用。'
        if 'Package not found' in message or 'not a zip file' in message.lower():
            return 'PPTX 无法读取，可能损坏、加密或并非有效的 PPTX 文件。'
        return message

    def open_path(self, path):
        from tkinter import messagebox
        try:
            open_local(path)
        except Exception as exc:
            messagebox.showerror('无法打开', str(exc), parent=self.root)

    def show_report(self):
        import tkinter as tk
        from tkinter import ttk, messagebox
        try:
            data = json.loads(self.report.read_text(encoding='utf-8'))
        except Exception as exc:
            messagebox.showerror('无法读取报告', str(exc), parent=self.root)
            return
        win = tk.Toplevel(self.root); win.title('转换报告与风险'); win.geometry('780x540')
        ttk.Label(win, text='请重点查看 warnings、limitations、integrity 及 slides 中的 checks。', wraplength=740).pack(padx=12, pady=10)
        from tkinter.scrolledtext import ScrolledText
        text = ScrolledText(win, wrap='word', font=('Arial', 11)); text.pack(fill='both', expand=True, padx=12, pady=8)
        text.insert('1.0', json.dumps(data, ensure_ascii=False, indent=2)); text.configure(state='disabled')

    def close(self):
        if self.busy:
            from tkinter import messagebox
            messagebox.showinfo('正在转换', '请等待任务完成后再关闭应用，避免中断文件写入。', parent=self.root)
        else:
            self.root.destroy()


def create_root():
    try:
        from tkinterdnd2 import TkinterDnD
        return TkinterDnD.Tk()
    except (ImportError, RuntimeError):
        import tkinter as tk
        return tk.Tk()


def smoke_test():
    """Run in native CI: create GUI and convert a synthetic deck with bundled resources."""
    from pptx import Presentation
    root = create_root(); root.withdraw()
    app = DesktopApp(root)
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        prs = Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = 'Micas desktop smoke test'
        slide.placeholders[1].text = 'Synthetic editable content'
        prs.save(tmp/'input.pptx')
        events = queue.Queue(); run_job(Job(tmp/'input.pptx', tmp), events)
        last = None
        while not events.empty():
            last = events.get()
        if last[0] != 'done':
            raise RuntimeError(str(last))
        converted = Presentation(last[1]['output'])
        if not any('Synthetic editable content' in sh.text for s in converted.slides for sh in s.shapes if sh.has_text_frame):
            raise RuntimeError('Bundled conversion lost content')
        app.selected(tmp/'input.pptx')
        root.update()
    root.destroy()


def main():
    if '--smoke-test' in sys.argv:
        smoke_test()
        return
    root = create_root()
    DesktopApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
