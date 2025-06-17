"""
History service for tracking file edit operations
"""

import datetime
from typing import Dict, List, Optional

from ..core import ServiceBase, MAX_EDIT_HISTORY_ENTRIES


class HistoryService(ServiceBase):
    """Service for tracking and managing edit history"""
    
    def __init__(self):
        self.edit_history: List[Dict] = []
        self.max_entries = MAX_EDIT_HISTORY_ENTRIES
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize history service"""
        # Could load history from file if needed
        pass
    
    def cleanup(self) -> None:
        """Cleanup old history entries"""
        # Trim history to max entries
        if len(self.edit_history) > self.max_entries:
            self.edit_history = self.edit_history[-self.max_entries:]
    
    def log_edit(self, action: str, file_path: str, details: dict) -> None:
        """Log a file editing action"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "file": file_path,
            "details": details
        }
        
        self.edit_history.append(log_entry)
        
        # Keep only last max_entries
        if len(self.edit_history) > self.max_entries:
            self.edit_history.pop(0)
    
    def get_history(self, limit: Optional[int] = None, 
                   file_path: Optional[str] = None) -> List[Dict]:
        """Get edit history with optional filtering"""
        history = self.edit_history
        
        # Filter by file path if specified
        if file_path:
            history = [entry for entry in history if entry['file'] == file_path]
        
        # Apply limit
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_file_history(self, file_path: str, limit: Optional[int] = None) -> List[Dict]:
        """Get history for a specific file"""
        return self.get_history(limit=limit, file_path=file_path)
    
    def get_recent_files(self, limit: int = 10) -> List[str]:
        """Get list of recently edited files"""
        recent_files = []
        seen_files = set()
        
        # Go through history in reverse order (newest first)
        for entry in reversed(self.edit_history):
            file_path = entry['file']
            if file_path not in seen_files:
                recent_files.append(file_path)
                seen_files.add(file_path)
                
                if len(recent_files) >= limit:
                    break
        
        return recent_files
    
    def clear_history(self) -> None:
        """Clear all edit history"""
        self.edit_history.clear()
    
    def export_history(self) -> Dict:
        """Export history for backup/analysis"""
        return {
            "export_time": datetime.datetime.now().isoformat(),
            "total_entries": len(self.edit_history),
            "history": self.edit_history
        }
    
    def get_stats(self) -> Dict:
        """Get statistics about edit history"""
        if not self.edit_history:
            return {"total_edits": 0}
        
        # Count actions
        action_counts = {}
        file_counts = {}
        
        for entry in self.edit_history:
            action = entry['action']
            file_path = entry['file']
            
            action_counts[action] = action_counts.get(action, 0) + 1
            file_counts[file_path] = file_counts.get(file_path, 0) + 1
        
        # Most edited files
        most_edited = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_edits": len(self.edit_history),
            "action_counts": action_counts,
            "most_edited_files": most_edited,
            "recent_activity": len([e for e in self.edit_history 
                                  if (datetime.datetime.now() - 
                                     datetime.datetime.fromisoformat(e['timestamp'])).days < 1])
        }


# Global history service instance  
history_service = HistoryService()
