# 财务工作手册 — 从 Raw Data 到 LedgerFlow 报表

面向会计人员：**如何把流水整理好、跑一次脚本、处理报错条目、更新规则后再跑出最终结果**。中文版优先。

---

## 一、准备工作（需要什么文件）

| 文件 | 说明 |
|------|------|
| **日记账 Excel** | 含 `entry_id`, `description`, `old_type`(类型), `amount`, `date` 等列；可按年份分 sheet（如 `2022`、`2023`）。演示仓库自带 **`examples/journal_entry_sample.xlsx`**（合成数据）；真实账本请自行保管或用环境变量指向路径（勿提交敏感账本）。 |
| **账目分类明细.xlsx** | 内含 **`journal_to_ledger`**（映射规则）、科目层级、`journal` 类型映射等 — **规则的唯一权威来源**。 |

可选：**BOOKS/** 下放人工参考账本，用于运行 `scripts/compare_quarterly.py` 做季度核对。

---

## 二、安装与运行（最短路径）

1. 首次：`bash setup_venv.sh`（Windows 见 `docs/如何运行-how-to-run.md`）。
2. 每次：`bash scripts/run_for_accounting.sh`  
   - 默认读取 `examples/journal_entry_sample.xlsx` + `账目分类明细.xlsx`，输出到 `output/<年份>/ledger_output.xlsx`。  
   - 真实路径：`VERITAS_JOURNAL_FILE`、`VERITAS_RULES_FILE`、`VERITAS_OUTPUT_DIR`（详见 README）。

---

## 三、读懂输出：`ledger_output.xlsx`

| 工作表 | 用途 |
|--------|------|
| **Journal Entry Categorization** | 每条生成的借贷明细；按 **日期 → 季度 → 流水号前缀（A→I→B→其它）** 排序，便于按原始流水顺序核对。 |
| **Account Summary (by Year)** | 按年的科目 CR/DR/净额 — **与人工年报小结对照的主表**。 |
| **Quarterly Report** | 按季度汇总。 |
| **Audit & Review** | 摘要及 **无匹配规则（NO_MATCH）** 的日记账列表。 |

终端若出现 `⚠️ X entries had no matching rules`，表示仍有日记账类型或条件未被规则覆盖。

---

## 四、无法匹配条目 — 标准处理流程（workflow）

1. **定位**：打开对应年份的 `ledger_output.xlsx` → **Audit & Review** 中的「Unmatched journal entries」列表；或对照终端提示的数量。  
2. **归类**：确认这些行的 **`old_type`（类型）** 与 **摘要** 业务含义（必要时与项目组沟通）。  
3. **改规则**：在 **`账目分类明细.xlsx` → `journal_to_ledger`**（或与团队约定的工作表）中 **新增一行规则**：  
   - 满足「同一 `(年份, 类型)` 互斥」惯例（详见 `docs/accounting-verification.md`）。  
   - `condition` 中常包含 `old_type == "…"` 以及摘要关键字 `"…" in description`。  
4. **重跑**：保存 Excel 后重新执行 `bash scripts/run_for_accounting.sh`（或 CLI / `process_multi_sheet.py`）。  
5. **复核**：NO_MATCH 数量应减少；仍有残留则重复 2–4。

---

## 五、类型缺失（MISSING_TYPE）

若日记账 **类型列为空**，程序会标为 **`__MISSING_TYPE__`**，需在源表中补全类型或增加可推断规则（参见 README「关键词启发式」）。**不要依赖静默默认类型**，以免误匹配。

---

## 六、每年都会出现但难归类的条目

例如：**银行商务卡结算**、**服务器（管理费）**、某年仅出现一两次的新摘要。

建议流程：

1. 先尝试归入最接近的现有 **`old_type`**，并在摘要中加一致关键字，便于规则里的 `description` 条件命中。  
2. 若会计确认需 **新类型**：在 `journal` / 类型映射表中增加该类型 → 映射到规则用的 `old_type`，再在 `journal_to_ledger` 增加对应借贷规则。  
3. 将「第一年遇到的特例」记在团队核对文档（如 `accounting-verification.md`）供次年沿用。

---

## 七、内部划转与不入账说明

- 描述中含 **`余利宝-基金赎回`** 或 **`余利宝自动转入`**：**不入账**（不产生报表行）。  
- **金额为 0** 的行：**不入账**。  
- 其它内部划转（基金申购/赎回、支付宝余额划转等）仍按 **`账目分类明细`** 中约定处理。

---

## 八、季度对比（可选）

将人工账本放入 **BOOKS/**（文件名支持常见下载变体），运行：

```bash
python3 scripts/compare_quarterly.py
```

具体列映射与 2022 特例列见脚本及 `docs/yearly-validation.md`。

---

## 九、演示数据再生（开发者）

合成示例账本可由脚本生成：

```bash
python3 scripts/generate_examples.py
```

将重写 **`examples/journal_entry_sample.xlsx`**。

---

## 十、延伸阅读

- [如何运行-how-to-run.md](./如何运行-how-to-run.md) — 逐步安装与命令  
- [accounting-verification.md](./accounting-verification.md) — 规则核对与历史待办  
- [architecture.md](./architecture.md) — 模块关系图（技术）
