# Example Files

本目录提供 **演示用** 输入格式说明；仓库内默认可运行的合成日记账为 **`journal_entry_sample.xlsx`**（不含真实财务数据）。

## Files

### journal_entry_sample.xlsx

- **生成方式**：`python3 scripts/generate_examples.py`  
- **内容**：2020–2024 五个年份 sheet，虚构 `entry_id`（如 `A-1-101`、`I-1-22`、`B-2-7`、`W-1-18`）、金额与摘要；包含演示用「跳过入账」描述及缺失类型行等边界情况。  
- **用途**：熟悉列结构与一键脚本；**正式账务请使用自己的账本文件**（可通过 `VERITAS_JOURNAL_FILE` 指定）。

### mapping_rules_sample.xlsx（若存在）

映射规则列示例：`rule_id`, `condition`, `account_code`, `priority` 等。

### account_hierarchy_sample.xlsx（若存在）

科目层级示例。

### ledger_output_sample.xlsx（若存在）

处理后输出样式参考。

## Usage

1. 复制或对照示例维护列名与数据类型。  
2. 运行校验：`veritas-accounting validate --input your_journal.xlsx --rules your_rules.xlsx`  
3. 处理：`bash scripts/run_for_accounting.sh`（或设置环境变量指向你的文件）。

## Documentation

- [工作手册-accountant-guide.md](../docs/工作手册-accountant-guide.md)  
- [Getting Started](../docs/getting-started.md)  
- [Rule Management](../docs/rule-management.md)
