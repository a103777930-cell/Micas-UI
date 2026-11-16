import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "document_skill.py"
spec = importlib.util.spec_from_file_location("document_skill", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class InspectTests(unittest.TestCase):
    def test_invalid_signature(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.xlsx"
            p.write_text("not a workbook")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                mod.inspect(p)

    def test_valid_minimal_ooxml(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "example.docx"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("[Content_Types].xml", "<Types/>")
                z.writestr("word/document.xml", "<document/>")
            result = mod.inspect(p)
            self.assertEqual(result["type"], "docx")
            self.assertFalse(result["conversion_performed"])

    def test_pdf_signature(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sample.pdf"
            p.write_bytes(b"%PDF-1.7\n")
            self.assertEqual(mod.inspect(p)["type"], "pdf")

if __name__ == "__main__":
    unittest.main()
