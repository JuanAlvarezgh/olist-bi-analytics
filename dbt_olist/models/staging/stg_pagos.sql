with fuente as (
    select * from {{ source('raw', 'pagos') }}
)

select
    id_orden,
    tipo_pago,
    nullif(cuotas, '')::int          as cuotas,
    nullif(valor_pago, '')::numeric  as valor_pago
from fuente
