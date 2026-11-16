# Build on the target OS. Only explicitly allowlisted resources enter the bundle.
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

root = Path(SPECPATH).parent
resources = root / 'templates'
template_dir = resources / 'presentations' / 'micas-official-ppt'
data, binaries, hiddenimports = collect_all('tkinterdnd2')
data += [
    (str(resources / 'catalog.json'), 'templates'),
    (str(template_dir / 'layout-mapping.md'), 'templates/presentations/micas-official-ppt'),
    (str(template_dir / 'v1.0.0' / 'PPT_Template_2026.pptx'), 'templates/presentations/micas-official-ppt/v1.0.0'),
]
a = Analysis([str(root / 'packaging' / 'desktop_entry.py')], pathex=[str(root)],
             binaries=binaries, datas=data, hiddenimports=hiddenimports,
             hookspath=[], runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
          name='MicasDocumentConverter', debug=False, strip=False, upx=False,
          console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='MicasDocumentConverter')
if sys.platform == 'darwin':
    app = BUNDLE(coll, name='MicasDocumentConverter.app', icon=None,
                 bundle_identifier='com.micas.documentconverter',
                 info_plist={'CFBundleShortVersionString': '0.1.0',
                             'NSHighResolutionCapable': True})
