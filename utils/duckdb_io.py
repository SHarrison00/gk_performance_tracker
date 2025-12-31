import duckdb


def connect(db_path):
    return duckdb.connect(str(db_path))


def export_table_to_parquet(con, table: str, out_path):
    con.execute(f"COPY (SELECT * FROM {table}) TO '{out_path}' (FORMAT PARQUET)")


def load_df_as_table(con, df_name: str, table_name: str):
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {df_name}")


def get_rows_from_table(con, table: str):
    return con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
