import subprocess
import sys


def test_cli_freeze_verify_checklist(tmp_path):
    source = tmp_path / "pred.h5ad"
    source.write_bytes(b"synthetic")
    bundle = tmp_path / "bundle"

    freeze_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_p3_freeze.cli",
            "freeze",
            "--bundle",
            str(bundle),
            "--board",
            "T1:val",
            "--slot",
            "1",
            "--file",
            str(source),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert freeze_run.returncode == 0, freeze_run.stdout + freeze_run.stderr

    verify_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_p3_freeze.cli",
            "verify",
            "--bundle",
            str(bundle),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify_run.returncode == 0
    assert "OK" in verify_run.stdout

    checklist_run = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_p3_freeze.cli",
            "checklist",
            "--bundle",
            str(bundle),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert checklist_run.returncode == 0
    assert (bundle / "SUBMISSION_CHECKLIST.md").exists()
