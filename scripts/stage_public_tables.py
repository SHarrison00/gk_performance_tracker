import time
import sys
from pathlib import Path
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from utils.logging import ts, update_status_json, make_status_patch
from utils.duckdb_io import export_table_to_parquet, get_rows_from_table


def export_tables_to_public(con, exports, out_dir):
    """
    Export each table in `exports` to `out_dir` as parquet.
    Returns dict like {"table": "123 rows"} for status logging.
    """
    tables = {}

    for table in exports:
        out_path = out_dir / f"{table}.parquet"
        print(f"[{ts()}] Exporting {table}...")

        export_table_to_parquet(con, table, out_path)

        rows = get_rows_from_table(con, table)
        tables[table] = f"{rows} rows"

        print(f"[{ts()}] Exported {table}")

    return tables


def main():
    # Config
    db_path = REPO_ROOT / "dbt_project" / "dev.duckdb"
    public_dir = REPO_ROOT / "public"
    exports = ["fct_goalkeeper_performance", "mart_goalkeeper_league_ratings"]
    
    # Duration tracking
    started_utc = ts()
    t0 = time.perf_counter()

    with duckdb.connect(db_path) as con:
        tables = export_tables_to_public(con, exports, public_dir)

    duration_s = round(time.perf_counter() - t0, 3)
    finished_utc = ts()

    # Logging
    status_patch = make_status_patch(
        step_name = "stage_public_tables.py",
        info = "Export DuckDB tables to public/ for downstream upload to S3.",
        started_utc = started_utc,
        finished_utc = finished_utc,
        duration_s = duration_s,
        tables = tables,
    )
    update_status_json(public_dir / "status.json", status_patch)


if __name__ == "__main__":
    main()
