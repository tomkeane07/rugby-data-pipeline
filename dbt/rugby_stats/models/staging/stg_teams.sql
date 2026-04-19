select distinct
  cast(team_id as string) as team_id,
  cast(team_name as string) as team_name
from {{ source('raw', 'teams') }}
where team_id is not null
