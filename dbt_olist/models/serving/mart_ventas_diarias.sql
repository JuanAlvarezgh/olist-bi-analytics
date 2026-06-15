select
    fecha_compra,
    count(*)                                    as ordenes,
    sum(ingresos)                               as ingresos,
    sum(flete)                                  as flete,
    sum(cantidad_items)                         as cantidad_items,
    sum(ingresos) / nullif(count(*), 0)         as ticket_promedio
from {{ ref('hechos_ordenes') }}
where estado_orden = 'delivered'
group by fecha_compra
