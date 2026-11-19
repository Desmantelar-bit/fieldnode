from pathlib import Path

from check_docs_status import check_status


def test_status_detects_missing_target(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    missing, incomplete = check_status(tmp_path)

    assert "docs/ROTEIRO_DEMO_BANCA.md" in missing
    assert incomplete == []


def test_status_detects_only_exact_skeleton_marker(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    for relative in (
        "OBSERVABILIDADE.md",
        "ROTEIRO_DEMO_BANCA.md",
        "INVESTOR_CTO_PRESSURE_TEST.md",
        "PITCH_FATOS.md",
    ):
        (docs / relative).write_text("Status: FINALIZADO\n", encoding="utf-8")
    (docs / "other.md").write_text("A palavra ESQUELETO aparece no texto.\n", encoding="utf-8")

    missing, incomplete = check_status(tmp_path)

    assert missing == []
    assert incomplete == []


def test_status_detects_skeleton_in_any_document(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    for relative in (
        "OBSERVABILIDADE.md",
        "ROTEIRO_DEMO_BANCA.md",
        "INVESTOR_CTO_PRESSURE_TEST.md",
        "PITCH_FATOS.md",
    ):
        (docs / relative).write_text("Status: FINALIZADO\n", encoding="utf-8")
    (docs / "draft.md").write_text("Status: ESQUELETO\n", encoding="utf-8")

    missing, incomplete = check_status(tmp_path)

    assert missing == []
    assert incomplete == ["docs/draft.md"]
