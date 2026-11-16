#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ "$(uname -s)" == Darwin ]] || { echo 'Build on macOS.' >&2; exit 1; }
python3 -m pip install -e '.[desktop,build]'
python3 -m PyInstaller --noconfirm --clean packaging/micas-desktop.spec
ditto -c -k --sequesterRsrc --keepParent dist/MicasDocumentConverter.app dist/MicasDocumentConverter-macOS.zip
