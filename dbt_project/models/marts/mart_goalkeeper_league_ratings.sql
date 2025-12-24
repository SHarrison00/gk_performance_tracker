{{ config(materialized='table') }}

with keepers as (

  select

      goalkeeper,
      team,

      -- Core metrics
      save_pct,
      pxsg_minus_ga,
      crosses_stopped_pct,
      pass_att_p90,
      long_kick_pass_completion_pct,
      def_actions_outside_pen_area_p90

  from {{ ref('fct_goalkeeper_performance') }}
  -- Exclude low-sample noise
  where matches_played >= 5
),


league_stats as (

  select
      -- League metric means
      avg(save_pct) as mean_save_pct,
      avg(pxsg_minus_ga) as mean_pxsg_minus_ga,
      avg(crosses_stopped_pct) as mean_crosses_stopped_pct,
      avg(pass_att_p90) as mean_pass_att_p90,
      avg(long_kick_pass_completion_pct) as mean_long_kick_pass_completion_pct,
      avg(def_actions_outside_pen_area_p90) as mean_def_actions_outside_pen_area_p90,

      -- League metric standard deviations
      stddev_pop(save_pct) as stddev_save_pct,
      stddev_pop(pxsg_minus_ga) as stddev_pxsg_minus_ga,
      stddev_pop(crosses_stopped_pct) as stddev_crosses_stopped_pct,
      stddev_pop(pass_att_p90) as stddev_pass_att_p90,
      stddev_pop(long_kick_pass_completion_pct) as stddev_long_kick_pass_completion_pct,
      stddev_pop(def_actions_outside_pen_area_p90) as stddev_def_actions_outside_pen_area_p90

  from keepers
),


keepers_normalised as (

  select

      k.goalkeeper,
      k.team,

      -- Raw metrics
      k.save_pct,
      k.pxsg_minus_ga,
      k.crosses_stopped_pct,
      k.pass_att_p90,
      k.long_kick_pass_completion_pct,
      k.def_actions_outside_pen_area_p90,

      -- Z-scores (league-relative)
      (k.save_pct - l.mean_save_pct) / nullif(l.stddev_save_pct, 0) as z_save_pct,
      (k.pxsg_minus_ga - l.mean_pxsg_minus_ga) / nullif(l.stddev_pxsg_minus_ga, 0) as z_pxsg_minus_ga,
      (k.crosses_stopped_pct - l.mean_crosses_stopped_pct) / nullif(l.stddev_crosses_stopped_pct, 0) as z_crosses_stopped_pct,
      (k.pass_att_p90 - l.mean_pass_att_p90) / nullif(l.stddev_pass_att_p90, 0) as z_pass_att_p90,
      (k.long_kick_pass_completion_pct - l.mean_long_kick_pass_completion_pct) / nullif(l.stddev_long_kick_pass_completion_pct, 0) as z_long_kick_pass_completion_pct,
      (k.def_actions_outside_pen_area_p90 - l.mean_def_actions_outside_pen_area_p90) / nullif(l.stddev_def_actions_outside_pen_area_p90, 0) as z_def_actions_outside_pen_area_p90,

      -- Percentiles (league-relative)
      percent_rank() over (order by k.save_pct) * 100 as pct_save_pct,
      percent_rank() over (order by k.pxsg_minus_ga) * 100 as pct_pxsg_minus_ga,
      percent_rank() over (order by k.crosses_stopped_pct) * 100 as pct_crosses_stopped_pct,
      percent_rank() over (order by k.pass_att_p90) * 100 as pct_pass_att_p90,
      percent_rank() over (order by k.long_kick_pass_completion_pct) * 100 as pct_long_kick_pass_completion_pct,
      percent_rank() over (order by k.def_actions_outside_pen_area_p90) * 100 as pct_def_actions_outside_pen_area_p90

  from keepers k
  cross join league_stats l
),


keepers_scored as (

  select

      k.*,

    -- Composite performance is a weighted sum of league-standardised metrics, 
    -- with approximately 45% emphasis on shot-stopping outcomes, 20% on box 
    -- command, and 30% on distribution and sweeping actions.        
    (0.20 * z_save_pct)
    + (0.25 * z_pxsg_minus_ga)
    + (0.20 * z_crosses_stopped_pct)
    + (0.10 * z_pass_att_p90)
    + (0.10 * z_long_kick_pass_completion_pct)
    + (0.10 * z_def_actions_outside_pen_area_p90)
    as overall_score

  from keepers_normalised k
),


final as (

  select

      *,

      -- Rank goalkeepers based on composite performance metric
      rank() over (order by overall_score desc) as overall_rank

  from keepers_scored
)

select * from final
