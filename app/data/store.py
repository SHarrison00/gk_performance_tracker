import pandas as pd
from pathlib import Path

REPO_ROOT = Path().resolve().parents[0]
APP_ROOT = REPO_ROOT / "app"
DATA_DIR = APP_ROOT / "data" / "raw"

from .transforms import get_clean_label_mapping


def get_parquet_table(pq_table: str, params: list, clean_labels: bool) -> pd.DataFrame:
    """Get DataFrame for given Parquet table."""

    pq_path = DATA_DIR / f"{pq_table}.parquet"

    # Read table & apply any filtering
    df = pd.read_parquet(pq_path, filters=params)

    # Rename headers to "nice" user-friendly labels
    if clean_labels:        
        label_mapping = get_clean_label_mapping(pq_table)
        df.rename(columns=label_mapping, inplace=True)

    return df