"""
Tests for file operations tools
"""

import pytest
from pathlib import Path

from mcp_local.tools.file_operations import (
    ListFilesTool, ReadFileTool, WriteFileTool, GetFileLinesTool, GetFileInfoTool
)


class TestListFilesTool:
    """Tests for ListFilesTool"""
    
    def test_list_files_basic(self, temp_dir):
        """Test basic file listing"""
        # Create some test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()
        
        tool = ListFilesTool()
        result = tool.execute(directory=str(temp_dir), show_hidden=False)
        
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result
        assert "📁" in result  # Directory icon
        assert "📄" in result  # File icon
    
    def test_list_files_with_hidden(self, temp_dir):
        """Test listing files including hidden ones"""
        # Create hidden file
        (temp_dir / ".hidden").write_text("hidden content")
        (temp_dir / "visible.txt").write_text("visible content")
        
        tool = ListFilesTool()
        
        # Without hidden files
        result_no_hidden = tool.execute(directory=str(temp_dir), show_hidden=False)
        assert ".hidden" not in result_no_hidden
        assert "visible.txt" in result_no_hidden
        
        # With hidden files
        result_with_hidden = tool.execute(directory=str(temp_dir), show_hidden=True)
        assert ".hidden" in result_with_hidden
        assert "visible.txt" in result_with_hidden


class TestReadFileTool:
    """Tests for ReadFileTool"""
    
    def test_read_file_basic(self, sample_file):
        """Test basic file reading"""
        tool = ReadFileTool()
        result = tool.execute(file_path=str(sample_file))
        
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 5" in result
        assert str(sample_file) in result
    
    def test_read_nonexistent_file(self, temp_dir):
        """Test reading non-existent file"""
        tool = ReadFileTool()
        result = tool.execute(file_path=str(temp_dir / "nonexistent.txt"))
        
        assert "Error" in result or "does not exist" in result


class TestWriteFileTool:
    """Tests for WriteFileTool"""
    
    def test_write_file_basic(self, temp_dir, reset_services):
        """Test basic file writing"""
        file_path = temp_dir / "new_file.txt"
        content = "Hello, World!"
        
        tool = WriteFileTool()
        result = tool.execute(file_path=str(file_path), content=content)
        
        assert "Successfully wrote" in result
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_write_file_overwrite(self, sample_file, reset_services):
        """Test overwriting existing file"""
        new_content = "New content"
        
        tool = WriteFileTool()
        result = tool.execute(file_path=str(sample_file), content=new_content)
        
        assert "Successfully wrote" in result
        assert sample_file.read_text() == new_content


class TestGetFileLinesTool:
    """Tests for GetFileLinesTool"""
    
    def test_get_lines_basic(self, sample_file):
        """Test getting specific lines"""
        tool = GetFileLinesTool()
        result = tool.execute(file_path=str(sample_file), start_line=2, end_line=4)
        
        assert "Line 2" in result
        assert "Line 3" in result
        assert "Line 4" in result
        assert "Line 1" not in result
        assert "Line 5" not in result
    
    def test_get_lines_single(self, sample_file):
        """Test getting single line"""
        tool = GetFileLinesTool()
        result = tool.execute(file_path=str(sample_file), start_line=3)
        
        assert "Line 3" in result
        assert "   3:" in result  # Line number formatting
    
    def test_get_lines_invalid_range(self, sample_file):
        """Test invalid line range"""
        tool = GetFileLinesTool()
        result = tool.execute(file_path=str(sample_file), start_line=100)
        
        assert "exceeds file length" in result


class TestGetFileInfoTool:
    """Tests for GetFileInfoTool"""
    
    def test_get_file_info_basic(self, sample_file):
        """Test getting file information"""
        tool = GetFileInfoTool()
        result = tool.execute(file_path=str(sample_file))
        
        assert "Name:" in result
        assert "Size:" in result
        assert "Type:" in result
        assert "Modified:" in result
        assert sample_file.name in result
    
    def test_get_file_info_directory(self, temp_dir):
        """Test getting directory information"""
        tool = GetFileInfoTool()
        result = tool.execute(file_path=str(temp_dir))
        
        assert "Type: Directory" in result
        assert "Name:" in result
