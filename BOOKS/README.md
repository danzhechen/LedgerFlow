# BOOKS — 人工账本文件夹

将历年人工账本 Excel 文件放在本目录，文件名**必须与下列完全一致**（含空格）：

```
2020Veritas China Account book.xlsx
2021Veritas China Account book.xlsx
2022Veritas China Account book.xlsx
2024Veritas China Account book.xlsx
```

放好后运行季度对比脚本：

```bash
# macOS / Linux（在 veritas-accounting/ 目录下）
source .venv/bin/activate
python3 scripts/compare_quarterly.py

# Windows
.venv\Scripts\activate
python scripts\compare_quarterly.py
```

> 注意：本文件夹中的 Excel 文件**不纳入版本控制**（已在 .gitignore 中排除），仅在本地使用。
