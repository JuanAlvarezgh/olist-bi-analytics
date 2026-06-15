select
    id_producto,
    categoria,
    peso_g
from {{ ref('stg_productos') }}
