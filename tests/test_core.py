import pytest

from vec_p3_freeze.core import checklist, freeze, verify


def test_freeze_verify_and_two_slot_rule(tmp_path):
    source = tmp_path / "pred.h5ad"
    source.write_bytes(b"prediction")
    bundle = tmp_path / "bundle"

    manifest = freeze(bundle, "T1:val", 1, source, "best")
    assert len(manifest["sha256"]) == 64
    assert verify(bundle)[0]["status"] == "OK"

    with pytest.raises(FileExistsError):
        freeze(bundle, "T1:val", 1, source)
    with pytest.raises(ValueError):
        freeze(bundle, "T1:val", 3, source)

    text = checklist(bundle)
    assert "T1:val" in text
    assert "slot" in text.lower()


def test_change_detected_even_if_readonly_bit_reset(tmp_path):
    source = tmp_path / "pred.h5ad"
    source.write_bytes(b"a")
    bundle = tmp_path / "bundle"

    manifest = freeze(bundle, "T3:gata4", 2, source)
    frozen = bundle / manifest["file"]
    frozen.chmod(0o644)
    frozen.write_bytes(b"b")

    assert verify(bundle)[0]["status"] == "CHANGED"


def test_unknown_board_and_missing_source_rejected(tmp_path):
    source = tmp_path / "missing.h5ad"
    with pytest.raises(ValueError):
        freeze(tmp_path / "b", "T9:nope", 1, source)
    with pytest.raises(FileNotFoundError):
        freeze(tmp_path / "b", "T1:val", 1, source)
