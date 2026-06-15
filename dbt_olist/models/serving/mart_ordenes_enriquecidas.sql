select
    ho.id_orden,
    ho.fecha_compra,
    ho.estado_orden,
    c.id_cliente_unico,
    c.estado_cliente,
    c.ciudad_cliente,
    ho.ingresos,
    ho.flete,
    ho.cantidad_items,
    ho.valor_pago,
    ho.tipo_pago,
    ho.cuotas,
    ho.dias_entrega,
    case when ho.a_tiempo is null then null when ho.a_tiempo then 1 else 0 end as a_tiempo,
    ho.puntaje_promedio
from {{ ref('hechos_ordenes') }} ho
join {{ ref('dim_clientes') }} c on c.id_cliente = ho.id_cliente
