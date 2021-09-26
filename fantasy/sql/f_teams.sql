SELECT lt.team_id
     , lt.name
     , lt.tag
     , lt.last_match_time
     , lt.rating
     , lt.wins
     , lt.losses
  FROM logs_teams AS lt
  JOIN dim_teams AS dt
    ON lt.tag = dt.tag