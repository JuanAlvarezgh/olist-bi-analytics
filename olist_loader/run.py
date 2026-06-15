from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

from olist_loader.loader import TABLAS_RAW, asegurar_esquema, cargar_csv


def ejecutar(dsn: str, dir_datos: Path) -> None:
    """Conecta al warehouse, asegura el esquema raw y carga todos los CSV."""
    with psycopg.connect(dsn) as conexion:
        asegurar_esquema(conexion)
        for tabla, nombre_archivo in TABLAS_RAW.items():
            n = cargar_csv(conexion, tabla, dir_datos / nombre_archivo)
            print(f"cargadas {n} filas en {tabla}")


if __name__ == "__main__":
    directorio = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
    ejecutar(os.environ["WAREHOUSE_DSN"], directorio)
