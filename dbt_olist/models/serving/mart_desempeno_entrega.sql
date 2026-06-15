select
    estado_cliente,
    date_trunc('month', fecha_compra)::date     as mes,
    count(*)                                    as ordenes,
    avg(dias_entrega)                           as dias_entrega_promedio,
    avg(a_tiempo::numeric)                      as tasa_a_tiempo
from {{ ref('mart_ordenes_enriquecidas') }}
where estado_orden = 'delivered'
  and dias_entrega is not null
group by estado_cliente, date_trunc('month', fecha_compra)
