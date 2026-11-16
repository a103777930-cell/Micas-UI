# Micas 文档模板 Skill — V1

## 设计
沿用 `templates/catalog.json`，不建立第二套 registry。保留原始模板文件、版本目录及 SHA-256 校验规则。

## 当前可用
- `SKILL.md`：AI 调用流程与保真、安全规则。
- `scripts/document_skill.py inspect <file>`：基于文件头和 OOXML 包结构识别 DOCX、PPTX、XLSX、PDF；查询同类型 active 模板候选。
- 文件识别仅产生候选，不会自动套用样式。
- `scripts/validate_templates.py`：继续校验模板登记及文件完整性。

## 尚未实现
- Word 样式与节、页眉页脚的转换
- PowerPoint 母版、占位符、页面重排
- Excel 样式映射、公式及图表保真转换
- PDF 内容提取、重建、导出与视觉回归

## 模板选择
目前唯一登记的 Excel 样例含 `purpose-pending` 标签，不能默认作为所有 Excel 文件的正式公司样式。必须先确认业务用途和样式规范。

## 安全
仓库是公开的。不要提交内部客户文件、生成物、密钥或含敏感内容的公司模板。转换应在隔离工作目录中进行，永不覆盖输入和版本化模板。
