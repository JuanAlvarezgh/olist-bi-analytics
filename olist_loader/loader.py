from __future__ import annotations

from pathlib import Path

import psycopg

# tabla raw (esquema.tabla) -> nombre del archivo CSV fuente
TABLAS_RAW = {
    "raw.clientes":              "olist_customers_dataset.csv",
    "raw.ordenes":               "olist_orders_dataset.csv",
    "raw.items_orden":           "olist_order_items_dataset.csv",
    "raw.productos":             "olist_products_dataset.csv",
    "raw.vendedores":            "olist_sellers_dataset.csv",
    "raw.pagos":                 "olist_order_payments_dataset.csv",
    "raw.resenas":               "olist_order_reviews_dataset.csv",
    "raw.traduccion_categorias": "product_category_name_translation.csv",
}

# DDL de las tablas raw en español; el ORDEN de columnas coincide exactamente
# con el del CSV original para que COPY (FORMAT csv, HEADER true) funcione.
DDL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.clientes (id_cliente text, id_cliente_unico text, prefijo_cp_cliente text, ciudad_cliente text, estado_cliente text);
CREATE TABLE IF NOT EXISTS raw.ordenes (id_orden text, id_cliente text, estado_orden text, fecha_compra text, fecha_aprobacion text, fecha_entrega_transportista text, fecha_entrega_cliente text, fecha_estimada_entrega text);
CREATE TABLE IF NOT EXISTS raw.items_orden (id_orden text, id_item text, id_producto text, id_vendedor text, fecha_limite_envio text, precio text, valor_flete text);
CREATE TABLE IF NOT EXISTS raw.productos (id_producto text, categoria_pt text, largo_nombre text, largo_descripcion text, cant_fotos text, peso_g text, largo_cm text, alto_cm text, ancho_cm text);
CREATE TABLE IF NOT EXISTS raw.vendedores (id_vendedor text, prefijo_cp_vendedor text, ciudad_vendedor text, estado_vendedor text);
CREATE TABLE IF NOT EXISTS raw.pagos (id_orden text, secuencia_pago text, tipo_pago text, cuotas text, valor_pago text);
CREATE TABLE IF NOT EXISTS raw.resenas (id_resena text, id_orden text, puntaje text, titulo_comentario text, comentario text, fecha_resena text, fecha_respuesta text);
CREATE TABLE IF NOT EXISTS raw.traduccion_categorias (categoria_pt text, categoria_en text);
"""


def asegurar_esquema(conexion: psycopg.Connection) -> None:
    """Crea el esquema raw y las tablas si no existen."""
    with conexion.cursor() as cur:
        cur.execute(DDL)
    conexion.commit()


def cargar_csv(conexion: psycopg.Connection, tabla: str, ruta_csv: Path) -> int:
    """Trunca la tabla y carga el CSV completo; devuelve el conteo de filas."""
    with conexion.cursor() as cur:
        cur.execute(f"TRUNCATE {tabla}")
        with open(ruta_csv, encoding="utf-8") as f:
            with cur.copy(f"COPY {tabla} FROM STDIN WITH (FORMAT csv, HEADER true)") as cp:
                while chunk := f.read(65536):
                    cp.write(chunk)
        cur.execute(f"SELECT count(*) FROM {tabla}")
        n = cur.fetchone()[0]
    conexion.commit()
    return n
