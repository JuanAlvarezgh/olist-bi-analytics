"""
Genera 6 gráficos de análisis a partir de las serving marts de Olist y los guarda como PNG.

Uso
---
    $env:WAREHOUSE_DSN = "postgresql://olist:olist@localhost:5434/olist"
    python -m analysis.make_charts
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # backend no interactivo — debe ir antes del import de pyplot

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import psycopg

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
SALIDA = Path(__file__).parent.parent / "docs" / "charts"

PALETA = [
    "#2E86AB",  # azul acero
    "#A23B72",  # ciruela
    "#F18F01",  # ámbar
    "#C73E1D",  # óxido
    "#3B1F2B",  # vino oscuro
    "#44BBA4",  # verde azulado
    "#E94F37",  # rojo-naranja
    "#393E41",  # carbón
    "#F5A623",  # dorado
    "#7B2D8B",  # morado
]

# Formateadores: separador de miles y formato BRL
_FMT_MILES = mticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
_FMT_BRL = mticker.FuncFormatter(lambda x, _: f"R${x:,.0f}")


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def consultar(conexion: psycopg.Connection, sql: str) -> pd.DataFrame:
    """Ejecuta *sql* y devuelve un DataFrame (evita problemas de pandas.read_sql con psycopg3)."""
    with conexion.cursor() as cur:
        cur.execute(sql)
        columnas = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columnas)


def _guardar(fig: plt.Figure, ruta: Path) -> None:
    """Guarda la figura como PNG y cierra el objeto matplotlib."""
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  guardado {ruta.name}  ({ruta.stat().st_size / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# Gráfico 1 — Ingresos mensuales (barras) + órdenes (línea, eje secundario)
# ---------------------------------------------------------------------------

def grafico_ingresos_mensuales(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT
            date_trunc('month', fecha_compra)::date AS mes,
            SUM(ingresos) AS ingresos,
            SUM(ordenes)  AS ordenes
        FROM serving.mart_ventas_diarias
        GROUP BY 1
        ORDER BY 1
        """,
    )
    df["mes"] = pd.to_datetime(df["mes"])
    df["ingresos"] = df["ingresos"].astype(float)
    df["ordenes"] = df["ordenes"].astype(float)

    fig, eje1 = plt.subplots(figsize=(12, 5))
    eje2 = eje1.twinx()

    barras = eje1.bar(df["mes"], df["ingresos"], width=25, color=PALETA[0], alpha=0.85,
                      label="Ingresos (BRL)")
    linea = eje2.plot(df["mes"], df["ordenes"], color=PALETA[2], linewidth=2.5, marker="o",
                      markersize=4, label="Órdenes entregadas")

    eje1.set_xlabel("Mes")
    eje1.set_ylabel("Ingresos (BRL)")
    eje2.set_ylabel("Órdenes entregadas")
    eje1.yaxis.set_major_formatter(_FMT_BRL)
    eje2.yaxis.set_major_formatter(_FMT_MILES)
    eje1.set_title("Ingresos y órdenes mensuales (entregadas)", fontsize=14,
                   fontweight="bold", pad=12)

    # Leyenda combinada de ambos ejes
    identificadores = [barras, linea[0]]
    etiquetas = ["Ingresos (BRL)", "Órdenes entregadas"]
    eje1.legend(identificadores, etiquetas, loc="upper left")

    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    _guardar(fig, salida / "01_ingresos_mensuales.png")


# ---------------------------------------------------------------------------
# Gráfico 2 — Top 10 categorías por ingresos (barra horizontal)
# ---------------------------------------------------------------------------

def grafico_top_categorias(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT categoria, ingresos
        FROM serving.mart_ventas_por_categoria
        ORDER BY ingresos DESC
        LIMIT 10
        """,
    )
    df["ingresos"] = df["ingresos"].astype(float)
    df = df.sort_values("ingresos")  # ascendente para que la mayor quede arriba

    fig, eje = plt.subplots(figsize=(10, 6))
    colores = [PALETA[i % len(PALETA)] for i in range(len(df))]
    eje.barh(df["categoria"], df["ingresos"], color=colores[::-1], alpha=0.88)
    eje.xaxis.set_major_formatter(_FMT_BRL)
    eje.set_xlabel("Ingresos (BRL)")
    eje.set_title("Top 10 categorías por ingresos (BRL)", fontsize=14,
                  fontweight="bold", pad=12)
    eje.tick_params(axis="y", labelsize=9)
    fig.tight_layout()
    _guardar(fig, salida / "02_top_categorias.png")


# ---------------------------------------------------------------------------
# Gráfico 3 — Top 12 estados del cliente por ingresos (barra vertical)
# ---------------------------------------------------------------------------

def grafico_ingresos_por_estado(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT estado_cliente, SUM(ingresos) AS ingresos
        FROM serving.mart_ordenes_enriquecidas
        WHERE estado_orden = 'delivered'
        GROUP BY estado_cliente
        ORDER BY ingresos DESC
        LIMIT 12
        """,
    )
    df["ingresos"] = df["ingresos"].astype(float)

    fig, eje = plt.subplots(figsize=(11, 5))
    eje.bar(df["estado_cliente"], df["ingresos"], color=PALETA[4], alpha=0.85)
    eje.yaxis.set_major_formatter(_FMT_BRL)
    eje.set_xlabel("Estado")
    eje.set_ylabel("Ingresos (BRL)")
    eje.set_title("Ingresos por estado del cliente (top 12)", fontsize=14,
                  fontweight="bold", pad=12)
    plt.xticks(rotation=0)
    fig.tight_layout()
    _guardar(fig, salida / "03_ingresos_por_estado.png")


