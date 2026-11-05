# Micas 文档模板库

集中保存 Micas 未来使用的文档模板、正式样例及使用规范。模板按文件类型分类，再按用途与版本组织；业务分类通过登记清单的标签扩展。

## 快速使用

1. 在 [模板目录](templates/README.md) 选择模板，并阅读对应说明。
2. 下载该版本的原文件，复制到自己的工作目录后填写；不要直接修改仓库中的正式样例。
3. 完成的业务文档保存在业务项目中，本仓库只收录模板与不含敏感信息的样例。

首个正式样例：[Excel Template(3).xlsx](templates/spreadsheets/excel-template/v1.0.0/Excel%20Template%283%29.xlsx)。这是用户提供的原始附件，逐字节保留，不重存、不转换。具体业务用途与填写字段尚待补充，使用前请阅读 [样例说明](templates/spreadsheets/excel-template/README.md)。

## 仓库结构

```text
templates/
  catalog.json                 # 唯一机器可读登记清单
  spreadsheets/               # Excel / 表格模板
    excel-template/
      README.md
      v1.0.0/Excel Template(3).xlsx
  documents/                  # Word / 文字文档模板（预留）
  presentations/              # PowerPoint / 演示模板（预留）
docs/template-standard.md     # 命名、分类、版本与使用规范
CONTRIBUTING.md                # 新样例收录与变更流程
scripts/validate_templates.py # 无第三方依赖的登记与完整性检查
.github/workflows/validate-templates.yml
CHANGELOG.md
```

## 维护与扩展

- 新增样例遵循 [贡献流程](CONTRIBUTING.md) 和 [模板规范](docs/template-standard.md)。
- 每个正式版本拥有独立目录；修改模板时新增版本，保留历史文件。
- [登记清单](templates/catalog.json) 保存稳定 ID、版本、路径、来源、状态与 SHA-256。新增条目时同步更新可读目录。
- 本地运行 `python3 scripts/validate_templates.py`；GitHub 提交与拉取请求会自动执行相同检查。
- 文件的收录不代表已完成业务、品牌、打印或 Excel 兼容性验收。现有样例的适用范围见各自说明。

## 权利与发布

仓库当前未声明统一许可证；保留原文件中的版权与归属信息。公开发布或对外复用前，由维护者确认相应权利与数据披露范围。
