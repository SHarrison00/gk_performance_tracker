import time
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from utils.logging import ts, update_status_json, make_status_patch
from utils.shell import run_cmd


def main():
    # Config
    bucket = "gk-performance-tracker-data"
    public_dir = REPO_ROOT / "public"
    history_dest = f"s3://{bucket}/history/{ts()}/"
    latest_dest = f"s3://{bucket}/latest/"

    # Duration tracking
    started_utc = ts()
    t0 = time.perf_counter()

    run_cmd(["aws", "s3", "sync", str(public_dir) + "/", history_dest], REPO_ROOT) # for rollback
    run_cmd(["aws", "s3", "sync", str(public_dir) + "/", latest_dest, "--delete"], REPO_ROOT)

    duration_s = round(time.perf_counter() - t0, 3)
    finished_utc = ts()

    # Logging
    status_patch = make_status_patch(
        step_name = "upload_public_to_s3.py",
        info = "Upload data to S3 (and history snapshot for rollback).",
        started_utc = started_utc,
        finished_utc = finished_utc,
        duration_s = duration_s
    )
    update_status_json(public_dir / "status.json", status_patch)


if __name__ == "__main__":
    main()
