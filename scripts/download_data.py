"""Download the Stack Overflow Developer Survey 2026 files into data/raw/.

Usage, from the repository root:
    python scripts/download_data.py

Files that already exist are skipped, so the script is safe to run several times.
The logic lives in src/so_ai/download.py so the app can reuse it at start-up.
"""

import sys

from so_ai.download import download_2026

if __name__ == "__main__":
    download_2026()
    sys.exit(0)
