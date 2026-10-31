import streamlit as st
import sqlite3
import pandas as pd 
from pathlib import Path 
from urllib.request import urlretrieve

st.markdown("""
<style>
    [data-testid="collapsedControl"], button[kind="header"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    section[data-testid="stSidebar"] {
        width: 75px !important;
        min-width: 75px !important;
        max-width: 75px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
    }
    section[data-testid="stSidebar"]:hover {
        width: 290px !important;
        min-width: 290px !important;
        max-width: 290px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {
        visibility: hidden;
        opacity: 0;
        transition: visibility 0.2s, opacity 0.2s ease-in-out;
        white-space: nowrap !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        visibility: visible;
        opacity: 1;
    }
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Cuestionario SQL", page_icon="🥵", layout="wide")
st.title("Cuestionario SQL")

st.header("Pregunta 2. Mayores saltos diarios de venta")

st.write(
    "Identificar los ocho dias con mayor aumento absoluto del importe total de las reservas"
    "respecto al dia calendario inmediatamente anterior, excluyendo los primeros catorce dias de la serie."
)
consulta_2 = """
WITH ventas_diarias AS (
    SELECT
        DATE(SUBSTR(book_date, 1, 19)) AS fecha,
        COUNT(*) AS reservas,
        SUM(total_amount) AS importe
    FROM bookings
    GROUP BY
        DATE(SUBSTR(book_date, 1, 19))
),
serie AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            ORDER BY fecha
        ) AS numero_dia
    FROM ventas_diarias
),
comparacion AS (
    SELECT
        actual.fecha,
        actual.reservas,
        actual.importe,
        anterior.importe AS importe_anterior,
        actual.importe - anterior.importe AS aumento
    FROM serie AS actual
    JOIN serie AS anterior
        ON anterior.fecha = DATE(actual.fecha, '-1 day')
    WHERE actual.numero_dia > 14
),
clasificacion AS (
    SELECT
        *,
        RANK() OVER (
            ORDER BY aumento DESC
        ) AS puesto_aumento,
        RANK() OVER (
            ORDER BY aumento ASC
        ) AS puesto_caida
    FROM comparacion
)
SELECT
    puesto_aumento,
    fecha,
    reservas AS cantidad_reservas,
    importe AS importe_dia,
    importe_anterior AS importe_dia_anterior,
    aumento AS aumento_absoluto,
    ROUND(
        100.0 * aumento / NULLIF(importe_anterior, 0),
        2
    ) AS variacion_porcentual,
    ROUND(
        100.0 * importe /
        NULLIF(
            (SELECT MAX(importe) FROM ventas_diarias),
            0
        ),
        2
    ) AS porcentaje_del_maximo_diario,
    puesto_caida AS puesto_ranking_caidas
FROM clasificacion
ORDER BY
    puesto_aumento,
    fecha
LIMIT 8;
"""
st.code(consulta_2, language="sql")
ruta_base = (
    Path(__file__).resolve().parent.parent
    / "Base_de_datos"
    / "travel_original.sqlite"
)

if not ruta_base.is_file():
    url_base = (
        "https://github.com/meaf-git/"
        "analisis-puntualidad-vuelos/releases/download/"
        "datos-originales-v1/travel.sqlite"
    )

    ruta_base.parent.mkdir(parents=True, exist_ok=True)
    ruta_temporal = ruta_base.with_suffix(".descarga")

    try:
        with st.spinner("Descargando la base original..."):
            urlretrieve(url_base, ruta_temporal)
            ruta_temporal.replace(ruta_base)
    except Exception as error:
        ruta_temporal.unlink(missing_ok=True)
        st.error(
            "No se pudo descargar la base original. "
            "Comprueba la conexión e inténtalo nuevamente."
        )
        st.exception(error)
        st.stop()

conexion = sqlite3.connect(
    ruta_base.as_uri() + "?mode=ro",
    uri=True
)

try:
    resultado_2 = pd.read_sql_query(consulta_2, conexion)
finally:
    conexion.close()

st.subheader("Resultados")
st.dataframe(resultado_2, hide_index=True)
st.subheader("Interpretación de los resultados")

st.write(
    "El mayor aumento se registró el 14 de julio de 2017. "
    "El importe de las reservas pasó de 432.826.700 el día "
    "anterior a 460.449.000, un aumento de 27.622.300, "
    "equivalente al 6,38 %."
)

st.write(
    "El mayor aumento diario no corresponde necesariamente "
    "al día con mayor importe de reservas. El 14 de agosto "
    "registró el importe máximo de toda la serie, con "
    "524.600.500, pero ocupa el octavo puesto por aumento."
)

st.write(
    "El puesto en el ranking de caídas se calcula entre "
    "todos los días considerados, antes de seleccionar "
    "estos ocho resultados. El puesto 1 corresponde a la "
    "mayor caída; por eso los mayores aumentos aparecen "
    "en los últimos puestos de ese ranking."
)