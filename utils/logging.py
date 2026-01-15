import json
from pathlib import Path
from datetime import datetime, timezone


def ts():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_manifest(path: Path, manifest: list[dict]) -> None:
    path.write_text(json.dumps(manifest, indent=2))


def sort_by_pipeline_order(data: dict) -> dict:
    ordered = {}

    PIPELINE_ORDER = [
        "cli.py",
        "load_duckdb.py",
        "run_dbt_build.py",
        "stage_public_tables.py",
        "upload_public_to_s3.py"
    ]

    for key in PIPELINE_ORDER:
        if key in data:
            ordered[key] = data[key]

    return ordered


def update_status_json(path: Path, patch: dict):
    data = {}

    if path.exists():
        with open(path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    data.update(patch)

    # Re-order JSON according to pipeline order
    data = sort_by_pipeline_order(data)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def make_status_patch(step_name, 
                      info, 
                      started_utc, 
                      finished_utc, 
                      duration_s, 
                      tables=None):
    """
    Small helper so status.json structure stays consistent across scripts.
    """
    return {
        step_name: {
            "info": info,
            "started_utc": started_utc,
            "finished_utc": finished_utc,
            "duration_s": duration_s,
            "tables": tables,
        }
    }