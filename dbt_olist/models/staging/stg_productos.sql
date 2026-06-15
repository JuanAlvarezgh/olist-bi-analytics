with fuente as (
    select
        p.id_producto,
        p.categoria_pt,
        p.peso_g,
        t.categoria_en
    from {{ source('raw', 'productos') }} p
    left join {{ source('raw', 'traduccion_categorias') }} t
        on p.categoria_pt = t.categoria_pt
)

select
    id_producto,
    coalesce(
        nullif(categoria_en, ''),
        nullif(categoria_pt, ''),
        'unknown'
    ) as categoria,
    nullif(peso_g, '')::numeric as peso_g
from fuente
