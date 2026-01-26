from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import dash_ag_grid as dag
import pandas as pd


@dataclass(frozen=True)
class GridSpec:
    """
    Immutable configuration object for constructing Dash AG Grid tables.
    """
    grid_id: str
    reference_cols: Sequence[str] = ("Goalkeeper", "Team")
    default_col_def: dict = None
    pinned_cols: bool = True
    height: str = "50vh"
    dash_grid_options: dict = None


def build_column_defs(df: pd.DataFrame, 
                      reference_cols: Iterable[str], 
                      pinned_cols: bool = True,
                      ) -> list[dict]:
    """
    Build AG Grid ``columnDefs`` with optional pinned reference columns.
    """
    ref = set(reference_cols)
    return [
        {
            "field": col,
            **({"pinned": "left"} if pinned_cols and col in ref else {}),
        }
        for col in df.columns
    ]


def make_aggrid(df: pd.DataFrame, spec: GridSpec) -> dag.AgGrid:
    """
    Create a Dash AG Grid component from a dataframe and grid specification.
    """
    
    default_col_def = {"sortable": True, "filter": True, "resizable": True}
    default_col_def = spec.default_col_def or default_col_def
    grid_options = spec.dash_grid_options or {}

    return dag.AgGrid(
        id = spec.grid_id,
        rowData = df.to_dict("records"),
        columnDefs = build_column_defs(df, spec.reference_cols, spec.pinned_cols),
        defaultColDef = default_col_def,
        dashGridOptions = grid_options,
        style = {"height": spec.height},
    )


def reset_grid(df: pd.DataFrame, spec: GridSpec):
    """
    Recreate a fresh AG Grid instance to clear filters and sorting state.
    """
    return make_aggrid(df, spec)
