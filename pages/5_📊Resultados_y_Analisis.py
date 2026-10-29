import streamlit as st

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

with st.expander("Criterios del análisis", expanded=True):
    st.markdown(
        """
        - Se analizan los vuelos que completaron su recorrido:
          estado **Arrived**.
        - Se comparan los horarios programados con los reales.
        - Se consideran ambos criterios: retraso **mayor de 0 minutos**
          y retraso **mayor de 15 minutos**.
        - Se utiliza la llegada programada reconstruida,
          aprobada por el equipo.
        - Las comparaciones por horario y día utilizan
          la salida programada local del aeropuerto de origen.
        """
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

    st.subheader("Pregunta que responde")
    st.write(pregunta)

    st.info(
        "Estructura creada. resultados, graficas y filtros aqui"
    )


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
