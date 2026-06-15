with fuente as (
    select * from {{ source('raw', 'resenas') }}
)

select
    id_resena,
    id_orden,
    nullif(puntaje, '')::int                   as puntaje,
    nullif(fecha_resena, '')::timestamp        as fecha_resena,
    nullif(fecha_respuesta, '')::timestamp     as fecha_respuesta
from fuente
