import streamlit as st

st.set_page_config(page_title="Planteamiento del Problema", page_icon="➕", layout="wide")
##############################################################################################
### PLANTEAMIENTO DEL PROBLEMA ###
st.title("Planteamiento del Problema")
st.markdown(""" 
​​A nivel mundial, la aviación comercial es la columna vertebral del transporte, donde la puntualidad es uno de los indicadores de desempeño más importantes para la logística, los costos de las aerolíneas y la fluidez del tránsito aéreo. A su vez, la red de aeropuertos de la Federación Rusa demanda una sincronización precisa para conectar múltiples zonas y, durante el período comprendido entre el 16 de julio y el 17 de agosto de 2017, este sistema aeroportuario gestionó un volumen alto de operaciones.

A pesar de la planificación de los itinerarios, se observan desviaciones constantes entre los horarios de salida y llegada programados frente a los horarios reales, lo que se traduce en una acumulación de retrasos que no se distribuye de manera correcta.
""", unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### JUSTIFICACION ###
st.subheader("1.1 Justificación")
st.markdown("""
El estudio de la puntualidad en el transporte aéreo es relevante debido a que es indicador clave que afecta al tránsito aéreo, la rentabilidad de las aerolíneas y la eficiencia en todo el sistema de aviación. En la actualidad, los pasajeros están dispuestos a pagar más por volar con aerolíneas que tienen un mejor historial de puntualidad. Dichas aerolíneas suelen tener márgenes de ganancias operativas superiores. Cada punto de mejora se traduce en millones de dólares de ahorro, ya que se reducen los costos asociados a los retrasos (como compensaciones a pasajeros, combustible extra y horas de tripulación) y se optimiza el uso de los aviones.

Desde una perspectiva académica, resulta significativo analizar cómo diversos factores influyen en las salidas y llegadas de los vuelos, mediante el uso de herramientas de análisis estadístico y modelado de datos que permitan identificar patrones, tendencias y correlaciones entre variables asociadas. Al cruzar variables temporales (día, hora) y operacionales (tipo de aeronave, aeropuertos de origen/destino), la investigación no solo describe el fenómeno, sino que generará información accionable. Este tipo de análisis puede contribuir a identificar áreas de alta incidencia geográfica y franjas horarias críticas, así como a generar conclusiones sobre futuras estrategias de optimización de la puntualidad, reducción de costos y mejora de la experiencia del pasajero en el sector aeronáutico.
""", unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### OBJETIVOS ###
st.subheader("1.2 Objetivos")

with st.expander("1.2.1 Objetivo general", expanded=False):
    st.markdown("""
     Evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017, mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales.
    """, unsafe_allow_html=True)

with st.expander("1.2.2 Objetivos específicos", expanded=False):
    st.markdown("""
    * Cuantificar la frecuencia y magnitud de los retrasos registrados en las salidas y llegadas de los vuelos, mediante la comparación entre los horarios programados y los horarios reales.

    * Analizar la incidencia de los retrasos según el horario programado de salida, con el propósito de identificar las franjas horarias que presentan mayor frecuencia y magnitud de retrasos.

    * Comparar el comportamiento de los retrasos entre los diferentes aeropuertos de origen y destino, a fin de identificar diferencias en el cumplimiento de los horarios programados.

    * Comparar la frecuencia y magnitud de los retrasos según el tipo de aeronave asignada a los vuelos, con el propósito de identificar diferencias en el cumplimiento de los horarios programados.

    * Examinar la variación de los retrasos según el día de la semana, con el propósito de identificar patrones temporales en el cumplimiento de los horarios programados.
    """, unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### VARIABLES ###
st.subheader("1.3 Variables de estudio")
st.markdown("""
variables de estudio
""", unsafe_allow_html=True)
##############################################################################################