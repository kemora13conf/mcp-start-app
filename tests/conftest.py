"""
Test configuration and fixtures for MCP Local tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from mcp_local.services import file_service, backup_service, history_service


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample text file for testing"""
    file_path = temp_dir / "sample.txt"
    content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def cleanup_services():
    """Clean up services after tests"""
    yield
    # Clear history after tests
    history_service.clear_history()


@pytest.fixture
def reset_services():
    """Reset all services to clean state"""
    history_service.clear_history()
    backup_service.initialize()
    file_service.initialize()
    yield
    history_service.clear_history()
