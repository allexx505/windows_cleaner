"""
Application constants. Internal defaults for intervals and resource limits
are not exposed to user config (lightweight / resource guard).
"""
import os

# App
APP_NAME = "Windows Cleaner"
APP_VERSION = "1.0.0"

# Paths (under user app data to avoid admin)
if "APPDATA" in os.environ:
    _base = os.path.join(os.environ["APPDATA"], APP_NAME.replace(" ", ""))
else:
    _base = os.path.expanduser("~/.windows_cleaner")
CONFIG_DIR = _base
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
INDEX_DB_DIR = CONFIG_DIR
INDEX_DB_NAME = "file_index.db"

# Internal intervals (not user-configurable)
DISK_CHECK_INTERVAL_MINUTES = 20
LARGE_FILE_JUNK_SCAN_INTERVAL_HOURS = 24
BATCH_DIRS_BEFORE_SLEEP = 200
BATCH_SLEEP_SECONDS = 0.5
RESOURCE_CHECK_INTERVAL_SECONDS = 5

# Resource guard thresholds (internal)
CPU_PERCENT_THRESHOLD = 70.0
MEMORY_MB_THRESHOLD = 400
HIGH_LOAD_SLEEP_SECONDS = 10

# Index / scan
MAX_RESULTS_PAGE = 500
DEFAULT_PAGE_SIZE = 100

# Junk dirs (Windows common temp/cache)
JUNK_DIR_ENV_KEYS = [
    "TEMP",
    "TMP",
    "LOCALAPPDATA",
]

# Junk subpaths under LOCALAPPDATA (relative)
JUNK_SUBPATHS = [
    "Temp",
    "Microsoft\\Windows\\INetCache",
    "Google\\Chrome\\User Data\\Default\\Cache",
    "Microsoft\\Edge\\User Data\\Default\\Cache",
]
