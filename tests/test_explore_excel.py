"""
Tests for explore-excel skill functions.

Tests preview_data_file() and create_file_summary() functions
with various file formats and edge cases.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
import tempfile
import os

# Import the functions to test
from preview_data_file import preview_data_file
from create_file_summary import create_file_summary


class TestPreviewDataFile:
    """Test cases for preview_data_file function."""

    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        result = preview_data_file("test.txt")
        assert "Error: Unsupported file type" in result
        assert ".txt" in result

    @patch('preview_data_file.pl')
    def test_csv_with_headers_success(self, mock_pl):
        """Test successful CSV reading with headers."""
        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.height = 100
        mock_df.width = 3
        mock_df.columns = ['Name', 'Age', 'City']
        mock_df.__getitem__.return_value.dtype = 'String'
        mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 95
        mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 5
        mock_df.head.return_value = "First 3 rows mock"
        mock_df.tail.return_value = "Last 3 rows mock"
        mock_df.with_row_count.return_value.sample.return_value.sort.return_value.drop.return_value = "Sample mock"
        
        mock_pl.read_csv.return_value = mock_df
        mock_pl.Int8 = 'Int8'
        mock_pl.Int16 = 'Int16'
        mock_pl.Int32 = 'Int32'
        mock_pl.Int64 = 'Int64'
        mock_pl.UInt8 = 'UInt8'
        mock_pl.UInt16 = 'UInt16'
        mock_pl.UInt32 = 'UInt32'
        mock_pl.UInt64 = 'UInt64'
        mock_pl.Float32 = 'Float32'
        mock_pl.Float64 = 'Float64'
        
        with patch('builtins.print') as mock_print:
            result = preview_data_file("test.csv")
        
        # Verify function was called and output contains expected elements
        mock_pl.read_csv.assert_called_once()
        assert "DATA FILE PREVIEW" in result
        assert "CSV (single sheet) - headers detected" in result
        assert "100 rows x 3 columns" in result
        assert "Name" in result
        assert "Age" in result
        assert "City" in result
        mock_print.assert_called_once()

    @patch('preview_data_file.pl')
    def test_csv_without_headers_fallback(self, mock_pl):
        """Test CSV reading fallback when headers can't be detected."""
        # First call fails, second succeeds
        mock_df = MagicMock()
        mock_df.height = 50
        mock_df.width = 2
        mock_df.columns = ['column_0', 'column_1']
        mock_df.__getitem__.return_value.dtype = 'String'
        mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 50
        mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 0
        mock_df.head.return_value = "First 3 rows mock"
        mock_df.tail.return_value = "Last 3 rows mock"
        mock_df.rename.return_value = mock_df
        
        mock_pl.read_csv.side_effect = [Exception("Headers failed"), mock_df]
        mock_pl.Int8 = 'Int8'
        mock_pl.Int16 = 'Int16'
        mock_pl.Int32 = 'Int32'
        mock_pl.Int64 = 'Int64'
        mock_pl.UInt8 = 'UInt8'
        mock_pl.UInt16 = 'UInt16'
        mock_pl.UInt32 = 'UInt32'
        mock_pl.UInt64 = 'UInt64'
        mock_pl.Float32 = 'Float32'
        mock_pl.Float64 = 'Float64'

        with patch('builtins.print'):
            result = preview_data_file("test.csv")
        
        assert "no headers detected" in result
        assert "column_0" in result
        assert "column_1" in result

    @patch('preview_data_file.pl')
    def test_csv_text_only_fallback(self, mock_pl):
        """Test CSV reading with text-only fallback."""
        # First two calls fail, third succeeds
        mock_df = MagicMock()
        mock_df.height = 10
        mock_df.width = 1
        mock_df.columns = ['column_0']
        mock_df.__getitem__.return_value.dtype = 'String'
        mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 10
        mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 0
        mock_df.head.return_value = "First 3 rows mock"
        mock_df.tail.return_value = "Last 3 rows mock"
        mock_df.rename.return_value = mock_df
        
        mock_pl.read_csv.side_effect = [
            Exception("Headers failed"), 
            Exception("No headers failed"), 
            mock_df
        ]
        mock_pl.Utf8 = 'Utf8'
        mock_pl.Int8 = 'Int8'
        mock_pl.Int16 = 'Int16'
        mock_pl.Int32 = 'Int32'
        mock_pl.Int64 = 'Int64'
        mock_pl.UInt8 = 'UInt8'
        mock_pl.UInt16 = 'UInt16'
        mock_pl.UInt32 = 'UInt32'
        mock_pl.UInt64 = 'UInt64'
        mock_pl.Float32 = 'Float32'
        mock_pl.Float64 = 'Float64'

        with patch('builtins.print'):
            result = preview_data_file("test.csv")
        
        assert "text only due to parsing issues" in result

    @patch('preview_data_file.pl')
    def test_excel_with_headers_success(self, mock_pl):
        """Test successful Excel reading with headers."""
        # Mock openpyxl at module level by patching the function directly
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_wb.sheetnames = ['Sheet1', 'Sheet2']
        mock_ws = MagicMock()
        mock_ws.values = [
            ('Name', 'Age', 'City'),  # Headers
            ('John', 25, 'NYC'),
            ('Jane', 30, 'LA')
        ]
        mock_wb.__getitem__.return_value = mock_ws
        mock_openpyxl.load_workbook.return_value = mock_wb
        
        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.height = 2
        mock_df.width = 3
        mock_df.columns = ['Name', 'Age', 'City']
        mock_df.__getitem__.return_value.dtype = 'String'
        mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 2
        mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 0
        mock_df.head.return_value = "First 3 rows mock"
        mock_df.tail.return_value = "Last 3 rows mock"
        
        mock_pl.DataFrame.return_value = mock_df
        mock_pl.Int8 = 'Int8'
        mock_pl.Int16 = 'Int16'
        mock_pl.Int32 = 'Int32'
        mock_pl.Int64 = 'Int64'
        mock_pl.UInt8 = 'UInt8'
        mock_pl.UInt16 = 'UInt16'
        mock_pl.UInt32 = 'UInt32'
        mock_pl.UInt64 = 'UInt64'
        mock_pl.Float32 = 'Float32'
        mock_pl.Float64 = 'Float64'

        # Mock the openpyxl import within the function
        with patch('sys.modules', {'openpyxl': mock_openpyxl}):
            with patch('builtins.print'):
                result = preview_data_file("test.xlsx")
        
        assert "Available sheets (2): Sheet1, Sheet2" in result
        assert "headers detected" in result
        assert "2 rows x 3 columns" in result

    @patch('preview_data_file.pl')
    def test_excel_without_headers(self, mock_pl):
        """Test Excel reading without headers."""
        # Mock openpyxl
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_wb.sheetnames = ['Data']
        mock_ws = MagicMock()
        mock_ws.values = [
            (100, 200, 300),  # Numeric data, not headers
            (150, 250, 350),
            (200, 300, 400)
        ]
        mock_wb.__getitem__.return_value = mock_ws
        mock_openpyxl.load_workbook.return_value = mock_wb
        
        # Mock DataFrame
        mock_df = MagicMock()
        mock_df.height = 3
        mock_df.width = 3
        mock_df.columns = ['column_0', 'column_1', 'column_2']
        mock_df.__getitem__.return_value.dtype = 'Int64'
        mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 3
        mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 0
        mock_df.head.return_value = "First 3 rows mock"
        mock_df.tail.return_value = "Last 3 rows mock"
        
        mock_pl.DataFrame.return_value = mock_df
        mock_pl.Int8 = 'Int8'
        mock_pl.Int16 = 'Int16'
        mock_pl.Int32 = 'Int32'
        mock_pl.Int64 = 'Int64'
        mock_pl.UInt8 = 'UInt8'
        mock_pl.UInt16 = 'UInt16'
        mock_pl.UInt32 = 'UInt32'
        mock_pl.UInt64 = 'UInt64'
        mock_pl.Float32 = 'Float32'
        mock_pl.Float64 = 'Float64'

        # Mock the openpyxl import within the function
        with patch('sys.modules', {'openpyxl': mock_openpyxl}):
            with patch('builtins.print'):
                result = preview_data_file("test.xlsx")
        
        assert "no headers detected" in result
        assert "column_0" in result

    def test_excel_empty_sheet(self):
        """Test Excel reading with empty sheet."""
        # Mock openpyxl
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_wb.sheetnames = ['Empty']
        mock_ws = MagicMock()
        mock_ws.values = []  # Empty sheet
        mock_wb.__getitem__.return_value = mock_ws
        mock_openpyxl.load_workbook.return_value = mock_wb

        # Mock the openpyxl import within the function
        with patch('sys.modules', {'openpyxl': mock_openpyxl}):
            with patch('builtins.print'):
                result = preview_data_file("test.xlsx")
        
        assert "appears to be empty" in result

    def test_excel_sheet_not_found(self):
        """Test Excel reading when requested sheet doesn't exist."""
        # Mock openpyxl
        mock_openpyxl = MagicMock()
        mock_wb = MagicMock()
        mock_wb.sheetnames = ['Sheet1', 'Sheet2']
        mock_ws = MagicMock()
        mock_ws.values = [('A', 'B'), (1, 2)]
        mock_wb.__getitem__.return_value = mock_ws
        mock_openpyxl.load_workbook.return_value = mock_wb

        # Mock DataFrame for successful reading on fallback
        with patch('preview_data_file.pl') as mock_pl:
            mock_df = MagicMock()
            mock_df.height = 1
            mock_df.width = 2
            mock_df.columns = ['A', 'B']
            mock_df.__getitem__.return_value.dtype = 'String'
            mock_df.__getitem__.return_value.is_not_null.return_value.sum.return_value = 1
            mock_df.__getitem__.return_value.is_null.return_value.sum.return_value = 0
            mock_df.head.return_value = "First 3 rows mock"
            mock_df.tail.return_value = "Last 3 rows mock"
            mock_pl.DataFrame.return_value = mock_df
            mock_pl.Int8 = 'Int8'
            mock_pl.Int16 = 'Int16'
            mock_pl.Int32 = 'Int32'
            mock_pl.Int64 = 'Int64'
            mock_pl.UInt8 = 'UInt8'
            mock_pl.UInt16 = 'UInt16'  
            mock_pl.UInt32 = 'UInt32'
            mock_pl.UInt64 = 'UInt64'
            mock_pl.Float32 = 'Float32'
            mock_pl.Float64 = 'Float64'

            # Mock the openpyxl import within the function
            with patch('sys.modules', {'openpyxl': mock_openpyxl}):
                with patch('builtins.print'):
                    result = preview_data_file("test.xlsx", sheet_name="NonExistent")
        
            assert "Warning: Sheet 'NonExistent' not found" in result

    def test_file_read_error(self):
        """Test handling of file read errors."""
        with patch('builtins.print'):
            result = preview_data_file("nonexistent.csv")
        
        assert "Error reading file" in result


