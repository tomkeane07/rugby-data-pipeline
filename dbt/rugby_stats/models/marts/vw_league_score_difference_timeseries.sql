{{ config(materialized='view') }}

with base as (
  select
    game_date,
    team_name,
    score_difference,
    competition_id,
    competition_name
  from {{ ref('fct_team_performance') }}
),
league_mapped as (
  select
    game_date,
    team_name,
    score_difference,
    competition_id,
    competition_name,
    case
      when competition_id = '83d92007' then 'European Rugby Challenge Cup'
      when competition_id = 'ee0c6883' then 'European Rugby Champions Cup'
      when lower(competition_name) = 'major league rugby' then 'Major League Rugby'
      when lower(competition_name) in ('super rugby pacific', 'super rugby')
        or competition_id = '877aa127' then 'Super Rugby Pacific'
      else null
    end as league_name
  from base
)
select
  game_date,
  team_name,
  score_difference,
  competition_id,
  competition_name,
  league_name
from league_mapped
where league_name is not null
