#!/usr/bin/env python3
"""Validate the template catalog and preserved files using only Python's stdlib."""

import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {"spreadsheets", "documents", "presentations"}
REQUIRED = {
    "id", "name", "category", "tags", "version", "status", "path", "readme",
    "original_filename", "source", "added_on", "size_bytes", "sha256",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def safe_file(value):
    check(isinstance(value, str) and value, "路径必须是非空字符串")
    path = PurePosixPath(value)
    check(not path.is_absolute() and ".." not in path.parts and "\\" not in value,
          f"不安全路径：{value}")
    resolved = (ROOT / path).resolve()
    check(ROOT in resolved.parents and resolved.is_file(), f"文件不存在或越界：{value}")
    return resolved


def validate():
    catalog = json.loads((ROOT / "templates/catalog.json").read_text(encoding="utf-8"))
    check(catalog.get("schema_version") == 1, "不支持的 schema_version")
    entries = catalog.get("templates")
    check(isinstance(entries, list) and entries, "templates 必须是非空列表")
    seen_keys, seen_paths = set(), set()
    id_locations = {}
    for entry in entries:
        check(isinstance(entry, dict) and REQUIRED <= entry.keys(), "模板缺少必填字段")
        for field in REQUIRED - {"tags", "size_bytes"}:
            check(isinstance(entry[field], str) and entry[field].strip(), f"{field} 必须是非空字符串")
        label = f"{entry['id']}@{entry['version']}"
        check(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]), f"{label}: ID 格式错误")
        check(re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", entry["version"]),
              f"{label}: 版本格式错误")
        check(entry["category"] in CATEGORIES, f"{label}: 未知分类")
        check(entry["status"] in {"draft", "active", "deprecated"}, f"{label}: 未知状态")
        check(isinstance(entry["tags"], list) and all(isinstance(t, str) and t.strip() for t in entry["tags"]),
              f"{label}: tags 格式错误")
        check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry["added_on"]), f"{label}: 日期格式错误")
        datetime.date.fromisoformat(entry["added_on"])
        check(type(entry["size_bytes"]) is int and entry["size_bytes"] > 0, f"{label}: 大小错误")
        check(re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]), f"{label}: SHA-256 格式错误")
        key = (entry["id"], entry["version"])
        check(key not in seen_keys and entry["path"] not in seen_paths, f"{label}: 重复登记")
        seen_keys.add(key)
        seen_paths.add(entry["path"])
        path = PurePosixPath(entry["path"])
        check(len(path.parts) == 5 and path.parts[0] == "templates"
              and path.parts[1] == entry["category"]
              and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.parts[2])
              and path.parts[3] == "v" + entry["version"]
              and path.name == entry["original_filename"], f"{label}: 目录或文件名不符合规范")
        location = str(path.parent.parent)
        check(id_locations.setdefault(entry["id"], location) == location, f"{label}: 同一 ID 的目录不一致")
        check(entry["readme"] == str(path.parent.parent / "README.md"), f"{label}: README 位置错误")
        safe_file(entry["readme"])
        source = safe_file(entry["path"])
        data = source.read_bytes()
        check(len(data) == entry["size_bytes"], f"{label}: 文件大小不匹配")
        check(hashlib.sha256(data).hexdigest() == entry["sha256"], f"{label}: 文件校验不匹配")
        if source.suffix.lower() == ".xlsx":
            with zipfile.ZipFile(source) as archive:
                check(archive.testzip() is None, f"{label}: XLSX 包损坏")
                check({"[Content_Types].xml", "xl/workbook.xml"} <= set(archive.namelist()),
                      f"{label}: 缺少 XLSX 结构")
        print(f"OK {label}: {entry['path']}")
    # Every file in a version directory must be explicitly registered.
    actual = {p.relative_to(ROOT).as_posix() for category in CATEGORIES
              for p in (ROOT / "templates" / category).glob("*/v*/*") if p.is_file()}
    check(actual == seen_paths, f"版本目录与登记清单不一致：{sorted(actual ^ seen_paths)}")
    print(f"Validated {len(entries)} template version(s).")


if __name__ == "__main__":
    try:
        validate()
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
