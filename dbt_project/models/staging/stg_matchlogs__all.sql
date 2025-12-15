{{ config(materialized='view') }}

{% set tables = get_table_names('raw_matchlogs') %}

{% for t in tables %}
select
  '{{ t }}' as source_table,
  *
from raw_matchlogs.{{ t }}
{% if not loop.last %} union all {% endif %}
{% endfor %}