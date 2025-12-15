{% macro get_table_names(schema_name) %}
  {% if execute %}
    {% set q %}
      select table_name
      from information_schema.tables
      where table_schema = '{{ schema_name }}'
        and table_type = 'BASE TABLE'
      order by table_name
    {% endset %}

    {% set res = run_query(q) %}
    {% set names = res.columns[0].values() %}
    {{ return(names) }}
  {% else %}
    {{ return([]) }}
  {% endif %}
{% endmacro %}
