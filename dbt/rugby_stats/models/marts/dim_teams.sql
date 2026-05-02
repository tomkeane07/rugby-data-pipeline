select
  team_id,
  any_value(team_name) as team_name,
  case when lower(any_value(team_name)) = 'other' then true else false end as is_unlabeled_team
from {{ ref('stg_teams') }}
group by team_id
