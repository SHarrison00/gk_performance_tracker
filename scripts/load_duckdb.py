from pathlib import Path
import sys
import pandas as pd

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

        df = pd.read_csv(csv_path)

        if schema == "raw_matchlogs":
            # Shift headers left by 9 and drop empty columns
            df.columns = df.columns[9:].tolist() + [None] * 9
            df = df.loc[:, df.columns.notna()]
            
        print(f"[{ts()}] Loading {fq_table}...")

        con.register("tmp_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {fq_table} AS SELECT * FROM tmp_df;")
        con.unregister("tmp_df")

        print(f"[{ts()}] Loaded {fq_table}") 
        
""" 

    python -m scripts.load_duckdb 

"""