import json
from pathlib import Path
from datetime import datetime, timezone


def ts():
    return datetime.now().isoformat(timespec="seconds")


def write_manifest(path: Path, manifest: list[dict]) -> None:
    path.write_text(json.dumps(manifest, indent=2))


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()