# 如何运行 Veritas 自动记账程序

本文档面向会计部门的 IT 负责人或需要自己跑数的会计老师。  
**目标**：一键生成各年度总账报表（`output/<年份>/ledger_output.xlsx`）。

---

## 一、前提条件

| 需要 | 说明 |
|------|------|
| Python 3.11 或更高版本 | [https://www.python.org/downloads/](https://www.python.org/downloads/) — 安装时勾选"Add to PATH" |
| 终端/命令提示符 | macOS/Linux：系统自带终端；Windows：命令提示符（cmd）或 PowerShell |
| 本项目文件夹 | 将整个 `veritas-accounting` 文件夹放到本地任意路径（例如桌面） |

确认 Python 已安装：

```bash
python3 --version   # macOS / Linux
python --version    # Windows
```

---

## 二、一次性安装（仅首次运行需要）

打开终端，`cd` 进入 `veritas-accounting` 文件夹，然后运行安装脚本：

**macOS / Linux：**

```bash
cd veritas-accounting
bash setup_venv.sh
```

**Windows（命令提示符）：**

```bat
cd veritas-accounting
python -m venv .venv
.venv\Scripts\activate
pip install pandas openpyxl pydantic pydantic-settings rule-engine click pyyaml
pip install -e .
```

安装完成后会出现 `✅ Setup complete!`（macOS/Linux）或 `Successfully installed ...`（Windows）。

---

## 三、每次跑数：一条命令

### macOS / Linux

```bash
cd veritas-accounting
bash scripts/run_for_accounting.sh
```

### Windows

```bat
cd veritas-accounting
scripts\run_for_accounting.bat
```

脚本运行约需 1–2 分钟。成功后终端最后会显示：

```
======================================================
  报表生成完成！
======================================================

  请打开以下文件查看结果：
    output/2020/ledger_output.xlsx
    output/2021/ledger_output.xlsx
    output/2022/ledger_output.xlsx
    output/2024/ledger_output.xlsx
```

> 运行中出现 `⚠️ X entries had no matching rules` 或 `Duplicate entry ID` 属于已知情况，不影响其他年份报表的生成。详见 `docs/accounting-verification.md` 第二节和第三节。

### 3.1 输入文件名不再强依赖（推荐做法：使用 input/ 目录）

默认脚本会读取：

- `examples/journal_entry_2020_2024.xlsx`
- `账目分类明细.xlsx`

如果你要跑真实账本，推荐在项目根目录新建 `input/` 文件夹（自行创建即可），把文件放进去，然后设置环境变量覆盖默认路径：

**macOS / Linux：**

```bash
export VERITAS_JOURNAL_FILE="input/journal.xlsx"
export VERITAS_RULES_FILE="input/账目分类明细.xlsx"
export VERITAS_OUTPUT_DIR="output"
bash scripts/run_for_accounting.sh
```

**Windows（cmd）：**

```bat
set VERITAS_JOURNAL_FILE=input\journal.xlsx
set VERITAS_RULES_FILE=input\账目分类明细.xlsx
set VERITAS_OUTPUT_DIR=output
scripts\run_for_accounting.bat
```

### 3.2 会自动处理哪些 sheet（避免漏跑 2023）

- 如果 Excel 里存在 `2020` / `2021` / `2022` / `2023` 这种“年份命名”的 sheet，会 **只处理这些年份 sheet（按年份顺序）**。\n
- 如果没有年份命名的 sheet，则处理全部 sheet。

---

## 四、如何查看报表

打开 `output/<年份>/ledger_output.xlsx`，其中包含以下工作表：

| 工作表 | 内容 |
|--------|------|
| **Quarterly Report** | 季度汇总（各科目按 Q1/Q2/Q3/Q4 列示） |
| **Account Summary** | 全年科目汇总（借贷方向、净额） |
| **Ledger** | 完整明细记录（每条流水对应的会计分录） |
| **Audit & Review** | 无法自动分类的条目列表（含类型、摘要、金额） |

> **最常用的是 Quarterly Report** — 与人工账本对照时，用这个工作表比较各季度数字。

---

## 五、如何放人工账本文件（用于季度对比）

如果需要运行**程序报表 vs 人工账本**的对比，请将历年人工账本 Excel 放入项目根目录下的 `BOOKS/` 文件夹。\n
文件名现在支持常见下载变体（例如 `(... (1).xlsx)`），但仍建议使用下面的标准命名，便于沟通：

```
veritas-accounting/
└── BOOKS/
    ├── 2020Veritas China Account book.xlsx
    ├── 2021Veritas China Account book.xlsx
    ├── 2022Veritas China Account book.xlsx
    └── 2024Veritas China Account book.xlsx
```

文件放好后，在终端运行：

```bash
# macOS / Linux
source .venv/bin/activate
python3 scripts/compare_quarterly.py

# Windows
.venv\Scripts\activate
python scripts\compare_quarterly.py
```

对比结果会直接打印到终端，每个年份、每个季度列示：程序净额 vs 人工账本数字、差额。

---

## 六、常见问题

| 问题 | 解决方法 |
|------|----------|
| `python3: command not found` | Python 未安装或未加入 PATH，重新安装并勾选"Add to PATH" |
| `ModuleNotFoundError: No module named 'pandas'` | 虚拟环境未激活，先运行 `source .venv/bin/activate`（Mac）或 `.venv\Scripts\activate`（Windows） |
| 某个年份报 `⚠️ X entries had no matching rules` | 正常现象；这些条目已列入 `docs/accounting-verification.md` 第二节待会计确认 |
| 2022 报 `Duplicate entry ID` | 已知数据问题（I-2-1 / I-2-2），见 `docs/accounting-verification.md` 第三节；不影响其他年份运行 |
| `BOOKS/` 中的文件找不到 | 检查文件名是否与第五节要求完全一致（包括空格和括号） |
| `BOOKS/` 中的文件找不到（新版本） | 仍建议按标准命名；若出现下载后的 `(1)` 等后缀，程序会尝试自动识别 |

---

## 七、文件说明

```
veritas-accounting/
├── 账目分类明细.xlsx           ← 规则文件（科目与借贷方向），由项目方维护
├── examples/
│   └── journal_entry_2020_2024.xlsx  ← 流水日记账（输入）
├── output/
│   ├── 2020/ledger_output.xlsx       ← 程序生成的 2020 总账报表
│   ├── 2021/ledger_output.xlsx       ← 2021
│   ├── 2022/ledger_output.xlsx       ← 2022
│   └── 2024/ledger_output.xlsx       ← 2024
├── BOOKS/                            ← 放人工账本文件（见第五节）
├── docs/
│   ├── accounting-verification.md    ← 规则核对说明（发给会计老师的主文档）
│   └── 如何运行-how-to-run.md        ← 本文件
└── scripts/
    ├── run_for_accounting.sh         ← 一键运行脚本（Mac/Linux）
    └── run_for_accounting.bat        ← 一键运行脚本（Windows）
```

---

*如有疑问请联系项目方。*
