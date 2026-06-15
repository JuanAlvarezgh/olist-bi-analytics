import os
from pathlib import Path

import psycopg
import pytest

from olist_loader.loader import TABLAS_RAW, asegurar_esquema, cargar_csv

DSN = os.environ.get("WAREHOUSE_DSN")
SAMPLE = Path(__file__).resolve().parent.parent / "sample"
pytestmark = pytest.mark.skipif(not DSN, reason="WAREHOUSE_DSN no configurado")


@pytest.fixture
def conexion():
    """Conexion al warehouse con esquema raw garantizado."""
    with psycopg.connect(DSN) as c:
        asegurar_esquema(c)
        yield c


def _conteos(conexion):
    """Devuelve un dict {tabla: conteo_filas} para todas las tablas raw."""
    resultado = {}
    with conexion.cursor() as cur:
        for tabla in TABLAS_RAW:
            cur.execute(f"SELECT count(*) FROM {tabla}")
            resultado[tabla] = cur.fetchone()[0]
    return resultado


def test_carga_sample_es_idempotente(conexion):
    """Cargar el sample dos veces produce los mismos conteos."""
    for tabla, nombre_archivo in TABLAS_RAW.items():
        cargar_csv(conexion, tabla, SAMPLE / nombre_archivo)
    conteos1 = _conteos(conexion)
    for tabla, nombre_archivo in TABLAS_RAW.items():
        cargar_csv(conexion, tabla, SAMPLE / nombre_archivo)
    conteos2 = _conteos(conexion)
    assert conteos1 == conteos2
    assert conteos1["raw.ordenes"] == 40
    assert conteos1["raw.items_orden"] >= 40
