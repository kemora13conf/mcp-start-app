"""
Backup service for managing file backups
"""

import datetime
import shutil
from pathlib import Path
from typing import Optional

from ..core import ServiceBase, BACKUP_DIR
from ..core.exceptions import BackupError


class BackupService(ServiceBase):
    """Service for creating and managing file backups"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize backup service"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
        except Exception as e:
            raise BackupError(f"Failed to initialize backup directory: {e}")
    
    def cleanup(self) -> None:
        """Cleanup old backups if needed"""
        # Could implement backup retention policy here
        pass
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the file before editing"""
        try:
            path = Path(file_path).expanduser().resolve()
            if not path.exists():
                return ""
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path.name}_{timestamp}.backup"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(path, backup_path)
            return str(backup_path)
        except Exception as e:
            raise BackupError(f"Failed to create backup: {e}")
    
    def list_backups(self, file_name: Optional[str] = None) -> list:
        """List available backups"""
        try:
            if file_name:
                pattern = f"{file_name}_*.backup"
                backups = list(self.backup_dir.glob(pattern))
            else:
                backups = list(self.backup_dir.glob("*.backup"))
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return [str(backup) for backup in backups]
        except Exception as e:
            raise BackupError(f"Failed to list backups: {e}")
    
    def get_latest_backup(self, file_name: str) -> Optional[str]:
        """Get the most recent backup for a file"""
        try:
            backups = self.list_backups(file_name)
            return backups[0] if backups else None
        except Exception as e:
            raise BackupError(f"Failed to get latest backup: {e}")
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """Restore a backup to target location"""
        try:
            backup = Path(backup_path)
            target = Path(target_path)
            
            if not backup.exists():
                raise BackupError(f"Backup file not found: {backup_path}")
            
            shutil.copy2(backup, target)
            return True
        except Exception as e:
            raise BackupError(f"Failed to restore backup: {e}")
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a specific backup"""
        try:
            backup = Path(backup_path)
            if backup.exists():
                backup.unlink()
                return True
            return False
        except Exception as e:
            raise BackupError(f"Failed to delete backup: {e}")


# Global backup service instance
backup_service = BackupService()
