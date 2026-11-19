"""Checks the repository's explicit document status convention."""

from pathlib import Path
import re
import sys


STATUS_RE = re.compile(r"^\s*Status\s*:\s*ESQUELETO\s*$", re.IGNORECASE | re.MULTILINE)
REQUIRED = (
    Path("docs/OBSERVABILIDADE.md"),
    Path("docs/ROTEIRO_DEMO_BANCA.md"),
    Path("docs/INVESTOR_CTO_PRESSURE_TEST.md"),
    Path("docs/PITCH_FATOS.md"),
)


def check_status(root: Path = Path(".")) -> tuple[list[str], list[str]]:
    required = [root / path for path in REQUIRED]
    docs_root = root / "docs"
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    incomplete = [
        path.relative_to(root).as_posix()
        for path in docs_root.rglob("*.md")
        if STATUS_RE.search(path.read_text(encoding="utf-8"))
    ]
    return missing, incomplete


def main() -> int:
    missing, incomplete = check_status()
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
