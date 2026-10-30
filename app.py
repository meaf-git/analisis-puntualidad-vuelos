from pathlib import Path
import sqlite3
import streamlit as st

from Base_de_datos.base_datos import cargar_configuracion, comprobar_base, resumen_base, muestra_vuelos

st.set_page_config(page_title="Análisis de vuelos", page_icon="✈️", layout="wide")

# ==============================================================================
# CSS DEFINITIVO: NATIVO SIN DUPLICAR, ICONOS VISIBLES Y HOVER SUAVE
# ==============================================================================
st.markdown("""
<style>
    /* 1. Eliminar botón superior nativo */
    [data-testid="collapsedControl"], button[kind="header"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Barra lateral contraída por defecto (ancho justo para los iconos) */
    section[data-testid="stSidebar"] {
        width: 75px !important;
        min-width: 75px !important;
        max-width: 75px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
    }
    
    /* 3. Expandir suavemente al hacer hover */
    section[data-testid="stSidebar"]:hover {
        width: 290px !important;
        min-width: 290px !important;
        max-width: 290px !important;
    }

    /* 4. Menú de páginas (arriba): ocultar solo el texto al contraer, manteniendo el icono visible */
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarNav"] span {
        display: none !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        display: inline !important;
    }

    /* 5. Contenido de usuario (abajo - Proyecto de computación): ocultar completo al no hacer hover */
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarUserContent"] {
        opacity: 0 !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarUserContent"] {
        opacity: 1 !important;
        visibility: visible !important;
        height: auto !important;
        transition: opacity 0.3s ease-in-out;
    }

    /* 6. Espaciado del menú de navegación */
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

raiz = Path(__file__).resolve().parent

# ==============================================================================
# BARRA LATERAL (ELEMENTOS INFERIORES: PROYECTO DE COMPUTACIÓN)
# ==============================================================================
st.sidebar.divider()
st.sidebar.title("Proyecto de computación")
seccion = st.sidebar.radio("Sección", ["Inicio", "Explorar vuelos"])
st.sidebar.caption("Análisis de horarios y retrasos")

# ==============================================================================
# CONTENIDO PRINCIPAL
# ==============================================================================
st.title("Análisis de vuelos y retrasos")
st.caption("Estudio del cumplimiento de horarios en aeropuertos de Rusia")

try:
    configuracion = cargar_configuracion(raiz)
    ruta_base = raiz / configuracion["ruta_base_datos"]
    comprobar_base(ruta_base)
except (OSError, ValueError, sqlite3.Error) as error:
    st.error(str(error))

    st.stop()

try:
    resumen = resumen_base(ruta_base)

    if seccion == "Inicio":
        st.subheader("Objetivo del panel")
        st.write(
            "Explorar los horarios programados y reales para estudiar "
            "los retrasos de salida y llegada de los vuelos."
        )
        columnas = st.columns(3)
        columnas[0].metric("Vuelos en la tabla de análisis", f"{resumen['total']:,}")
        columnas[1].metric("Vuelos aptos para analizar", f"{resumen['aptos']:,}")
        columnas[2].metric("Vuelos excluidos del análisis", f"{resumen['excluidos']:,}")
        st.write(
            "**Fechas de salida local de la muestra apta:** "
            f"{resumen['fecha_min']} a {resumen['fecha_max']}"
        )
        st.info(
        "Los vuelos excluidos se conservan en la base, pero "
        "no cumplen los requisitos de información del análisis "
        "de retrasos, como disponer de las horas necesarias "
        "para calcular la demora. "
        "Los vuelos puntuales sí forman parte del análisis "
        "y se incluyen en el total utilizado para calcular "
        "el porcentaje de vuelos con retraso."
    )
    else:
        st.subheader("Muestra de vuelos aptos")
        st.caption(
            "Primeros 100 vuelos ordenados por salida programada y número de identificación."
        )
        st.dataframe(muestra_vuelos(ruta_base), hide_index=True, width="stretch")
except sqlite3.Error as error:
    st.error(f"No se pudo consultar la base de datos: {error}")