select
    id_cliente,
    id_cliente_unico,
    ciudad_cliente,
    estado_cliente
from {{ ref('stg_clientes') }}
