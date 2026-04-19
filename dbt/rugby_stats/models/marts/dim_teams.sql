select
  team_id,
  any_value(team_name) as team_name
from {{ ref('stg_teams') }}
group by team_id
