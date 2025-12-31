import time
import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from utils.logging import ts, update_status_json, make_status_patch
from utils.duckdb_io import load_df_as_table, get_rows_from_table


def build_csv_manifest(data_raw_dir, datasets):
    """Return {dataset: [csv_paths...]}"""
    return {
        dataset: sorted((data_raw_dir / dataset).glob("*.csv"))
        for dataset in datasets
    }


def clean_matchlogs_df(df):
    """Apply the matchlogs header shift and drop empty columns."""
    df.columns = df.columns[9:].tolist() + [None] * 9
    return df.loc[:, df.columns.notna()]


def load_csvs_to_duckdb(con, schema, tables_manifest):
    """
    Load CSVs into DuckDB schema.
    Returns dict like {"table_name": "123 rows"} for status logging.
    """
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    tables = {}
    for dataset, csv_files in tables_manifest.items():
        for csv_path in csv_files:
            table_name = csv_path.stem.lower().replace("-", "_")
            fq_table_name = f"{schema}.{table_name}"

            df = pd.read_csv(csv_path)

            # Dataset-specific cleaning
            if dataset == "matchlogs":
                df = clean_matchlogs_df(df)

            print(f"[{ts()}] Loading {fq_table_name}...")
            tmp_df = "tmp_df"
            con.register(tmp_df, df)
            load_df_as_table(con, tmp_df, fq_table_name)
            rows = get_rows_from_table(con, tmp_df)
            con.unregister(tmp_df)
            tables[table_name] = f"{rows} rows"

            print(f"[{ts()}] Loaded {fq_table_name}")

    return tables


def main():
    # Config
    db_path = REPO_ROOT / "dbt_project" / "dev.duckdb"
    data_raw_dir = REPO_ROOT / "data" / "raw" / "fbref"
    public_dir = REPO_ROOT / "public"
    schema = "raw_matchlogs"
    datasets = ["matchlogs"]
    tables_manifest = build_csv_manifest(data_raw_dir, datasets)

    # Duration tracking
    started_utc = ts()
    t0 = time.perf_counter()

    with duckdb.connect(db_path) as con:
        tables = load_csvs_to_duckdb(con, schema, tables_manifest)

    duration_s = round(time.perf_counter() - t0, 3)
    finished_utc = ts()

    # Logging
    status_patch = make_status_patch(
        step_name = "load_duckdb.py",
        info = "Load player matchlogs data into DB.",
        started_utc = started_utc,
        finished_utc = finished_utc,
        duration_s = duration_s,
        tables = tables,
    )
    update_status_json(public_dir / "status.json", status_patch)


if __name__ == "__main__":
    main()
