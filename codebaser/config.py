#!/usr/bin/env python3
"""Centralized configuration and constants."""

# Color palette
COLORS = {
    'background': '#1B211A',
    'primary': '#628141',
    'secondary': '#8BAE66',
    'accent': '#EBD5AB',
    'surface': '#2A3129',
    'text_primary': '#EBD5AB',
    'text_secondary': '#8BAE66',
    'divider': '#3A4239',
    'success': '#8BAE66',
    'warning': '#EBD5AB',
    'error': '#C44536',
    'stop': '#C44536'
}

# Default output filename
DEFAULT_OUTPUT_FILENAME = "codebase.txt"

# Hidden files/folders start with these prefixes.
HIDDEN_PREFIXES = ('.',)

# Whether hidden files/folders (.env, .git, etc.) are shown in the tree.
SHOW_HIDDEN_FILES = True

# Binary/non-text extensions. Selecting one of these warns before compiling.
UNSUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin', '.o', '.obj', '.class',
    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv',
    '.ttf', '.otf', '.woff', '.woff2',
    '.db', '.sqlite', '.sqlite3', '.pyc', '.pyo',
}

# Filenames/extensions/keywords that usually hold secrets. Selecting one
# of these warns before compiling.
SENSITIVE_FILE_NAMES = {
    '.env', '.env.local', '.env.development', '.env.production', '.env.test',
    '.npmrc', '.pypirc', '.netrc', '.htpasswd',
    'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
    'credentials', 'credentials.json', 'secrets.json', 'secrets.yaml', 'secrets.yml',
}
SENSITIVE_EXTENSIONS = {'.pem', '.key', '.pfx', '.p12', '.crt', '.cer'}
SENSITIVE_KEYWORDS = ('secret', 'credential', 'password', 'apikey', 'api_key', 'token')

# File extension to emoji mapping
ICON_MAP = {
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

# UI fonts
FONT_TITLE = ('Segoe UI', 36, 'bold')
FONT_SUBTITLE = ('Segoe UI', 14)
FONT_HEADING = ('Segoe UI', 11, 'bold')
FONT_BODY = ('Segoe UI', 10)
FONT_SMALL = ('Segoe UI', 9)
FONT_BUTTON = ('Segoe UI', 10, 'bold')
FONT_BUTTON_LARGE = ('Segoe UI', 12, 'bold')