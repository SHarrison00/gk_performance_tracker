
with base AS (

    select

        *,

        -- Clean minutes played column
        case 
            when minutes = 'Match Report' then 0
            else cast(minutes as integer)
        end as minutes_played

    from {{ ref('stg_matchlogs__all') }}
),


final AS (

    select
        source_table,
        
        -- Extract goalkeeper and season fields from source_table 
        regexp_replace(source_table, '_[0-9]{4}_[0-9]{4}$', '') AS goalkeeper,
        regexp_extract(source_table, '([0-9]{4}_[0-9]{4})$', 1) AS season,
        
        date as match_date,
        comp as competition,    
        round,
        venue,
        result,
        team, 
        opponent,
        game_started,
        minutes_played,        
        gk_shots_on_target_against,
        gk_goals_against,
        gk_saves,
        
        -- Derive clean sheets when missing, based on minutes and goals conceded
        case 
            when gk_clean_sheets is not null then gk_clean_sheets 
            when minutes_played > 0 and gk_goals_against > 0 then 0
            when minutes_played > 0 and gk_goals_against = 0 then 1
        else gk_clean_sheets end as gk_clean_sheets,

        gk_psxg,
        gk_pens_att,
        gk_pens_allowed,
        gk_pens_saved,
        gk_pens_missed,
        gk_passes_launched,
        gk_passes_completed_launched,
        gk_passes,    
        gk_passes_throws,
        gk_passes_length_avg,
        gk_goal_kicks, 

        -- Disaggregated metric so we can aggregate launched goal kicks later
        gk_goal_kicks * gk_pct_goal_kicks_launched / 100 as gk_goal_kicks_launched,
        
        gk_goal_kick_length_avg,
        gk_crosses,
        gk_crosses_stopped,
        gk_def_actions_outside_pen_area,
        gk_avg_distance_def_actions

    from base
)

select * from final
