"""Download the survey files from the Stack Overflow GitHub archive into data/raw/.

The files are stored with Git LFS, so we use media.githubusercontent.com.
The plain GitHub "raw" link would only return the small LFS pointer file.
"""

from __future__ import annotations

from pathlib import Path

import requests

BASE_URL = "https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# (year, remote file name, local file name)
FILES_2026 = [
    ("2026", "survey_results_public.csv", "survey_results_public_2026.csv"),
    ("2026", "survey_results_schema.csv", "survey_results_schema_2026.csv"),
]

MIN_SIZE = 1_000  # bytes: a real survey file is far larger than an LFS pointer


def download_file(year: str, remote_name: str, local_name: str, raw_dir: Path = RAW_DIR) -> Path:
    """Download one file unless it is already on disk. Returns the local path."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / local_name
    if target.exists() and target.stat().st_size > MIN_SIZE:
        print(f"[skip] {target.name} already present")
        return target

    url = f"{BASE_URL}/{year}/{remote_name}"
    print(f"[get ] {url}")
    tmp = target.with_suffix(".part")
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    head = tmp.read_bytes()[:40]
    if tmp.stat().st_size < MIN_SIZE or head.startswith(b"version https://git-lfs"):
        tmp.unlink()
        raise RuntimeError(f"{url} returned a Git LFS pointer, not the data file")

    tmp.replace(target)
    print(f"[ok  ] {target.name} ({target.stat().st_size / 1e6:.1f} MB)")
    return target


def download_2026(raw_dir: Path = RAW_DIR) -> list[Path]:
    """Download the 2026 answers and schema. Safe to call several times."""
    return [download_file(y, r, l, raw_dir) for y, r, l in FILES_2026]
