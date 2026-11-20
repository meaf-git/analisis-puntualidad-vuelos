from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Conclusiones", page_icon="🎉", layout="wide")

# ==============================================================================
# CSS UNIFICADO CON APP.PY
# ==============================================================================
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
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarNav"] span {
        display: none !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        display: inline !important;
    }
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
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
    section[data-testid="stSidebar"]:not(:hover)::before {
        content: "";
        display: block;
        width: 34px;
        height: 34px;
        margin: 20px auto 0 auto;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F4D03F'%3E%3Cpath d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E");
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL INFERIOR (UNIFICADA CON APP.PY)
# ==============================================================================
st.sidebar.divider()
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; padding: 6px 0 10px 0;">
    <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="#F4D03F">
        <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
    </svg>
    <span style="font-size: 20px; font-weight: 700; color: #F8FAFC;">Proyecto de computación</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption("Hallazgos y conclusiones operativas")

# ==============================================================================
# CONSULTA A LA BASE DE DATOS
# ==============================================================================
raiz = Path(__file__).resolve().parents[1]
ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"
if not ruta_base.is_file():
    ruta_base = raiz / "denormalizacion_vuelos.duckdb"

try:
    if not ruta_base.is_file():
        raise FileNotFoundError(f"No se encontró {ruta_base.name}")

    with duckdb.connect(str(ruta_base), read_only=True) as conexion:
        df_top_aero = conexion.execute(
            "SELECT * FROM lim_vuelos LIMIT 50000"
        ).fetchdf()

except (OSError, duckdb.Error) as error:
    st.error(f"No se pudo consultar la base de datos: {error}")
    st.stop()

# ==============================================================================
# CONTENIDO PRINCIPAL: CUELLOS DE BOTELLA POR VOLUMEN OPERATIVO
# ==============================================================================
st.title("Conclusiones")
st.caption("Comparativa de cuellos de botella según el volumen mínimo de operaciones por terminal.")

st.divider()
st.subheader("Cuellos de botella: Top 10 aeropuertos con mayor demora")
st.write(
    "Evaluación del retraso promedio en salida comparando todas las terminales "
    "frente a aeropuertos con flujo medio (≥ 50 vuelos) y alto tráfico (≥ 100 vuelos)."
)

col_origen = next(
    (c for c in df_top_aero.columns if "origen" in c.lower() or "departure_airport" in c.lower() or "salida_aero" in c.lower()),
    df_top_aero.columns[0]
)

df_top_aero["demora_calc"] = (
    pd.to_datetime(df_top_aero["salida_real"]) - pd.to_datetime(df_top_aero["salida_programada"])
).dt.total_seconds() / 60.0

resumen_aero = (
    df_top_aero.groupby(col_origen, as_index=False)
    .agg(demora_promedio=("demora_calc", "mean"), total_vuelos=("demora_calc", "count"))
)


def renderizar_top_aeropuertos(titulo_bloque, subtitulo_bloque, min_vuelos, key_chart):
    st.markdown(f"#### {titulo_bloque}")
    st.caption(subtitulo_bloque)

    ranking = (
        resumen_aero[resumen_aero["total_vuelos"] >= min_vuelos]
        .sort_values("demora_promedio", ascending=False)
        .head(10)
        .copy()
    )
    ranking["demora_promedio"] = ranking["demora_promedio"].round(1)

    if ranking.empty:
        st.info(f"No hay aeropuertos con al menos {min_vuelos} vuelos en el conjunto de datos.")
        return

    peor_aero = ranking.iloc[0][col_origen]
    peor_demora = ranking.iloc[0]["demora_promedio"]
    peor_vuelos = int(ranking.iloc[0]["total_vuelos"])

    st.warning(
        f"⚠️ **Alerta de congestión:** El aeropuerto **{peor_aero}** lidera las demoras "
        f"con un promedio de **{peor_demora} min** por salida ({peor_vuelos:,} vuelos)."
    )

    fig_barras = px.bar(
        ranking.sort_values("demora_promedio", ascending=True),
        x="demora_promedio",
        y=col_origen,
        orientation="h",
        text="demora_promedio",
        color="demora_promedio",
        color_continuous_scale="OrRd",
        hover_data={"total_vuelos": ":,"},
        labels={
            "demora_promedio": "Demora promedio (min)",
            col_origen: "Aeropuerto",
            "total_vuelos": "Vuelos analizados"
        }
    )
    fig_barras.update_traces(texttemplate="%{text} min", textposition="outside")
    fig_barras.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=45, t=10, b=10),
        height=380,
        xaxis_title="Minutos promedio de retraso",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_barras, use_container_width=True, key=key_chart)


# 1. Sin restricción de vuelos (todos los aeropuertos)
renderizar_top_aeropuertos(
    "1. Panorama general (sin mínimo de vuelos)",
    "Terminales con el promedio más alto de minutos de retraso en salida considerando toda la red.",
    min_vuelos=1,
    key_chart="top_aero_todos"
)

st.divider()

# 2. Mínimo 50 vuelos
renderizar_top_aeropuertos(
    "2. Terminales de flujo medio (mínimo 50 vuelos)",
    "Terminales con el promedio más alto de minutos de retraso en salida (mínimo 50 vuelos).",
    min_vuelos=50,
    key_chart="top_aero_50"
)

st.divider()

# 3. Mínimo 100 vuelos
renderizar_top_aeropuertos(
    "3. Terminales de alto tráfico (mínimo 100 vuelos)",
    "Terminales con el promedio más alto de minutos de retraso en salida (mínimo 100 vuelos).",
    min_vuelos=100,
    key_chart="top_aero_100"
)