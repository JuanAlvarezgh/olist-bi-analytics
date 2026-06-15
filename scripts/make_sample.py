from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
SAMPLE = Path(__file__).resolve().parent.parent / "sample"
N_ORDENES = 40


def leer(nombre: str) -> list[dict]:
    """Lee un CSV del directorio de datos y devuelve una lista de dicts."""
    with open(DATA / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(nombre: str, filas: list[dict]) -> None:
    """Escribe las filas en un CSV dentro del directorio sample."""
    SAMPLE.mkdir(exist_ok=True)
    campos = list(filas[0].keys())
    with open(SAMPLE / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    print(f"{nombre}: {len(filas)} filas")


def principal() -> None:
    # Prioriza órdenes entregadas para que el sample ejercite métricas de entrega.
    todas_ordenes = leer("olist_orders_dataset.csv")
    entregadas = [o for o in todas_ordenes if o["order_status"] == "delivered"]
    ordenes = (entregadas or todas_ordenes)[:N_ORDENES]
    # Claves de CSV en inglés: son los encabezados reales del archivo fuente
    ids_orden = {o["order_id"] for o in ordenes}
    ids_cliente = {o["customer_id"] for o in ordenes}

    clientes = [c for c in leer("olist_customers_dataset.csv") if c["customer_id"] in ids_cliente]
    items = [i for i in leer("olist_order_items_dataset.csv") if i["order_id"] in ids_orden]
    ids_producto = {i["product_id"] for i in items}
    ids_vendedor = {i["seller_id"] for i in items}
    productos = [p for p in leer("olist_products_dataset.csv") if p["product_id"] in ids_producto]
    vendedores = [s for s in leer("olist_sellers_dataset.csv") if s["seller_id"] in ids_vendedor]
    pagos = [p for p in leer("olist_order_payments_dataset.csv") if p["order_id"] in ids_orden]
    resenas = [r for r in leer("olist_order_reviews_dataset.csv") if r["order_id"] in ids_orden]
    cats = leer("product_category_name_translation.csv")

    escribir("olist_orders_dataset.csv", ordenes)
    escribir("olist_customers_dataset.csv", clientes)
    escribir("olist_order_items_dataset.csv", items)
    escribir("olist_products_dataset.csv", productos)
    escribir("olist_sellers_dataset.csv", vendedores)
    escribir("olist_order_payments_dataset.csv", pagos)
    escribir("olist_order_reviews_dataset.csv", resenas)
    escribir("product_category_name_translation.csv", cats)


if __name__ == "__main__":
    principal()
