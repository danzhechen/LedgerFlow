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

### 输入/输出约定

| 项目 | 说明 |
|------|------|
| **默认日记账** | `examples/journal_entry_2020_2024.xlsx` |
| **默认规则/科目表** | `账目分类明细.xlsx`（与 `--rules` / `--account-hierarchy` 常用同一文件） |
| **默认输出** | `output/<年份>/ledger_output.xlsx`（每个处理的 sheet 对应一个子目录） |

**会自动处理哪些 sheet？**

- 若工作簿里存在名为 `2020`、`2021`、`2022`、`2023`、`2024` 等 **四位数字年份** 的 sheet，则 **只处理这些 sheet**，并按年份升序执行。
- 若 **没有任何**「年份命名」的 sheet，则 **处理全部 sheet**（保持原有顺序）。

**通用化输入（不必固定 `journal_entry_2020_2024.xlsx` 文件名）**

将真实账本放在例如 `input/` 下，通过环境变量覆盖路径即可：

**macOS / Linux**

```bash
export VERITAS_JOURNAL_FILE="input/journal.xlsx"
export VERITAS_RULES_FILE="input/账目分类明细.xlsx"
export VERITAS_OUTPUT_DIR="output"
bash scripts/run_for_accounting.sh
```

**Windows**

在「系统环境变量」或当前会话中设置 `VERITAS_JOURNAL_FILE`、`VERITAS_RULES_FILE`、`VERITAS_OUTPUT_DIR` 后，运行：

```bat
scripts\run_for_accounting.bat
```

一键脚本默认使用 **`--validation-level lenient`**（与多表处理脚本一致）；需要严格校验时可改用 CLI 并指定 `strict`。

---

## 常见问题（关键行为说明）

### 年份与 sheet 不一致（例如 2023 年分录出现在「2022」sheet）

- 处理 **名为某年** 的 sheet（如 `2022`）时，会校验分录 **日期所属年份** 是否与 sheet 名一致。
- **strict**：发现不一致即 **报错并停止**，请修正源表后再跑。
- **lenient**（一键脚本默认）：**丢弃**年份不符的行并 **警告**，避免污染该年报表。

### 日记账「类型 / Type」列缺失

- 不再静默默认成 `OL`；会标为 **`__MISSING_TYPE__`**，在 **`ledger_output.xlsx`** 的审查相关区域（如 **Flagged Entries** / Audit & Review）中提示需 **人工补类型或补规则**。
- 若规则条件里含有 `"关键词" in description` 形式，工具会尝试 **关键词启发式推断**（高置信度可自动填入类型，低置信度仅在备注中给出建议，供核对）。

### 「余利宝-基金赎回…」「余利宝自动转入」误记投资收益

- 上述描述视为 **资产内部划转**，记为 **银行存款 DR + 银行存款 CR**（借贷等额，净额对投资收益无影响），避免误入投资收益。

---

## 进阶用法（开发者 / CLI）

### 安装（可编辑模式）

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 只处理某一个 sheet（例如仅 2022）

```bash
veritas-accounting process \
  --input examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --sheet 2022 \
  --output ./output/2022_only
```

多 sheet 批量仍推荐使用 `scripts/process_multi_sheet.py`（与一键脚本相同的核心逻辑：年份 sheet 自动筛选等）。

---

## 文档入口（中文优先）

| 文档 | 用途 |
|------|------|
| [docs/如何运行-how-to-run.md](docs/如何运行-how-to-run.md) | 安装、目录约定、常见问题（给会计） |
| [docs/accounting-verification.md](docs/accounting-verification.md) | 规则核对、已知数据问题 |
| `progress.md` | 维护用「踩坑与变更记录」（若存在；默认可能被 `.gitignore` 忽略，仅本地） |

---

## 项目结构（高频路径）

```
veritas-accounting/
├── 账目分类明细.xlsx              # 规则 / 科目 / 借贷方向（主要配置来源）
├── examples/                      # 示例日记账等
├── scripts/
│   ├── run_for_accounting.sh      # 一键运行（macOS / Linux）
│   ├── run_for_accounting.bat     # 一键运行（Windows）
│   ├── process_multi_sheet.py     # 多 sheet：按策略选表、逐年输出
│   └── compare_quarterly.py       # 与人工账本季度对比（读取 BOOKS/）
├── docs/                          # 说明文档（中文优先）
├── BOOKS/                         # 人工参考账本（对比用；支持常见下载文件名变体）
├── output/                        # 生成结果（默认不入库）
└── src/veritas_accounting/        # Python 包源码
```

---

## 许可证

MIT