# ---------------------------------------------------------------------------
# Gráfico 4 — Histograma de días de entrega con línea en la mediana
# ---------------------------------------------------------------------------

def grafico_tiempo_entrega(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT dias_entrega
        FROM serving.mart_ordenes_enriquecidas
        WHERE dias_entrega IS NOT NULL
          AND dias_entrega BETWEEN 0 AND 60
        """,
    )
    df["dias_entrega"] = df["dias_entrega"].astype(float)
    mediana = df["dias_entrega"].median()

    fig, eje = plt.subplots(figsize=(10, 5))
    eje.hist(df["dias_entrega"], bins=61, range=(0, 60), color=PALETA[3], alpha=0.80,
             edgecolor="white", linewidth=0.4)
    eje.axvline(mediana, color=PALETA[2], linewidth=2.2, linestyle="--",
                label=f"Mediana: {mediana:.1f} días")
    eje.yaxis.set_major_formatter(_FMT_MILES)
    eje.set_xlabel("Días de entrega")
    eje.set_ylabel("Órdenes")
    eje.set_title("Tiempo de entrega de órdenes (días)", fontsize=14,
                  fontweight="bold", pad=12)
    eje.legend()
    fig.tight_layout()
    _guardar(fig, salida / "04_tiempo_entrega.png")
    print(f"    Mediana de días de entrega: {mediana:.1f}")


# ---------------------------------------------------------------------------
# Gráfico 5 — Distribución de puntajes de reseña
# ---------------------------------------------------------------------------

def grafico_puntajes_resena(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT puntaje, COUNT(*) AS cantidad
        FROM marts.hechos_resenas
        GROUP BY puntaje
        ORDER BY puntaje
        """,
    )
    df["puntaje"] = df["puntaje"].astype(int)
    df["cantidad"] = df["cantidad"].astype(int)

    fig, eje = plt.subplots(figsize=(8, 5))
    colores_barras = [PALETA[i] for i in range(len(df))]
    eje.bar(df["puntaje"], df["cantidad"], color=colores_barras, alpha=0.88, width=0.6)
    eje.yaxis.set_major_formatter(_FMT_MILES)
    eje.set_xlabel("Puntaje")
    eje.set_ylabel("Cantidad")
    eje.set_xticks(df["puntaje"])
    eje.set_title("Distribución de puntajes de reseña", fontsize=14,
                  fontweight="bold", pad=12)
    fig.tight_layout()
    _guardar(fig, salida / "05_distribucion_puntajes.png")


# ---------------------------------------------------------------------------
# Gráfico 6 — Órdenes por tipo de pago
# ---------------------------------------------------------------------------

def grafico_tipo_pago(conexion: psycopg.Connection, salida: Path) -> None:
    df = consultar(
        conexion,
        """
        SELECT tipo_pago, COUNT(*) AS cantidad
        FROM serving.mart_ordenes_enriquecidas
        WHERE tipo_pago IS NOT NULL
        GROUP BY tipo_pago
        ORDER BY cantidad DESC
        """,
    )
    df["tipo_pago"] = df["tipo_pago"].astype(str)
    df["cantidad"] = df["cantidad"].astype(int)

    fig, eje = plt.subplots(figsize=(9, 5))
    colores_barras = [PALETA[i % len(PALETA)] for i in range(len(df))]
    eje.bar(df["tipo_pago"], df["cantidad"], color=colores_barras, alpha=0.88)
    eje.yaxis.set_major_formatter(_FMT_MILES)
    eje.set_xlabel("Tipo de pago")
    eje.set_ylabel("Cantidad de órdenes")
    eje.set_title("Órdenes por tipo de pago", fontsize=14, fontweight="bold", pad=12)
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()
    _guardar(fig, salida / "06_ordenes_por_tipo_pago.png")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def principal(dsn: str, salida: Path) -> None:
    """Conecta al warehouse y genera los 6 gráficos PNG."""
    salida.mkdir(parents=True, exist_ok=True)
    print("Conectando al warehouse…")
    with psycopg.connect(dsn) as conexion:
        print("Generando gráficos…")
        grafico_ingresos_mensuales(conexion, salida)
        grafico_top_categorias(conexion, salida)
        grafico_ingresos_por_estado(conexion, salida)
        grafico_tiempo_entrega(conexion, salida)
        grafico_puntajes_resena(conexion, salida)
        grafico_tipo_pago(conexion, salida)
    print("Listo. Los 6 gráficos guardados en", salida)


if __name__ == "__main__":
    principal(os.environ["WAREHOUSE_DSN"], SALIDA)
