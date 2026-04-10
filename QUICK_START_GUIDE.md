# veritas-accounting 快速入门 / Quick Start Guide

## 这是什么？/ What is veritas-accounting?

**veritas-accounting** 自动将日记账分录通过映射规则转换成分类账，专为 Excel 工作流设计。

**veritas-accounting** automates the transformation of journal entries into ledger entries using mapping rules. It's designed for Excel-native workflows.

### 解决的问题 / The Problem It Solves

无需手动处理 691+ 条日记账分录，工具将：
- ✅ 从 Excel 读取日记账分录
- ✅ 自动应用所有映射规则
- ✅ 生成按账户层级分类的分类账
- ✅ 自动检测并标记问题条目（类型缺失、年份错误、无规则匹配等）
- ✅ 生成统一的审查报告（`ledger_output.xlsx`）

---

## Quick Usage (3 Steps)

### Step 1: Prepare Your Files

You need **two Excel files**:

1. **Journal Entries** (`journal.xlsx`) - Your input data
2. **Mapping Rules** (`rules.xlsx`) - Rules that map entries to accounts

### Step 2: Run the Command

```bash
veritas-accounting process \
  --input journal.xlsx \
  --rules rules.xlsx \
  --output ./output
```

### Step 3: Review Output Files

Check the `./output` directory for:
- `ledger_output.xlsx` — 统一报告（分类账 + 季度汇总 + 审查标记 + 审计轨迹）

所有输出合并在一个工作簿中，包含多个工作表（Ledger Output、Account Summary、Quarterly Report、Flagged Entries 等）。

---

## Sample Input Data

### Journal Entries (`journal.xlsx`)

| entry_id | year | description | old_type | amount | date | quarter | notes |
|----------|------|-------------|----------|--------|------|---------|-------|
| JE-001 | 2024 | Payment received from customer | OL | 1000 | 2024-01-15 | 1 | Q1 payment |
| JE-002 | 2024 | Expense payment for services | CR | 500 | 2024-02-20 | 1 | |
| JE-003 | 2024 | Large payment received | OL | 5000 | 2024-03-10 | 1 | Large transaction |
| JE-004 | 2024 | Quarterly expense | DR | 750 | 2024-03-31 | 1 | Q1 expense |
| JE-005 | 2024 | Regular payment | OL | 250 | 2024-04-05 | 2 | |

**Required Columns:**
- `entry_id` - Unique identifier
- `year` - Year (2000-2100)
- `description` - Transaction description
- `old_type` - Original account type (OL, CR, DR, etc.)
- `amount` - Transaction amount (decimal)
- `date` - Transaction date

**Optional Columns:**
- `quarter` - Quarter number (1-4)
- `notes` - Additional notes

### Mapping Rules (`rules.xlsx`)

| rule_id | condition | account_code | priority | old_type | description | generates_multiple |
|---------|-----------|--------------|----------|----------|-------------|-------------------|
| R-001 | old_type == "OL" | A1 | 10 | OL | Map OL entries to A1 | False |
| R-002 | old_type == "CR" | B2 | 10 | CR | Map CR entries to B2 | False |
| R-003 | old_type == "OL" and amount > 1000 | A1-1 | 15 | OL | Map large OL entries (>1000) to A1-1 | False |
| R-004 | old_type == "DR" | C3 | 10 | DR | Map DR entries to C3 | False |
| R-005 | old_type == "OL" and year == 2024 | A1 | 12 | OL | Map 2024 OL entries to A1 | False |

**How Rules Work:**
- **condition** - Rule-engine expression (e.g., `old_type == "OL" and amount > 1000`)
- **account_code** - Target account code for matching entries
- **priority** - Higher priority rules are evaluated first
- **generates_multiple** - If True, one journal entry can create multiple ledger entries

**Rule Evaluation:**
- Rules are evaluated in priority order (higher priority first)
- First matching rule is applied
- Conditions use rule-engine syntax (supports AND, OR, comparisons, etc.)

---

## Sample Output Results

### Ledger Output (`ledger_output.xlsx`)

After processing, your journal entries are transformed into ledger entries:

| entry_id | account_code | account_path | level | description | amount | date | quarter | year | source_entry_id | rule_applied |
|----------|--------------|--------------|-------|-------------|--------|------|---------|------|-----------------|--------------|
| LE-001 | A1 | Level1/Account1 | 1 | Payment received from customer | 1000 | 2024-01-15 | 1 | 2024 | JE-001 | R-001 |
| LE-002 | B2 | Level1/Account2 | 1 | Expense payment for services | 500 | 2024-02-20 | 1 | 2024 | JE-002 | R-002 |
| LE-003 | A1-1 | Level1/Account1/Level2/Account1-1 | 2 | Large payment received | 5000 | 2024-03-10 | 1 | 2024 | JE-003 | R-003 |
| LE-004 | C3 | Level1/Account3 | 1 | Quarterly expense | 750 | 2024-03-31 | 1 | 2024 | JE-004 | R-004 |
| LE-005 | A1 | Level1/Account1 | 1 | Regular payment | 250 | 2024-04-05 | 2 | 2024 | JE-005 | R-001 |

**Key Features:**
- Each ledger entry links back to source journal entry (`source_entry_id`)
- Shows which rule was applied (`rule_applied`)
- Organized by account hierarchy (`account_path`, `level`)
- Preserves all original data (description, amount, date, etc.)

### 统一报告 (`ledger_output.xlsx`) 中的工作表

