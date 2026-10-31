from pathlib import Path
import duckdb
import streamlit as st


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

ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"

try:
    if not ruta_base.is_file():
        raise FileNotFoundError(f"No se encontró {ruta_base.name}")

    with duckdb.connect(str(ruta_base), read_only=True) as conexion:
        total = conexion.execute(
            "SELECT COUNT(*) FROM vuelos"
        ).fetchone()[0]

        aptos = conexion.execute(
            "SELECT COUNT(*) FROM v_analisis_vuelos_limpios"
        ).fetchone()[0]

        fecha_min, fecha_max = conexion.execute(
            "SELECT MIN(CAST(salida_prog_local AS DATE)), "
            "MAX(CAST(salida_prog_local AS DATE)) FROM lim_vuelos"
        ).fetchone()

        muestra = None
        if seccion == "Explorar vuelos":
            muestra = conexion.execute(
                "SELECT * FROM v_analisis_vuelos_limpios LIMIT 100"
            ).fetchdf()

    if aptos > total:
        raise ValueError(
            "La vista limpia contiene más registros que la tabla vuelos."
        )

except (OSError, ValueError, duckdb.Error) as error:
    st.error(f"No se pudo consultar la base de datos: {error}")
    st.stop()



if seccion == "Inicio":
    st.subheader("Objetivo del panel")
    st.write(
        "Explorar los horarios programados y reales para estudiar "
        "los retrasos de salida y llegada de los vuelos."
    )

    columnas = st.columns(3)
    columnas[0].metric("Vuelos registrados", f"{total:,}")
    columnas[1].metric("Vuelos aptos para analizar", f"{aptos:,}")
    columnas[2].metric("Vuelos excluidos del análisis", f"{total - aptos:,}")

    st.write(
        "**Fechas de salida local de la tabla limpia:** "
        f"{fecha_min or 'Sin datos'} a {fecha_max or 'Sin datos'}"
    )
    st.html("""
    <div style="background: rgba(59, 130, 246, 0.10);
                padding: 20px 24px; border-radius: 10px;">

        <p style="font-size: 18px; line-height: 1.7; margin: 0 0 16px;">
            <strong>Vuelos incluidos:</strong>
            vuelos que completaron su recorrido (estado Arrived)
            y cuentan con horarios programados y reales
            de salida y llegada.
        </p>

        <p style="font-size: 18px; line-height: 1.7; margin: 0 0 16px;">
            <strong>Vuelos excluidos:</strong>
            vuelos en otros estados o con horarios incompletos,
            porque no permiten comparar los horarios programados
            con los reales y calcular los retrasos de salida y llegada.
        </p>

        <p style="font-size: 18px; line-height: 1.7; margin: 0;">
            Los vuelos excluidos se conservan en la base de datos.
        </p>

    </div>
    """)
else:
    st.subheader("Muestra de vuelos aptos")
    st.caption("Muestra de hasta 100 registros de la vista de análisis limpia.")
    st.dataframe(muestra, hide_index=True, width="stretch")