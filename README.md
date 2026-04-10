# Veritas 自动记账（LedgerFlow）

本项目面向会计/财务团队的 **Excel 原生**工作流：读取人工流水日记账（journal），应用映射规则（rules），输出每年一份 `ledger_output.xlsx`（含季度汇总、明细、审计与复核）。

> 中文为第一语言；英文文档（如有）用于补充开发者信息。

## 快速开始（会计/非开发者推荐）

### 一次性安装（仅首次）

```bash
cd veritas-accounting
bash setup_venv.sh
```

### 每次跑数（一条命令）

```bash
bash scripts/run_for_accounting.sh
```

#### 输入/输出约定

- **默认输入**：
  - `examples/journal_entry_2020_2024.xlsx`
  - `账目分类明细.xlsx`
- **默认输出**：`output/<年份>/ledger_output.xlsx`
- **会自动处理哪些 sheet**：
  - 如果 Excel 里存在 `2020` / `2021` / `2022` / `2023` 这种“年份命名”的 sheet，会 **只处理这些年份 sheet（按年份顺序）**
  - 如果没有年份命名的 sheet，则处理全部 sheet

#### 通用化输入文件名（不再强依赖 journal_entry_2020_2024.xlsx）

你可以通过环境变量覆盖输入/输出路径（适合把真实账本放在 `input/` 目录）：\n

```bash
export VERITAS_JOURNAL_FILE="input/journal.xlsx"
export VERITAS_RULES_FILE="input/账目分类明细.xlsx"
export VERITAS_OUTPUT_DIR="output"
bash scripts/run_for_accounting.sh
```

Windows 同理（设置环境变量后运行 `scripts\\run_for_accounting.bat`）。

## 常见问题（关键行为说明）

- **2023 数据跑到 2022 里**：现在会被阻止。\n
  - 当你处理名为 `2022` 的 sheet 时，如果某些行的日期解析为 2023：\n
    - `strict` 模式：直接报错并停止（强制修正源数据）\n
    - `lenient` 模式：会丢弃这些行并给出警告（默认一键脚本使用 lenient）
- **journal 的 type（类型）缺失**：不会再静默默认成 `OL`。\n
  - 缺失时会标记为 `__MISSING_TYPE__` 并在复核输出中明确提示需要人工分类/补规则。
- **余利宝内部划转误入投资收益**：已做保护。\n
  - 描述包含“余利宝-基金赎回，转账到支付宝 / 余利宝自动转入”会被记为 **银行存款 DR + 银行存款 CR（净额 0）**。

## 进阶用法（开发者/CLI）

### 安装（开发者推荐）

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 处理单个 sheet（例如只跑 2022）

```bash
veritas-accounting process \
  --input examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --sheet 2022 \
  --output ./output/2022_only
```

## 文档入口（中文优先）

- **运行说明（给会计）**：`docs/如何运行-how-to-run.md`
- **规则核对/已知数据问题**：`docs/accounting-verification.md`
- **维护“踩坑记录”**：`progress.md`

## 项目结构（高频文件）

```
veritas-accounting/
├── 账目分类明细.xlsx                 # 规则/科目/借贷方向（主要来源）
├── examples/                         # 示例输入
├── scripts/
│   ├── run_for_accounting.sh         # 一键运行（Mac/Linux）
│   ├── run_for_accounting.bat        # 一键运行（Windows）
│   ├── process_multi_sheet.py        # 多 sheet 处理器（每个 sheet 独立输出）
│   └── compare_quarterly.py          # 与人工账本季度对比（BOOKS/）
├── docs/                             # 文档（中文优先）
├── BOOKS/                            # 人工账本（用于对比；支持常见下载文件名变体）
├── output/                           # 生成的报表（不入库）
└── src/veritas_accounting/           # Python 包源码
```

## 许可证

MIT
