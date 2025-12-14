from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from utils.logging import ts
import duckdb


DB_PATH = REPO_ROOT / "dbt_project" / "dev.duckdb"
DATA_ROOT = REPO_ROOT / "data/raw/fbref"

DATASETS = ["matchlogs"]

TABLES = {
    dataset: sorted((DATA_ROOT / dataset).glob("*.csv"))
    for dataset in DATASETS
}

con = duckdb.connect(DB_PATH)

schema = "raw_matchlogs"
con.execute(f"create schema if not exists {schema};")


for dataset, csv_files in TABLES.items():
    for csv_path in csv_files:

        table_name = csv_path.stem.lower().replace("-", "_")
        fq_table = f"{schema}.{table_name}"

        print(f"[{ts()}] Loading {fq_table}...")

        con.execute(
            f"""
            create or replace table {fq_table} as
            select *
            from read_csv_auto('{csv_path.as_posix()}', header=true);
            """
        )

        print(f"[{ts()}] Loaded {fq_table}")
 
""" 

    python -m scripts.load_duckdb 

"""