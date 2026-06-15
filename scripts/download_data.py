from __future__ import annotations

import sys
from pathlib import Path

import requests

BASE = "https://raw.githubusercontent.com/Ganesh7699/Brazilian-E-Commerce-OList/main"
ARCHIVOS = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "product_category_name_translation.csv",
]
DIR_DATOS = Path(__file__).resolve().parent.parent / "data"


def descargar(destino: Path = DIR_DATOS) -> None:
    """Descarga los CSV de Olist al directorio destino si no existen."""
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in ARCHIVOS:
        salida = destino / nombre
        if salida.exists() and salida.stat().st_size > 0:
            print(f"omitiendo {nombre} (ya existe)")
            continue
        url = f"{BASE}/{nombre}"
        print(f"descargando {nombre} ...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        salida.write_bytes(resp.content)
        print(f"  guardados {salida.stat().st_size:,} bytes")


if __name__ == "__main__":
    descargar(Path(sys.argv[1]) if len(sys.argv) > 1 else DIR_DATOS)
