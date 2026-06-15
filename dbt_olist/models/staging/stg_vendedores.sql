with fuente as (
    select * from {{ source('raw', 'vendedores') }}
)

select
    id_vendedor,
    ciudad_vendedor,
    upper(estado_vendedor) as estado_vendedor
from fuente
