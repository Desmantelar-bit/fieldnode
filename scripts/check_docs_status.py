"""Checks the repository's explicit document status convention."""

from pathlib import Path
import re
import sys


STATUS_RE = re.compile(r"^\s*Status\s*:\s*ESQUELETO\s*$", re.IGNORECASE | re.MULTILINE)
REQUIRED = (Path("docs/OBSERVABILIDADE.md"),)


def main() -> int:
    missing = [str(path) for path in REQUIRED if not path.exists()]
    incomplete = [str(path) for path in Path("docs").rglob("*.md") if STATUS_RE.search(path.read_text(encoding="utf-8"))]
    if missing or incomplete:
        for path in missing:
            print(f"missing required document: {path}")
        for path in incomplete:
            print(f"document has explicit ESQUELETO status: {path}")
        return 1
    print("documentation status: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
