with resenas_dedup as (
    select
        id_resena,
        id_orden,
        puntaje,
        fecha_resena,
        fecha_respuesta,
        row_number() over (partition by id_resena order by fecha_resena, id_orden) as rn
    from {{ ref('stg_resenas') }}
),
resenas as (
    select
        id_resena,
        id_orden,
        puntaje,
        fecha_resena,
        fecha_respuesta
    from resenas_dedup
    where rn = 1
),
ordenes as (
    select id_orden from {{ ref('hechos_ordenes') }}
)

select
    r.id_resena,
    r.id_orden,
    r.puntaje,
    case
        when r.fecha_respuesta is not null and r.fecha_resena is not null
        then date_part('day', r.fecha_respuesta - r.fecha_resena)::int
    end as dias_respuesta
from resenas r
inner join ordenes o on o.id_orden = r.id_orden
