@echo off
REM ============================================================
REM Veritas 自动记账 — 一键生成报表（Windows）
REM 用法：在 veritas-accounting\ 目录下双击或在命令提示符中运行
REM   scripts\run_for_accounting.bat
REM ============================================================

echo.
echo ======================================================
echo   Veritas 自动记账 -- 生成 2020/2021/2022/2024 报表
echo ======================================================
echo.

REM ── Locate project root (parent of scripts\) ────────────
cd /d "%~dp0.."

REM ── Activate virtual environment ────────────────────────
IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [OK] 虚拟环境已激活
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] 虚拟环境已激活
) ELSE (
    echo [警告] 未找到虚拟环境 (.venv\ 或 venv\)
    echo        请先运行以下命令安装环境：
    echo          python -m venv .venv
    echo          .venv\Scripts\activate
    echo          pip install pandas openpyxl pydantic pydantic-settings rule-engine click pyyaml
    echo          pip install -e .
    echo        详见 docs\如何运行-how-to-run.md
    pause
    exit /b 1
)

echo.
echo 正在生成报表，请稍候（约 1-2 分钟）...
echo.

python scripts\process_multi_sheet.py ^
    -i examples\journal_entry_2020_2024.xlsx ^
    -r 账目分类明细.xlsx ^
    -a 账目分类明细.xlsx ^
    -o output ^
    -s 2020 -s 2021 -s 2022 -s 2024 ^
    --validation-level lenient

echo.
echo ======================================================
echo   报表生成完成！
echo ======================================================
echo.
echo   请打开以下文件查看结果：
echo     output\2020\ledger_output.xlsx
echo     output\2021\ledger_output.xlsx
echo     output\2022\ledger_output.xlsx
echo     output\2024\ledger_output.xlsx
echo.
echo   每个文件中的「Quarterly Report」工作表
echo   可与人工账本季度数字对照。
echo.
pause
