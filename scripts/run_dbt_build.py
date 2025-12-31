import time
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from utils.logging import ts, update_status_json, make_status_patch
from utils.shell import run_cmd


def main():
    # Config
    dbt_dir = REPO_ROOT / "dbt_project"
    public_dir = REPO_ROOT / "public"

    # Duration tracking
    started_utc = ts()
    t0 = time.perf_counter()

    run_cmd(["dbt", "debug"], cwd = dbt_dir)
    run_cmd(["dbt", "build"], cwd = dbt_dir)

    duration_s = round(time.perf_counter() - t0, 3)
    finished_utc = ts()

    status_patch = make_status_patch(
        step_name = "run_dbt_build.py",
        info = "Transform loaded data into final tables using dbt.",
        started_utc = started_utc,
        finished_utc = finished_utc,
        duration_s = duration_s
    )
    update_status_json(public_dir / "status.json", status_patch)


if __name__ == "__main__":
    main()
