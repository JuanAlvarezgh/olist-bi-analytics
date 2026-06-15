with fuente as (
    select * from {{ source('raw', 'clientes') }}
)

select
    id_cliente,
    id_cliente_unico,
    ciudad_cliente,
    upper(estado_cliente) as estado_cliente
from fuente
