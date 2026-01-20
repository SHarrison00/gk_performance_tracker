import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Mapping, Any

import boto3
from dotenv import load_dotenv

from app.config import Config
from app.utils import ts

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")


def normalize_prefix(prefix: str) -> str:
    prefix = (prefix or "").strip("/")
    return f"{prefix}/" if prefix else ""


def normalize_prefix(prefix: str) -> str:
    prefix = (prefix or "").strip("/")
    return f"{prefix}/" if prefix else ""


def list_s3_objects(s3, bucket: str, prefix: str) -> list[dict[str, Any]]:
    """
    List objects under s3://bucket/prefix.

    Returns a list of dicts with at least:
      - Key (str)
      - LastModified (datetime)
      - Size (int)
    """
    out: list[dict[str, Any]] = []

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []) or []:
            key = obj.get("Key", "")
            if not key or key.endswith("/"):
                continue
            out.append(obj)

    return out


def local_path_for_key(local_dir: Path, prefix: str, key: str) -> Path:
    """Map S3 object name (key) to local file path."""
    if prefix and key.startswith(prefix):
        rel = key[len(prefix):]
    else:
        rel = key
    return local_dir / rel


def is_download_needed(local_path: Path, s3_last_modified: datetime) -> bool:
    """Decides whether a local file needs to be downloaded from S3."""
    if not local_path.exists():
        return True
    else:
        local_mtime = os.path.getmtime(local_path)
        local_mtime_dt = datetime.fromtimestamp(local_mtime, tz=timezone.utc)

    s3_last_modified_utc = s3_last_modified.astimezone(timezone.utc)

    return s3_last_modified_utc > local_mtime_dt


def download_object(s3, bucket: str, key: str, local_path: Path) -> None:
    """Download a S3 object to a given local path."""
    local_path.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, str(local_path))


def sync_latest(bucket: str, prefix: str, local_dir: Path, state_path: Path) -> None:
    if not bucket:
        raise ValueError("Missing S3 bucket (Config.S3_BUCKET)")
    prefix = normalize_prefix(prefix)
    s3 = boto3.client("s3")

    objs = list_s3_objects(s3, bucket, prefix)
    if not objs:
        raise RuntimeError("No objects found under bucket/prefix")



    downloaded = []
    skipped = []

    for obj in objs:
        key = obj["Key"]
        s3_mlast = obj["LastModified"]
        s3_mlast_iso = s3_mlast.astimezone(timezone.utc).isoformat(timespec="seconds")
        
        local_path = local_path_for_key(local_dir, prefix, key)

        if is_download_needed(local_path, s3_mlast):
            download_object(s3, bucket, key, local_path)
            downloaded.append({
                "key": key,
                "local_path": str(local_path),
                "s3_last_modified_utc": s3_mlast_iso
            })
        else:
            skipped.append({
                "key": key,
                "local_path": str(local_path),
                "s3_last_modified_utc": s3_mlast_iso
            })

    result = {
        "bucket": bucket,
        "prefix": prefix,
        "synced_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "downloaded_count": len(downloaded),
        "skipped_count": len(skipped),
        "downloaded": downloaded,
        "skipped": skipped
    }

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(result, indent=2))

    return


def _recently_synced(state_path: Path, min_seconds: int) -> bool:
    if not state_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text())
        t = state.get("synced_at_utc")
        if not t:
            return False
        last = datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(timezone.utc)
        return datetime.now(timezone.utc) - last < timedelta(seconds=min_seconds)
    except Exception:
        return False


def sync_data(config: Mapping[str, Any]) -> None:
    """Sync local data directory with S3. Runs once at app startup."""
    bucket = config["S3_BUCKET"]
    prefix = config.get("S3_PREFIX", "")
    local_dir = Path(config["DATA_DIR"])
    state_path = local_dir / ".sync.json"    
    min_seconds = int(config.get("MIN_SYNC_INTERVAL_SECONDS", 300))

    force = str(config.get("FORCE_S3_SYNC", "0")) == "1"
    if not force and _recently_synced(state_path, min_seconds):
        print(f"[{ts()}] Skipping S3 sync (synced recently).")
        return

    print(f"[{ts()}] Syncing latest files from S3...")
    sync_latest(bucket, prefix, local_dir, state_path)
    print(f"[{ts()}] Synced latest files from S3...")


def main():
    sync_data({
        "S3_BUCKET": Config.S3_BUCKET,
        "S3_PREFIX": Config.S3_PREFIX,
        "DATA_DIR": Config.DATA_DIR,
        "FORCE_S3_SYNC": Config.FORCE_S3_SYNC
    })
    


if __name__ == "__main__": 
    main()
