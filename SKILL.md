---
name: micas-document-template
description: Detect DOCX, PPTX, XLSX and PDF uploads, select approved Micas templates from the existing catalog, and safely standardize formatting without losing content.
---
# Micas Document Template Skill

## Trigger
Use when a user uploads a Word, PowerPoint, Excel, or PDF file and asks to apply Micas company formatting.

## Mandatory workflow
1. Identify the file using extension **and** actual file signature / OOXML package structure. Reject mismatches, macro-enabled documents, encrypted or malformed archives.
2. Run `python scripts/document_skill.py inspect INPUT` to inspect content and obtain eligible templates from `templates/catalog.json`.
3. Select an appropriate template only when its file family, purpose and approved status are clear. `active` means registered, **not** business-approved: verify the template's README and tags. Ask when purpose is ambiguous. Never silently use a placeholder template.
4. Preserve source content, embedded images, tables, charts, equations, notes, hyperlinks and spreadsheet formulas. Do not silently flatten or delete objects. Treat macros and external links as untrusted.
5. For a conversion, use a format-aware document tool; never overwrite the source or original template. If a safe converter is not available, stop after inspection and explain that conversion has not occurred.
6. Validate source vs output: text counts and object inventory, spreadsheet formulas and sheet names, slide count and notes, document sections and media. Render and visually inspect when possible.
7. Deliver the editable output and a report listing changes, unsupported features and any discrepancies. PDF may be generated as an additional deliverable; PDF inputs require a separate extraction/reconstruction workflow.

## CLI
```bash
python scripts/document_skill.py inspect input.xlsx
python scripts/document_skill.py inspect input.docx --json
python scripts/document_skill.py inspect input.pptx --json
```

The initial CLI is an **inspection and matching tool**, not a converter. Never claim that it has applied a template.

## Catalog
Use only `templates/catalog.json` as the source of truth. Do not rename, re-save or mutate versioned templates. A new template version requires a new catalog entry and SHA-256 verification.

## Privacy
The repository is public. Never commit customer data, confidential documents, generated outputs or credentials.
