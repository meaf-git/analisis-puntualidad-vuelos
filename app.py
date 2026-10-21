from pathlib import Path
import sqlite3

import streamlit as st

from Base_de_datos.base_datos import cargar_configuracion, comprobar_base, resumen_base, muestra_vuelos


st.set_page_config(page_title="Análisis de vuelos", page_icon="✈️", layout="wide")

raiz = Path(__file__).resolve().parent
st.sidebar.title("Proyecto de computación")
seccion = st.sidebar.radio("Sección", ["Inicio", "Explorar vuelos"])
st.sidebar.caption("Análisis de horarios y retrasos")

st.title("Análisis de vuelos y retrasos")
st.caption("Estudio del cumplimiento de horarios en aeropuertos de Rusia")

try:
    configuracion = cargar_configuracion(raiz)
    ruta_base = raiz / configuracion["ruta_base_datos"]
    comprobar_base(ruta_base)
except (OSError, ValueError, sqlite3.Error) as error:
    st.error(str(error))
    st.info(
        "Descomprime Limpieza_retrasos.sqlite.zip y coloca "
        "Eduardo_limpieza_retrasos.sqlite dentro de la carpeta data. "
        "Si tu archivo tiene otro nombre, ajusta .config/settings.json."
    )
    st.stop()

try:
    resumen = resumen_base(ruta_base)
    st.sidebar.success("Base de datos conectada")

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
            "La muestra utiliza la vista vw_muestra_retrasos, que selecciona "
            "apto_analisis = 1. Los vuelos excluidos no entran en el análisis "
            "de retrasos; siguen conservados en la base."
        )
        st.subheader("Contenido que agregaremos")
        st.markdown(
            "- Filtros por fecha, aeropuerto y aeronave.\n"
            "- Indicadores de retrasos de salida y llegada.\n"
            "- Gráficos por aeropuerto, día de la semana y hora local.\n"
            "- Explicación de la preparación y de los límites de los datos."
        )
    else:
        st.subheader("Muestra de vuelos aptos")
        st.caption(
            "Primeros 100 vuelos ordenados por salida programada y número de identificación. "
            "Esta muestra sirve para comprobar la lectura de la base. "
            "Los retrasos están expresados en minutos."
        )
        st.dataframe(muestra_vuelos(ruta_base), hide_index=True, width="stretch")
except sqlite3.Error as error:
    st.error(f"No se pudo consultar la base de datos: {error}")

