# Score Difference Data Quality Incident

## Summary

A data quality issue was identified in the score-difference time series: some matches had only one team row in source data, while other matches correctly had both team rows.

Expected rule per match:

- If two teams are present for a match, score differences must be additive inverses.
- In other words, for each match with two rows: `score_difference_team_a + score_difference_team_b = 0`.

## Discovery Evidence

The issue was identified during pipeline validation: some matches appeared with only one team row in source data rather than two.

## Verification

A schema-aware profile over local `data/raw/team_stats/*.parquet` confirmed:

- `teams_per_match` distribution included one-sided matches.
- `one_sided_matches = 18`
- For matches with exactly 2 team rows, inverse symmetry held with zero violations:
  - `two_team_matches = 3171`
  - `inverse_violations = 0`

Interpretation:

- The transformation logic for score difference was mathematically correct.
- The one-sided match behavior was caused by incomplete match coverage in source rows.

## Root Cause

Two source completeness problems contributed to the issue:

1. Some `match_id` values had only one team row available.
2. A subset of historical parquet files had schema drift and lacked score columns, reducing usable rows for score-difference analytics.

## Remediation Implemented

### 1) Model-level completeness filter

`int_team_game_metrics` was updated to keep only scored rows from complete two-team matches.

File:

- `dbt/rugby_stats/models/intermediate/int_team_game_metrics.sql`

Logic added:

- Keep rows where `score` and `opponent_score` are non-null.
- Keep only `match_id` groups with `count(distinct team_id) = 2`.

### 2) Ongoing quality guardrail

A custom dbt data test was added to enforce symmetry in the final fact model.

File:

- `dbt/rugby_stats/tests/fct_team_performance_score_symmetry.sql`

Test rule:

- Fail if any `match_id` has `team_rows != 2` or `abs(sum(score_difference)) > 0.000001`.

## Validation After Fix

Targeted dbt build/test for the affected models and symmetry test completed successfully.

Outcome:

- No symmetry violations remain in `fct_team_performance`.
- The score-difference time series now reflects only complete, consistent match pairs.

## Pipeline Integration

This is now an explicit quality gate in the transformation layer:

1. Raw ingestion lands source data.
2. Intermediate model filters to complete scored matches.
3. Fact model is validated by symmetry test before downstream dashboard use.

This ensures score-difference analytics remain internally consistent across runs.
