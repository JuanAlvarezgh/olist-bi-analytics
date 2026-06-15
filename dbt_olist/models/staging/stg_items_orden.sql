with fuente as (
    select * from {{ source('raw', 'items_orden') }}
)

select
    id_orden,
    id_item::int        as id_item,
    id_producto,
    id_vendedor,
    nullif(precio, '')::numeric       as precio,
    nullif(valor_flete, '')::numeric  as valor_flete
from fuente
