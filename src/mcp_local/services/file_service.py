"""
File service for managing file operations
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from ..core import ServiceBase, MAX_FILE_SIZE
from ..core.exceptions import FileNotFoundError, FileSizeError, FileAccessError
from ..core.utils import format_file_size, validate_path


class FileService(ServiceBase):
    """Service for file operations and management"""
    
    def __init__(self):
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize file service"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass
    
    def read_file(self, file_path: str, max_size: Optional[int] = None) -> str:
        """Read contents of a text file"""
        try:
            path = validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File '{file_path}' does not exist")
            
            # Check file size
            file_size = path.stat().st_size
            size_limit = max_size or MAX_FILE_SIZE
            
            if file_size > size_limit:
                raise FileSizeError(f"File too large ({format_file_size(file_size)}). "
                                  f"Limit: {format_file_size(size_limit)}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except (FileNotFoundError, FileSizeError):
            raise
        except PermissionError:
            raise FileAccessError(f"Permission denied accessing '{file_path}'")
        except UnicodeDecodeError:
            raise FileAccessError(f"Cannot decode file '{file_path}' as text")
        except Exception as e:
            raise FileAccessError(f"Error reading file '{file_path}': {e}")
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> bool:
        """Write content to a file"""
        try:
            path = validate_path(file_path)
            
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except PermissionError:
            raise FileAccessError(f"Permission denied writing to '{file_path}'")
        except Exception as e:
            raise FileAccessError(f"Error writing file '{file_path}': {e}")
    
    def get_file_info(self, file_path: str) -> dict:
        """Get detailed information about a file"""
        try:
            path = validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File '{file_path}' does not exist")
            
            stat = path.stat()
            
            return {
                "path": str(path),
                "name": path.name,
                "size": stat.st_size,
                "size_formatted": format_file_size(stat.st_size),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "is_symlink": path.is_symlink(),
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:],
                "extension": path.suffix,
                "parent": str(path.parent)
            }
            
        except FileNotFoundError:
            raise
        except Exception as e:
            raise FileAccessError(f"Error getting file info for '{file_path}': {e}")
    
    def list_directory(self, directory: str, show_hidden: bool = False, 
                      include_size: bool = True) -> List[dict]:
        """List contents of a directory"""
        try:
            path = validate_path(directory)
            
            if not path.exists():
                raise FileNotFoundError(f"Directory '{directory}' does not exist")
            
            if not path.is_dir():
                raise FileAccessError(f"'{directory}' is not a directory")
            
            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                try:
                    stat = item.stat()
                    item_info = {
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "modified_time": stat.st_mtime
                    }
                    
                    if include_size and item.is_file():
                        item_info["size"] = stat.st_size
                        item_info["size_formatted"] = format_file_size(stat.st_size)
                    
                    items.append(item_info)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
            
            # Sort: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            
            return items
            
        except (FileNotFoundError, FileAccessError):
            raise
        except Exception as e:
            raise FileAccessError(f"Error listing directory '{directory}': {e}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            path = validate_path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File '{file_path}' does not exist")
            
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()  # Only empty directories
            else:
                raise FileAccessError(f"Cannot delete '{file_path}': unsupported file type")
            
            return True
            
        except FileNotFoundError:
            raise
        except PermissionError:
            raise FileAccessError(f"Permission denied deleting '{file_path}'")
        except OSError as e:
            if "Directory not empty" in str(e):
                raise FileAccessError(f"Cannot delete non-empty directory '{file_path}'")
            raise FileAccessError(f"Error deleting '{file_path}': {e}")
        except Exception as e:
            raise FileAccessError(f"Error deleting '{file_path}': {e}")
    
    def copy_file(self, src_path: str, dst_path: str) -> bool:
        """Copy a file"""
        try:
            import shutil
            
            src = validate_path(src_path)
            dst = validate_path(dst_path)
            
            if not src.exists():
                raise FileNotFoundError(f"Source file '{src_path}' does not exist")
            
            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dst)
            return True
            
        except FileNotFoundError:
            raise
        except PermissionError:
            raise FileAccessError(f"Permission denied copying '{src_path}' to '{dst_path}'")
        except Exception as e:
            raise FileAccessError(f"Error copying file: {e}")
    
    def move_file(self, src_path: str, dst_path: str) -> bool:
        """Move/rename a file"""
        try:
            import shutil
            
            src = validate_path(src_path)
            dst = validate_path(dst_path)
            
            if not src.exists():
                raise FileNotFoundError(f"Source file '{src_path}' does not exist")
            
            # Create destination directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(src, dst)
            return True
            
        except FileNotFoundError:
            raise
        except PermissionError:
            raise FileAccessError(f"Permission denied moving '{src_path}' to '{dst_path}'")
        except Exception as e:
            raise FileAccessError(f"Error moving file: {e}")


# Global file service instance
file_service = FileService()
