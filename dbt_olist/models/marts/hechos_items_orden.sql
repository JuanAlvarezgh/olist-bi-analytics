with items as (
    select * from {{ ref('stg_items_orden') }}
),
productos as (
    select id_producto from {{ ref('dim_productos') }}
),
vendedores as (
    select id_vendedor from {{ ref('dim_vendedores') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['i.id_orden', 'i.id_item']) }} as llave_item,
    i.id_orden,
    i.id_item,
    i.id_producto,
    i.id_vendedor,
    i.precio,
    i.valor_flete
from items i
inner join productos p on p.id_producto = i.id_producto
inner join vendedores v on v.id_vendedor = i.id_vendedor
