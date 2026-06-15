select
    p.categoria,
    sum(i.precio)                      as ingresos,
    count(distinct i.id_orden)         as ordenes,
    avg(i.precio)                      as precio_promedio,
    avg(ho.puntaje_promedio)           as resena_promedio
from {{ ref('hechos_items_orden') }} i
join {{ ref('dim_productos') }} p on p.id_producto = i.id_producto
join {{ ref('hechos_ordenes') }} ho on ho.id_orden = i.id_orden
where ho.estado_orden = 'delivered'
group by p.categoria
