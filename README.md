# Veritas 自动记账

基于 Veritas 2020–2024 年流水日记账，自动生成分类总账和季度报表。

## 快速开始

### 1. 安装环境（仅首次）

```bash
cd veritas-accounting
bash setup_venv.sh
```

### 2. 生成报表

```bash
bash scripts/run_for_accounting.sh
```

报表输出到 `output/2020/`、`output/2021/`、`output/2022/`、`output/2024/`，每个目录下的 `ledger_output.xlsx` 包含季度汇总和明细。

### 3. 查看规则与未匹配条目

- **规则核对**：`docs/accounting-verification.md` — 已用规则、未匹配类型、数据问题
- **运行说明**：`docs/如何运行-how-to-run.md` — 详细安装、命令、常见问题

## 项目结构

```
veritas-accounting/
├── 账目分类明细.xlsx           # 规则文件（科目与借贷方向）
├── examples/
│   └── journal_entry_2020_2024.xlsx   # 流水日记账（输入）
├── output/                    # 程序生成的报表（运行后生成）
├── BOOKS/                     # 放人工账本文件（用于季度对比）
├── docs/
│   ├── accounting-verification.md    # 规则核对说明（发给会计）
│   └── 如何运行-how-to-run.md        # 运行指南
├── scripts/
│   ├── run_for_accounting.sh         # 一键运行（Mac/Linux）
│   └── run_for_accounting.bat        # 一键运行（Windows）
└── src/                       # 程序源码
```

## 依赖

- Python 3.11+
- pandas, openpyxl, pydantic, rule-engine, click, pyyaml

详见 `pyproject.toml`。安装：`pip install -e .`

## 提交到 GitHub

首次推送或更新后，在项目根目录执行：

```bash
git add .
git status   # 确认 账目分类明细.xlsx、docs/、scripts/ 等已纳入
git commit -m "Veritas accounting handoff: rules, docs, run scripts"
git push origin main
```

> `output/`、`.venv/`、`BOOKS/*.xlsx` 已通过 .gitignore 排除，不会提交。

## 许可证

MIT
