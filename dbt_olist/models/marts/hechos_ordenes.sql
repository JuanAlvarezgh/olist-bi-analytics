with ordenes as (
    select * from {{ ref('stg_ordenes') }}
),
clientes as (
    select id_cliente from {{ ref('dim_clientes') }}
),
agg_items as (
    select
        id_orden,
        sum(precio)       as ingresos,
        sum(valor_flete)  as flete,
        count(*)          as cantidad_items
    from {{ ref('stg_items_orden') }}
    group by id_orden
),
agg_pagos as (
    select
        id_orden,
        sum(valor_pago)                                       as valor_pago,
        mode() within group (order by cuotas)                 as cuotas,
        mode() within group (order by tipo_pago)              as tipo_pago
    from {{ ref('stg_pagos') }}
    group by id_orden
),
agg_resenas as (
    select
        id_orden,
        avg(puntaje) as puntaje_promedio
    from {{ ref('stg_resenas') }}
    group by id_orden
)

select
    o.id_orden,
    o.id_cliente,
    o.fecha_compra::date                                                        as fecha_compra,
    o.estado_orden,
    coalesce(i.ingresos, 0)                                                     as ingresos,
    coalesce(i.flete, 0)                                                        as flete,
    coalesce(i.cantidad_items, 0)                                               as cantidad_items,
    coalesce(p.valor_pago, 0)                                                   as valor_pago,
    p.tipo_pago,
    coalesce(p.cuotas, 0)                                                       as cuotas,
    r.puntaje_promedio,
    case
        when o.fecha_entrega is not null and o.fecha_compra is not null
        then date_part('day', o.fecha_entrega - o.fecha_compra)::int
    end as dias_entrega,
    case
        when o.fecha_estimada is not null and o.fecha_compra is not null
        then date_part('day', o.fecha_estimada - o.fecha_compra)::int
    end as dias_estimados,
    case
        when o.fecha_entrega is not null and o.fecha_estimada is not null
        then (o.fecha_entrega <= o.fecha_estimada)
    end as a_tiempo
from ordenes o
inner join clientes c on c.id_cliente = o.id_cliente
left join agg_items i on i.id_orden = o.id_orden
left join agg_pagos p on p.id_orden = o.id_orden
left join agg_resenas r on r.id_orden = o.id_orden
