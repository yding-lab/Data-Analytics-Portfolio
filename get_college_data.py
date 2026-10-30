"""Download the College dataset used by notebooks/01_college_admissions_analysis.ipynb.

    python get_college_data.py          # -> data/College.csv

Source: the `College` data set from the ISLR R package, version 1.4 (James, Witten, Hastie
and Tibshirani, *An Introduction to Statistical Learning*), read from the CRAN mirror on
GitHub at that pinned version. The package documents the data as statistics for 777 US
colleges from the 1995 issue of US News & World Report, taken from the StatLib library at
Carnegie Mellon University (ASA Statistical Graphics Section's 1995 Data Analysis Exposition).
The ISLR package is distributed under GPL-2. The file is downloaded, not redistributed here.
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/cran/ISLR/1.4/data/College.rda"
OUT = Path(__file__).resolve().parent / "data" / "College.csv"


def main() -> int:
    try:
        import pyreadr
    except ImportError:
        print("pyreadr is required: pip install -r requirements.txt", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        rda = Path(tmp) / "College.rda"
        with urllib.request.urlopen(URL, timeout=60) as response:
            rda.write_bytes(response.read())
        digest = hashlib.sha256(rda.read_bytes()).hexdigest()
        college = next(iter(pyreadr.read_r(str(rda)).values()))

    if college.shape != (777, 18):
        print(f"Unexpected shape {college.shape}; expected (777, 18)", file=sys.stderr)
        return 1

    # Same layout as the course version of College.csv: the 18 variables plus a Names column.
    college = college.copy()
    college["Private"] = college["Private"].astype(str)
    numeric = [c for c in college.columns if c != "Private"]
    college[numeric] = college[numeric].round().astype(int).where(college[numeric] % 1 == 0, college[numeric])
    college["Names"] = college.index
    OUT.parent.mkdir(exist_ok=True)
    college.to_csv(OUT, index=False)
    print(f"Wrote {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}: "
          f"{len(college)} rows (source sha256 {digest[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
