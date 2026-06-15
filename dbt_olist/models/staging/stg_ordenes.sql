with fuente as (
    select * from {{ source('raw', 'ordenes') }}
)

select
    id_orden,
    id_cliente,
    estado_orden,
    nullif(fecha_compra, '')::timestamp              as fecha_compra,
    nullif(fecha_entrega_cliente, '')::timestamp     as fecha_entrega,
    nullif(fecha_estimada_entrega, '')::timestamp    as fecha_estimada
from fuente
