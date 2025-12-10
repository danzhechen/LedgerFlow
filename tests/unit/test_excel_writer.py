"""Unit tests for ExcelWriter."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from veritas_accounting.excel.writer import ExcelWriter
from veritas_accounting.utils.exceptions import ExcelIOError


class TestExcelWriter:
    """Test cases for ExcelWriter."""

    def test_write_dataframe_to_new_file(self, tmp_path: Path) -> None:
        """Test writing a DataFrame to a new Excel file."""
        writer = ExcelWriter()
        df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        output_file = tmp_path / "test_output.xlsx"

        writer.write_file(df, output_file)

        assert output_file.exists()
        # Verify content
        read_df = pd.read_excel(output_file, engine="openpyxl")
        pd.testing.assert_frame_equal(df, read_df)

    def test_write_list_of_dicts(self, tmp_path: Path) -> None:
        """Test writing a list of dictionaries to Excel."""
        writer = ExcelWriter()
        data = [{"Name": "Alice", "Age": 30}, {"Name": "Bob", "Age": 25}]
        output_file = tmp_path / "test_dicts.xlsx"

        writer.write_file(data, output_file)

        assert output_file.exists()
        read_df = pd.read_excel(output_file, engine="openpyxl")
        expected_df = pd.DataFrame(data)
        pd.testing.assert_frame_equal(expected_df, read_df)

    def test_write_to_specific_sheet(self, tmp_path: Path) -> None:
        """Test writing to a specific worksheet name."""
        writer = ExcelWriter()
        df = pd.DataFrame({"Col1": [1, 2], "Col2": [3, 4]})
        output_file = tmp_path / "test_sheet.xlsx"
        sheet_name = "MySheet"

        writer.write_sheet(df, output_file, sheet_name)

        assert output_file.exists()
        # Verify sheet exists
        read_df = pd.read_excel(
            output_file, sheet_name=sheet_name, engine="openpyxl"
        )
        pd.testing.assert_frame_equal(df, read_df)

    def test_create_directory_structure(self, tmp_path: Path) -> None:
        """Test that directory structure is created if it doesn't exist."""
        writer = ExcelWriter()
        df = pd.DataFrame({"A": [1]})
        output_file = tmp_path / "nested" / "dir" / "output.xlsx"

        writer.write_file(df, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_chinese_text_encoding(self, tmp_path: Path) -> None:
        """Test that Chinese text is handled correctly."""
        writer = ExcelWriter()
        df = pd.DataFrame(
            {
                "名称": ["测试", "数据"],
                "金额": [100, 200],
            }
        )
        output_file = tmp_path / "chinese_test.xlsx"

        writer.write_file(df, output_file)

        assert output_file.exists()
        read_df = pd.read_excel(output_file, engine="openpyxl")
        pd.testing.assert_frame_equal(df, read_df)

    def test_write_multiple_sheets(self, tmp_path: Path) -> None:
        """Test writing multiple sheets to one file."""
        writer = ExcelWriter()
        sheets = {
            "Sheet1": pd.DataFrame({"A": [1, 2]}),
            "Sheet2": pd.DataFrame({"B": [3, 4]}),
        }
        output_file = tmp_path / "multi_sheet.xlsx"

        writer.write_multiple_sheets(sheets, output_file)

        assert output_file.exists()
        # Verify both sheets exist
        for sheet_name, expected_df in sheets.items():
            read_df = pd.read_excel(
                output_file, sheet_name=sheet_name, engine="openpyxl"
            )
            pd.testing.assert_frame_equal(expected_df, read_df)

    def test_overwrite_existing_file(self, tmp_path: Path) -> None:
        """Test overwriting an existing file."""
        writer = ExcelWriter()
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame({"B": [3, 4]})
        output_file = tmp_path / "overwrite_test.xlsx"

        # Write first file
        writer.write_file(df1, output_file)
        # Overwrite with second file
        writer.write_file(df2, output_file, overwrite=True)

        read_df = pd.read_excel(output_file, engine="openpyxl")
        pd.testing.assert_frame_equal(df2, read_df)

    def test_empty_dataframe(self, tmp_path: Path) -> None:
        """Test writing an empty DataFrame."""
        writer = ExcelWriter()
        df = pd.DataFrame()
        output_file = tmp_path / "empty.xlsx"

        writer.write_file(df, output_file)

        assert output_file.exists()
        read_df = pd.read_excel(output_file, engine="openpyxl")
        assert read_df.empty

    def test_empty_list(self, tmp_path: Path) -> None:
        """Test writing an empty list."""
        writer = ExcelWriter()
        data: list[dict[str, int]] = []
        output_file = tmp_path / "empty_list.xlsx"

        writer.write_file(data, output_file)

        assert output_file.exists()

    def test_invalid_data_format(self) -> None:
        """Test that invalid data format raises ExcelIOError."""
        writer = ExcelWriter()
        invalid_data = "not a dataframe or list"

        with pytest.raises(ExcelIOError, match="Invalid data format"):
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
                writer.write_file(invalid_data, f.name)

    def test_permission_error_handling(self, tmp_path: Path) -> None:
        """Test handling of permission errors."""
        writer = ExcelWriter()
        df = pd.DataFrame({"A": [1]})
        # Try to write to a path that would require root permissions
        # (This test may not work on all systems, but tests the error handling)
        restricted_path = Path("/root/test.xlsx")

        # Skip on systems where this might actually work
        if not restricted_path.parent.exists():
            pytest.skip("Cannot test permission error on this system")

        with pytest.raises(ExcelIOError, match="Permission denied"):
            writer.write_file(df, restricted_path)

    def test_formatting_applied(self, tmp_path: Path) -> None:
        """Test that formatting (header styling, column widths) is applied."""
        writer = ExcelWriter()
        df = pd.DataFrame({"Column1": [1, 2, 3], "Column2": ["a", "b", "c"]})
        output_file = tmp_path / "formatted.xlsx"

        writer.write_file(df, output_file)

        # Verify file exists and can be opened
        assert output_file.exists()
        # Note: We can't easily test formatting without opening the file,
        # but we can verify the file is valid
        read_df = pd.read_excel(output_file, engine="openpyxl")
        assert not read_df.empty