| 工作表 | 内容 |
|--------|------|
| Ledger Output | 所有分类账分录，含账户代码和来源 |
| Account Summary | 按账户层级汇总金额 |
| Quarterly Report | 按季度汇总 |
| Flagged Entries | 需审查的条目（NO_MATCH、MISSING_TYPE、年份错误等） |
| Audit Trail | 完整审计轨迹（处理时间、规则应用记录） |

---

## Example Workflow

### Scenario: Process Q1 2024 Journal Entries

```bash
# 1. 先验证输入文件（推荐）
veritas-accounting validate \
  --input journal_entries_q1.xlsx \
  --rules mapping_rules.xlsx

# 2. 处理分录
veritas-accounting process \
  --input journal_entries_q1.xlsx \
  --rules mapping_rules.xlsx \
  --output ./output/q1_2024

# 3. 审查结果
# 打开 ./output/q1_2024/ledger_output.xlsx
# 查看 "Flagged Entries" 工作表了解需人工处理的条目
```

### What You'll See During Processing

```
📖 Reading journal entries...
   ✓ Read 691 journal entries
📋 Reading mapping rules...
   ✓ Loaded 194 mapping rules
✅ Validating input data...
   ✓ Input validation passed
🔄 Applying mapping rules and transforming entries...
   ✓ Generated 1250 ledger entries
📊 Generating report...
   ✓ Generated report: ./output/ledger_output.xlsx

✅ Processing complete!
📁 Output files saved to: ./output
```

---

## Common Use Cases

### 1. Process Monthly Journal Entries

```bash
veritas-accounting process \
  --input january_2024.xlsx \
  --rules rules.xlsx \
  --output ./output/january
```

### 2. Validate Before Processing

```bash
# Check for errors first
veritas-accounting validate \
  --input journal.xlsx \
  --rules rules.xlsx

# If validation passes, process
veritas-accounting process \
  --input journal.xlsx \
  --rules rules.xlsx
```

### 3. Use Configuration File

Create `config.yaml`:
```yaml
input:
  journal_file: "journal.xlsx"
  rules_file: "rules.xlsx"
  account_hierarchy_file: "accounts.xlsx"

output:
  directory: "./output"
  
validation:
  level: "strict"
  auto_fix: true
```

Then run:
```bash
veritas-accounting process --config config.yaml
```

### 4. Enable Auto-Fix for Common Errors

```bash
veritas-accounting process \
  --input journal.xlsx \
  --rules rules.xlsx \
  --auto-fix
```

---

## Understanding the Transformation

### Before (Journal Entry)
```
JE-001: Payment received from customer, OL, $1000, 2024-01-15
```

### After (Ledger Entry)
```
LE-001: Account A1, Payment received from customer, $1000, 2024-01-15
        Source: JE-001, Rule: R-001
```

**What Happened:**
1. System read journal entry JE-001
2. Evaluated mapping rules in priority order
3. Rule R-001 matched: `old_type == "OL"` → account_code A1
4. Created ledger entry LE-001 with account A1
5. Linked back to source (JE-001) and rule (R-001)

---

## Key Features

### ✅ Excel-Native
- Work with familiar Excel files
- No database setup required
- Easy to edit and review

### ✅ Complete Transparency
- Every transformation is tracked
- Full audit trail
- Before/after comparisons

### ✅ Comprehensive Validation
- Input validation before processing
- Error detection and reporting
- Auto-fix suggestions

### ✅ Hierarchical Organization
- Account hierarchy support
- Multi-level organization
- Quarterly aggregation

### ✅ Rule-Based Transformation
- 194 mapping rules supported
- Complex conditions (AND, OR, comparisons)
- Priority-based evaluation
- One-to-many mapping support

---

## Next Steps

1. **Try the Examples:**
   ```bash
   cd examples/
   # Review the sample files
   # Then process them:
   veritas-accounting process \
     --input journal_entries_sample.xlsx \
     --rules mapping_rules_sample.xlsx \
     --output ./test_output
   ```

2. **Read Full Documentation:**
   - [Getting Started Guide](./docs/getting-started.md) - Detailed installation and setup
   - [User Manual](./docs/user-manual.md) - Complete feature reference
   - [Configuration Guide](./docs/configuration.md) - Advanced configuration options
   - [Rule Management Guide](./docs/rule-management.md) - How to create and edit rules

3. **Customize for Your Needs:**
   - Update mapping rules in Excel
   - Configure account hierarchy
   - Set up configuration file
   - Customize validation settings

---

## Getting Help

- **CLI Help:** `veritas-accounting --help` or `veritas-accounting process --help`
- **审查报告 / Review Report:** 打开 `ledger_output.xlsx`，查看 "Flagged Entries" 工作表
- **Documentation:** See `docs/` folder for complete guides
- **Examples:** Check `examples/` folder for sample files

---

## Quick Reference

```bash
# Process entries
veritas-accounting process --input journal.xlsx --rules rules.xlsx

# Validate only
veritas-accounting validate --input journal.xlsx --rules rules.xlsx

# Use config file
veritas-accounting process --config config.yaml

# Enable auto-fix
veritas-accounting process --input journal.xlsx --rules rules.xlsx --auto-fix

# Verbose logging
veritas-accounting process --input journal.xlsx --rules rules.xlsx --verbose
```

---

**Ready to get started?** Check out the [Getting Started Guide](./docs/getting-started.md) for detailed installation instructions!









