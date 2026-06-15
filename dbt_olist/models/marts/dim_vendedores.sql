select
    id_vendedor,
    ciudad_vendedor,
    estado_vendedor
from {{ ref('stg_vendedores') }}
