
import os

def get_file_icon(filename):
    """Get appropriate emoji icon for file type."""
    ext = os.path.splitext(filename)[1].lower()
    
    icon_map = {
        '.py': '🐍', '.js': '📜', '.jsx': '⚛️', '.ts': '📘', '.tsx': '⚛️',
        '.html': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
        '.java': '☕', '.cpp': '🔧', '.c': '🔧', '.h': '📋',
        '.json': '📦', '.xml': '📄', '.yml': '⚙️', '.yaml': '⚙️',
        '.md': '📝', '.txt': '📃', '.csv': '📊', '.sql': '🗄️',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗', '.xlsx': '📗',
        '.zip': '🗜️', '.tar': '🗜️', '.gz': '🗜️', '.7z': '🗜️',
        '.exe': '⚙️', '.dll': '🔧', '.so': '🔧', '.dylib': '🔧',
        '.sh': '🐚', '.bash': '🐚', '.zsh': '🐚',
        '.php': '🐘', '.rb': '💎', '.go': '🐹', '.rs': '🦀',
        '.swift': '🐦', '.kt': '🅺', '.dart': '🎯',
    }
    
    return icon_map.get(ext, '📄')
