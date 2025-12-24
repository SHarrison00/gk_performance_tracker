{{ config(materialized='table') }}

with base as (

    select 

    *
  
    from {{ ref('stg_matchlogs__parsed') }}

    where minutes_played > 0
    and competition = 'Premier League' 

),


final as (

    select

        goalkeeper,
        team,
        
        -- Performance
        count(*) as matches_played,    
        sum(gk_clean_sheets) as clean_sheets,   
        sum(gk_goals_against) as ga,  
        
        -- Shot-stopping  
        sum(gk_saves) as saves,  
        sum(gk_shots_on_target_against) as shots_on_target_against,
        round(sum(gk_saves) / sum(gk_shots_on_target_against), 3) * 100 as save_pct,
        round(sum(gk_psxg) - sum(gk_goals_against), 2) as pxsg_minus_ga,
        
        -- Crossing
        round(sum(gk_crosses) / sum(minutes_played), 3) * 100 as crosses_faced_p90,
        round(sum(gk_crosses_stopped) / sum(gk_crosses), 3) * 100 as crosses_stopped_pct,  

        -- Passing
        round(sum(gk_passes) / sum(minutes_played), 3) * 100 as pass_att_p90,
        round(sum(gk_passes_completed_launched) / sum(gk_passes_launched), 3) * 100 as long_kick_pass_completion_pct,  

        -- Sweeper
        round(sum(gk_def_actions_outside_pen_area) / sum(minutes_played), 3) * 100 as def_actions_outside_pen_area_p90,
        sum(gk_def_actions_outside_pen_area * gk_avg_distance_def_actions)
        / nullif(sum(gk_def_actions_outside_pen_area), 0)
            as avg_distance_def_actions

    from base

    group by
        goalkeeper,
        team

    order by
        matches_played desc,
        clean_sheets desc
)

select * from final
