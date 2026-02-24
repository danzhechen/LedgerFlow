#!/bin/bash
# ============================================================
# Veritas 自动记账 — 一键生成报表
# 用法：在 veritas-accounting/ 目录下运行
#   bash scripts/run_for_accounting.sh
# ============================================================

set -e

# Resolve the project root (directory containing this script's parent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$BASE"

echo ""
echo "======================================================"
echo "  Veritas 自动记账 — 生成 2020/2021/2022/2024 报表"
echo "======================================================"
echo ""

# ── Activate virtual environment ──────────────────────────
VENV_ACTIVATE=""
if [ -f ".venv/bin/activate" ]; then
    VENV_ACTIVATE=".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    VENV_ACTIVATE="venv/bin/activate"
fi

if [ -n "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    echo "✓ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境（.venv/ 或 venv/）"
    echo "   请先运行：bash setup_venv.sh"
    echo "   详见 docs/如何运行-how-to-run.md"
    exit 1
fi

# ── Run pipeline ──────────────────────────────────────────
JOURNAL="examples/journal_entry_2020_2024.xlsx"
RULES="账目分类明细.xlsx"

echo ""
echo "输入文件：$JOURNAL"
echo "规则文件：$RULES"
echo ""

python3 scripts/process_multi_sheet.py \
    -i "$JOURNAL" \
    -r "$RULES" \
    -a "$RULES" \
    -o output \
    -s 2020 -s 2021 -s 2022 -s 2024 \
    --validation-level lenient

echo ""
echo "======================================================"
echo "  报表生成完成！"
echo "======================================================"
echo ""
echo "  请打开以下文件查看结果："
echo "    output/2020/ledger_output.xlsx"
echo "    output/2021/ledger_output.xlsx"
echo "    output/2022/ledger_output.xlsx"
echo "    output/2024/ledger_output.xlsx"
echo ""
echo "  每个文件中的「Quarterly Report」工作表"
echo "  可与人工账本季度数字对照。"
echo ""
