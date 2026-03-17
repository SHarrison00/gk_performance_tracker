## Models

### Staging

| Model | Materialization | Grain | Description |
|-------|----------------|-------|-------------|
| `stg_matchlogs__all` | View | goalkeeper-match | All raw match logs unioned across players |
| `stg_matchlogs__parsed` | View | goalkeeper-match | Cleaned and type-cast match-level data |

### Marts

| Model | Materialization | Grain | Description |
|-------|----------------|-------|-------------|
| `fct_goalkeeper_performance` | Table | goalkeeper | Season aggregates per goalkeeper |
| `mart_goalkeeper_league_ratings` | Table | goalkeeper | Z-scores, percentiles and overall rank |

---

For full column-level documentation run:
    `dbt docs generate && dbt docs serve`