{{ config(materialized='view') }}

select
  case
    when competition_id = '83d92007' then 'European Rugby Challenge Cup'
    when competition_id = 'ee0c6883' then 'European Rugby Champions Cup'
    when competition_name in ('Super Rugby Pacific', 'Super Rugby') or competition_id = 'bc5d9ec5'
      then 'Super Rugby Pacific'
    else null
  end as league_name,
  count(distinct match_id) as matches,
  avg(abs(score_difference)) as avg_match_margin,
  approx_quantiles(abs(score_difference), 100)[offset(50)] as median_match_margin
from {{ ref('fct_team_performance') }}
where score_difference is not null
group by 1
having league_name is not null