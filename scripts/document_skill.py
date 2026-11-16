#!/usr/bin/env python3
"""Read-only document inspection and template candidate discovery. Python stdlib only."""
import argparse
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TYPES = {
    ".docx": ("documents", "word/", "word/document.xml"),
    ".pptx": ("presentations", "ppt/", "ppt/presentation.xml"),
    ".xlsx": ("spreadsheets", "xl/", "xl/workbook.xml"),
}
PDF = ".pdf"
MAX_SIZE = 100 * 1024 * 1024
MAX_ENTRIES = 10000

def inspect(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError("Input file does not exist")
    if path.stat().st_size > MAX_SIZE:
        raise ValueError("File exceeds 100 MiB safety limit")
    suffix = path.suffix.lower()
    if suffix == PDF:
        with path.open("rb") as f:
            if not f.read(8).startswith(b"%PDF-"):
                raise ValueError("Extension/signature mismatch: expected PDF")
        family, kind = "pdf", "pdf"
    elif suffix in TYPES:
        family, prefix, required = TYPES[suffix]
        if not zipfile.is_zipfile(path):
            raise ValueError("Extension/signature mismatch: expected OOXML ZIP")
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if len(names) > MAX_ENTRIES or any(n.startswith("/") or ".." in n.split("/") for n in names):
                raise ValueError("Unsafe archive structure")
            if any(i.flag_bits & 1 for i in z.infolist()):
                raise ValueError("Encrypted archive entries are unsupported")
            if required not in names or "[Content_Types].xml" not in names:
                raise ValueError("OOXML structure does not match file extension")
            if any("vbaProject.bin" in n for n in names):
                raise ValueError("Macro-bearing OOXML is unsupported")
            if any(i.file_size > MAX_SIZE for i in z.infolist()) or sum(i.file_size for i in z.infolist()) > 5 * MAX_SIZE:
                raise ValueError("Archive exceeds decompression safety limit")
        kind = suffix.lstrip(".")
    else:
        raise ValueError("Unsupported file type; expected DOCX, PPTX, XLSX or PDF")

    catalog = json.loads((ROOT / "templates/catalog.json").read_text(encoding="utf-8"))
    matches = [
        {"id": t["id"], "name": t["name"], "version": t["version"],
         "path": t["path"], "tags": t.get("tags", []), "status": t["status"]}
        for t in catalog["templates"]
        if t["category"] == family and t["status"] == "active"
    ]
    return {"input": str(path), "type": kind, "category": family,
            "candidate_templates": matches, "conversion_performed": False,
            "warning": "Inspection only. Candidate templates are not automatically approved for the document's purpose."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inspect"])
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect(args.file)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
