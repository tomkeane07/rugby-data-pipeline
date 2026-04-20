# Graph Development: League Score Difference Timeseries (Matplotlib)

This page documents the Matplotlib timeseries charts generated from `vw_league_score_difference_timeseries`.

## Visual Overview

```mermaid
flowchart LR
    classDef transform fill:#fde7c8,stroke:#b7791f,color:#4a2b00,stroke-width:1px;
    classDef field fill:#dbe7f7,stroke:#4f6b8a,color:#1d2d44,stroke-width:1px;
    classDef serve fill:#f7d9d9,stroke:#9b4d4d,color:#4a1f1f,stroke-width:1px;

    A[vw_league_score_difference_timeseries] --> B[team_name]
    A --> C[game_date]
    A --> D[score_difference]
    A --> E[league_name]
    A --> F[Per-league Matplotlib line chart images]

    class A transform;
    class B,C,D,E field;
    class F serve;
```

## Graph Purpose

These charts show match-by-match score-difference trajectories per team within each league.

Each league is written to its own image file to improve readability and avoid overcrowded subplot layouts.

## Backing Inputs

Primary columns used:

- `match_id`
- `game_date`
- `team_name`
- `opponent_team_name`
- `score_difference`
- `league_name`

Input source is selected by runtime mode:

- BigQuery mart `vw_league_score_difference_timeseries`
- or local parquet-derived equivalent

## Rendering Logic

For each league:

1. Select all teams by default (or top-N if `MPL_MAX_TEAMS_PER_LEAGUE` is set).
2. Plot one line per team with date on x-axis and score difference on y-axis.
3. Apply a shared y-axis scale across all league charts for comparability.
4. Render a compact legend using configurable entry and row caps.

## Output Artifacts

Default output naming pattern:

- `docs/assets/matplotlib/league_score_difference_timeseries_<league_slug>.png`

Examples:

- `docs/assets/matplotlib/league_score_difference_timeseries_european_rugby_challenge_cup.png`
- `docs/assets/matplotlib/league_score_difference_timeseries_european_rugby_champions_cup.png`
- `docs/assets/matplotlib/league_score_difference_timeseries_super_rugby_pacific.png`

## Shared Dependencies

This graph shares runtime controls and source-mode behavior with the categorical chart:

- [Matplotlib Pipeline Runtime and Configuration](../shared/matplotlib_pipeline_runtime_and_config.md)