class TestCreateFileSummary:
    """Test cases for create_file_summary function."""

    @patch('create_file_summary.datetime')
    def test_create_file_summary_success(self, mock_datetime):
        """Test successful file summary creation."""
        # Mock datetime
        mock_datetime.now.return_value.strftime.return_value = "2026-02-13 10:30:00"
        
        file_name = "test_data.xlsx"
        summary_content = "Excel file with 3 sheets containing loss triangles for reserve analysis."
        
        with patch('builtins.print') as mock_print:
            result = create_file_summary(file_name, summary_content)
        
        # Check that content is formatted correctly
        assert "# FILE SUMMARY" in result
        assert file_name in result
        assert "2026-02-13 10:30:00" in result
        assert summary_content in result
        assert "TeamAnalyst" in result
        
        # Check that it was printed
        mock_print.assert_called_once_with(result)

    @patch('create_file_summary.datetime')
    def test_create_file_summary_with_special_characters(self, mock_datetime):
        """Test file summary with special characters in content."""
        mock_datetime.now.return_value.strftime.return_value = "2026-02-13 15:45:30"
        
        file_name = "data & analysis.csv"
        summary_content = "File contains data with special chars: #, $, %, & more!"
        
        with patch('builtins.print') as mock_print:
            result = create_file_summary(file_name, summary_content)
        
        assert file_name in result
        assert summary_content in result
        mock_print.assert_called_once()

    @patch('create_file_summary.datetime')  
    def test_create_file_summary_empty_content(self, mock_datetime):
        """Test file summary with empty summary content."""
        mock_datetime.now.return_value.strftime.return_value = "2026-02-13 20:00:00"
        
        file_name = "empty.csv"
        summary_content = ""
        
        with patch('builtins.print') as mock_print:
            result = create_file_summary(file_name, summary_content)
        
        assert file_name in result
        assert "## Summary" in result  # Section header should still be there
        mock_print.assert_called_once()


# Integration test to ensure both functions work together
class TestIntegration:
    """Integration tests for explore-excel functions."""

    def test_functions_can_be_imported(self):
        """Test that both functions can be imported successfully."""
        # This test verifies the import path and basic function availability
        assert callable(preview_data_file)
        assert callable(create_file_summary)
        
        # Test function signatures
        import inspect
        preview_sig = inspect.signature(preview_data_file)
        assert 'file_path' in preview_sig.parameters
        assert 'sheet_name' in preview_sig.parameters
        assert 'sample_size' in preview_sig.parameters
        
        summary_sig = inspect.signature(create_file_summary)
        assert 'file_name' in summary_sig.parameters
        assert 'summary_content' in summary_sig.parameters


if __name__ == "__main__":
    pytest.main([__file__])