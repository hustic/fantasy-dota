SELECT dp.account_id
     , lp.name
     , dp.role
     , lp.team_id
     , lp.team_tag
  FROM logs_players AS lp
  JOIN dim_players AS dp
    ON lp.account_id = dp.account_id