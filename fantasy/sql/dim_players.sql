SELECT p.account_id
     , p.name
     , p.fantasy_role
     , p.team_id
  FROM logs_players AS p, dim_teams AS t
 WHERE p.team_id = t.team_id
