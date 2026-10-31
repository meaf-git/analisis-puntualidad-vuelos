import streamlit as st
from pathlib import Path
import duckdb
st.set_page_config(
    page_title="Resultados y análisis",
    page_icon="📊",
    layout="wide"
)

st.title("Resultados y análisis de la puntualidad")

st.write(
    "En esta sección se presentan los resultados correspondientes "
    "a los cinco objetivos específicos de la investigación."
)

st.caption(
    "Período de estudio: 16 de julio al 15 de agosto de 2017."
)

st.divider()
raiz = Path(__file__).resolve().parents[1]
ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"

if not ruta_base.is_file():
    st.error("No se encontró la base DuckDB.")
    st.stop()


def consultar(sql, parametros=None):
    with duckdb.connect(
        str(ruta_base),
        read_only=True
    ) as conexion:
        return conexion.execute(
            sql,
            parametros or []
        ).fetchdf()

control = consultar("""
    SELECT
        COUNT(*) AS vuelos,
        MIN(CAST(salida_prog_local AS DATE)) AS desde,
        MAX(CAST(salida_prog_local AS DATE)) AS hasta
    FROM v_analisis_vuelos_limpios
""")

if int(control.loc[0, "vuelos"]) == 0:
    st.warning("No hay vuelos en la muestra limpia.")
    st.stop()

st.caption(
    f"Muestra limpia: {int(control.loc[0, 'vuelos']):,} vuelos"
)

umbral = 0


with st.expander("Criterios del análisis", expanded=True):
    st.markdown(
        """
        - Se analizan los vuelos que completaron su recorrido:
          estado **Arrived**.
        - Se comparan los horarios programados con los reales.
        - Se considera retraso toda demora **mayor de 0 minutos** respecto al horario programado.
        - Las comparaciones por horario y día utilizan
          la salida programada local del aeropuerto de origen.
        """
    )

def resumir_por(campo):
    permitidos = {
        "franja_horaria",
        "origen",
        "destino",
        "modelo_aeronave",
        "dia_semana"
    }
    if campo not in permitidos:
        raise ValueError("Agrupación no permitida")

    return consultar(f"""
        SELECT
            {campo} AS grupo,
            COUNT(*) AS vuelos,
            SUM(CASE WHEN retraso_salida_min > ?
                THEN 1 ELSE 0 END) AS salida_retrasada,
            SUM(CASE WHEN retraso_llegada_min > ?
                THEN 1 ELSE 0 END) AS llegada_retrasada,
            AVG(CASE WHEN retraso_salida_min > ?
                THEN retraso_salida_min END) AS media_salida,
            AVG(CASE WHEN retraso_llegada_min > ?
                THEN retraso_llegada_min END) AS media_llegada
        FROM v_analisis_vuelos_limpios
        GROUP BY {campo}
        ORDER BY {campo}
    """, [umbral, umbral, umbral, umbral])

def mostrar_grupo(tabla, fase):
    tabla = tabla.copy()
    casos = fase + "_retrasada"
    media = "media_" + fase
    tabla["porcentaje"] = (
        100 * tabla[casos] / tabla["vuelos"]
    )

    st.dataframe(tabla.round(2), hide_index=True)
    st.caption("Frecuencia del retraso en porcentaje")
    st.bar_chart(
        tabla.set_index("grupo")[["porcentaje"]]
    )
    st.caption("Demora media entre retrasados en minutos")
    st.bar_chart(
        tabla.set_index("grupo")[[media]]
    )

pestanas = st.tabs(
    [
        "Objetivo 1",
        "Objetivo 2",
        "Objetivo 3",
        "Objetivo 4",
        "Objetivo 5",
    ]
)


def presentar_objetivo(titulo, objetivo, pregunta):
    st.header(titulo)
    st.write(objetivo)

    st.subheader("Pregunta de analisis")
    st.write(pregunta)


with pestanas[0]:
    presentar_objetivo(
        "Frecuencia y magnitud de los retrasos",
        (
            "Cuantificar la frecuencia y magnitud de los retrasos "
            "registrados en las salidas y llegadas de los vuelos, "
            "mediante la comparación entre los horarios programados "
            "y los horarios reales."
        ),
        "¿Cuántos vuelos se retrasaron y de cuántos minutos fueron "
        "sus retrasos de salida y llegada?"
    )
  

with pestanas[1]:
    presentar_objetivo(
        "Retrasos según el horario programado",
        (
            "Analizar la incidencia de los retrasos según el horario "
            "programado de salida, con el propósito de identificar "
            "las franjas horarias que presentan mayor frecuencia "
            "y magnitud de retrasos."
        ),
        "¿Qué franjas de salida programada presentan mayor "
        "proporción de vuelos retrasados y demoras más largas?"
    )


with pestanas[2]:
    presentar_objetivo(
        "Comparación entre aeropuertos",
        (
            "Comparar el comportamiento de los retrasos entre "
            "los diferentes aeropuertos de origen y destino, "
            "a fin de identificar diferencias en el cumplimiento "
            "de los horarios programados."
        ),
        "¿Cómo varían los retrasos de salida entre los orígenes "
        "y los retrasos de llegada entre los destinos?"
    )


with pestanas[3]:
    presentar_objetivo(
        "Comparación según la aeronave",
        (
            "Comparar la frecuencia y magnitud de los retrasos "
            "según el tipo de aeronave asignada a los vuelos, "
            "con el propósito de identificar diferencias "
            "en el cumplimiento de los horarios programados."
        ),
        "¿Qué diferencias de frecuencia y magnitud de retrasos "
        "se observan entre los modelos de aeronave?"
    )


with pestanas[4]:
    presentar_objetivo(
        "Variación según el día de la semana",
        (
            "Examinar la variación de los retrasos según el día "
            "de la semana, con el propósito de identificar patrones "
            "temporales en el cumplimiento de los horarios programados."
        ),
        "¿Cómo cambian la frecuencia y la magnitud de los retrasos "
        "según el día de salida programada?"
    )
