import json
from pathlib import Path


def write_table_metadata(dbt_dir: Path, public_dir: Path) -> None:
    manifest_path = dbt_dir / "target" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    out = {"models": {}}

    # Only dbt models (not tests, snapshots, etc.)
    for unique_id, node in (manifest.get("nodes") or {}).items():
        if node.get("resource_type") != "model":
            continue

        model_name = node.get("name")
        cols = node.get("columns") or {}

        out["models"][model_name] = {
            "description": node.get("description") or "",
            "columns": {},
        }

        for col_name, col_def in cols.items():
            meta = col_def.get("meta") or {}
            out["models"][model_name]["columns"][col_name] = {
                "label": meta.get("label"),
                "description": col_def.get("description") or ""         
            }

    out_dir = public_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "table_metadata.json"
    out_path.write_text(json.dumps(out, indent=2))
    return
