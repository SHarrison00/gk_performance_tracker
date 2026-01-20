import pandas as pd
import numpy as np
from pathlib import Path
import json

REPO_ROOT = Path().resolve().parents[0]
APP_ROOT = REPO_ROOT / "app"
DATA_DIR = APP_ROOT / "data" / "raw"


def get_clean_label_mapping(table_name: str) -> dict:
    """Get clean label mapping for given table."""

    with open(DATA_DIR / 'table_metadata.json', 'r') as file:
        table_metadata = json.load(file)

    table_dict = table_metadata["models"].get(table_name, {})
    columns_dict = table_dict.get("columns", {})

    label_mapping = {}

    for col in columns_dict.keys():
        label = columns_dict[col]["label"] or ""
        label_mapping[col] = label

    return label_mapping


def clean_numeric_columns(df: pd.DataFrame, decimals: int = 1) -> pd.DataFrame:
    """Gerneral-purpose step to clean numeric columns."""

    df = df.copy()

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            series = df[col].dropna()

            if series.empty:
                continue

            # Check if values are effectively integers
            is_integer_like = np.all(np.isclose(series % 1, 0))

            if is_integer_like:
                # Use pandas nullable integer
                df[col] = df[col].round(0).astype("Int64")
            else:
                df[col] = df[col].round(decimals)

    return df


def title_case_columns(df: pd.DataFrame, columns = list[str]) -> pd.DataFrame:
    """Covert lower case columns with underscores to title case."""
    df = df.copy()
    for col in columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("_", " ")
            .str.title()
        )        
    return df


def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """Combine repeatable transformation logic."""
    df = clean_numeric_columns(df)
    df = title_case_columns(df, ["Goalkeeper"])
    return df
