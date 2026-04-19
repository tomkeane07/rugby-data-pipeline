-- Fails if any match does not have exactly two rows whose score_difference values sum to 0.
with match_score_checks as (
  select
    match_id,
    count(*) as team_rows,
    sum(score_difference) as score_diff_sum
  from {{ ref('fct_team_performance') }}
  where match_id is not null
  group by match_id
)
select
  match_id,
  team_rows,
  score_diff_sum
from match_score_checks
where team_rows != 2
   or abs(score_diff_sum) > 0.000001
