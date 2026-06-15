with limites as (
    select
        date_trunc('day', min(fecha_compra)) as dia_inicio,
        date_trunc('day', max(fecha_compra)) as dia_fin
    from {{ ref('stg_ordenes') }}
    where fecha_compra is not null
),
columna as (
    select generate_series(dia_inicio, dia_fin, interval '1 day')::date as dia
    from limites
)

select
    dia,
    extract(year from dia)::int                 as anio,
    extract(month from dia)::int                as mes,
    extract(quarter from dia)::int              as trimestre,
    trim(to_char(dia, 'Day'))                   as dia_semana
from columna
