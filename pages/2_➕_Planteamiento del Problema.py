import streamlit as st

st.set_page_config(page_title="Planteamiento del Problema", page_icon="➕", layout="wide")
##############################################################################################
### PLANTEAMIENTO DEL PROBLEMA ###
st.title("Planteamiento del Problema")
st.markdown(""" 
planteamiento del problema
""", unsafe_allow_html=True)
##############################################################################################

st.divider ()

##############################################################################################
### JUSTIFICACION ###
st.subheader("1.1 Justificacion")
st.markdown("""
El estudio de la puntualidad en el transporte aéreo es relevante debido a que es un indicador 
clave que afecta al tránsito aéreo, la rentabilidad de las aerolíneas y la eficiencia en todo 
el sistema de aviación. En la actualidad, los estudios demuestran que los pasajeros están dispuestos 
a pagar más por volar con aerolíneas que tienen un mejor historial de puntualidad. Por ejemplo, Zhang (2012) encontró que un pasajero promedio está dispuesto a pagar hasta 1.56 dólares por 
cada minuto de retraso evitado. Las aerolíneas más puntuales suelen tener márgenes de ganancias operativas superiores. 
Cada punto de mejora se traduce en millones de dólares de ahorro, ya que se reducen los costos asociados a los retrasos 
(como compensaciones a pasajeros, combustible extra y horas de tripulación) y se optimiza el uso de los aviones.

Desde una perspectiva académica, resulta significativo analizar cómo diversos factores influyen en las salidas y llegadas de 
los vuelos, mediante el uso de herramientas de análisis estadístico y modelado de datos que permitan identificar patrones, 
tendencias y correlaciones entre variables asociadas. Al cruzar variables temporales (día, hora) y operacionales (tipo de aeronave, aeropuertos de origen/destino), 
la investigación no solo describe el fenómeno, sino que generará información accionable. Este tipo de análisis puede contribuir a identificar áreas de alta incidencia 
geográfica y franjas horarias críticas, así como a generar conclusiones sobre futuras estrategias de optimización de la puntualidad, reducción de costos y mejora de la experiencia del pasajero en el sector aeronáutico.

""", unsafe_allow_html=True)
##############################################################################################

st.divider ()

##############################################################################################
### OBJETIVOS ###
st.subheader("1.2 Objetivos")

with st.expander("**1.2.1 Objetivos generales**", expanded=True):
    st.markdown("""
     1. Evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en 
     los aeropuertos rusos durante el período comprendido entre el xs de julio y el xs de agosto de 2017, 
     mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales.
    """, unsafe_allow_html=True)

with st.expander("**1.2.2 Objetivos específicos**", expanded=False):
    st.markdown("""
     1. Cuantificar la frecuencia y magnitud de los retrasos registrados en las salidas y llegadas de los vuelos, 
    mediante la comparación entre los horarios programados y los horarios reales

    2. Analizar la incidencia de los retrasos según el horario programado de salida, con el propósito de identificar 
    las franjas horarias que presentan mayor frecuencia y magnitud de retrasos.

    3. Comparar el comportamiento de los retrasos entre los diferentes aeropuertos de origen y destino, a fin de 
    identificar diferencias en el cumplimiento de los horarios programados.

    4. Comparar la frecuencia y magnitud de los retrasos según el tipo de aeronave asignada a los vuelos, con el 
    propósito de identificar diferencias en el cumplimiento de los horarios programados.

    5. Determinar la variación de los retrasos según el día de la semana, con el propósito de identificar patrones 
    temporales en el cumplimiento de los horarios programados.
    """, unsafe_allow_html=True)
##############################################################################################

st.divider ()

##############################################################################################
### VARIABLES ###
st.subheader("1.3 Variables de estudio")
st.markdown("""
variables de estudio
""", unsafe_allow_html=True)
##############################################################################################

st.divider ()

###########################################################################################
########## PERIODO DE REFERENCIA (CON CUADRO BONITO) ##########

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 2px solid #64b5f6;
        border-radius: 12px;
        padding: 24px;                     
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
    ">
        <h6 style="color: #0d47a1; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; font-weight: 700;">
            PERIODO DE REFERENCIA 
        </h6>
        <p style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin: 0;">
        La población objetivo del estudio está conformada por todos los vuelos comerciales registrados en la base de datos travel.sqlite, la cual contiene un total de 33.121 registros en la tabla principal Flights. El periodo de referencia de este análisis se encuentra entre 16 de julio al 15 de agosto del 2017. 
        La muestra utilizada se centrará únicamente en los vuelos que completaron su itinerario, es decir, aquellos cuyo campo status sea Arrived. Conservando un total de 16.707 registros que contienen información detallada sobre:
        </p> 
        <ul style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin-bottom: 12px; padding-left: 20px;">
            <li style="margin-bottom: 8px;"><b>Variables temporales:</b> 
            extraídas de los campos scheduled_departure, actual_departure, scheduled_arrival y actual_arrival.
            </li>
            <li><b>Variables operacionales:</b> 
            obtenidas mediante la relación de la tabla flights con airports_data (para origen y destino: departure_airport, arrival_airport, airport_name, city) y con aircrafts_data (para el tipo de aeronave: aircraft_code, model).
            </li>
        </ul>
        <p style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin: 0;">
            De este estudio se excluyen los 8 vuelos que no registraron su llegada, es decir que se encuentran en el estatus de Cancelled, ya que estos vuelos no presentan tiempos reales de operación y su inclusión causaria sesgo en el cálculo de los retrasos.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
##############################################################################################################

st.divider ()

##############################################################################################################
st.subheader("1. Universo y Unidad de Análisis")

col_kobe, col_lebron = st.columns(2)
###########################################################################################
#### LADO IZQUIERDO ####    
with col_kobe:
    st.markdown("#### **• Universo de programación:**")
    st.markdown("""
     Está conformado por todos los vuelos comerciales registrados en la base de datos Travel.sqlite, la cual está constituida por un total de 33.121 registros de vuelos.
    """, unsafe_allow_html=True)

    st.markdown("#### **• Universo de operación:**")
    st.markdown("""
    El estudio se focaliza en la muestra de 16.707 vuelos que se iniciaron y finalizaron su ruta filtrados por el estado de Arrived. Y que cuentan con datos reales de despegue 
    y aterrizaje (actual_departure y actual_arrival). 
    
    Se excluyeron 8 registros cuyo estatus es "Cancelled", dado que no cuentan con horas reales de operación.  El periodo de referencia de este análisis se encuentra entre el 16 de julio y el 15 de agosto de 2017.
    """, unsafe_allow_html=True)

############################################################################################
#### LADO DERECHO ####

with col_lebron:
    
    st.markdown("#### **• Unidad de análisis:**")
    st.markdown("""
    La unidad mínima de observación es cada vuelo en particular. Cada uno de estos registros es único e irrepetible, 
    y puede ser rastreado de manera inequívoca a través de su identificador primario (flight_id) dentro de la base de datos. 
    """, unsafe_allow_html=True)
    
    st.markdown("#### **• Técnicas:**")
    st.markdown("""
    Para el procesamiento de los datos, se emplearon diversas medidas descriptivas que permiten caracterizar el comportamiento 
    de la muestra en estudio. 

    Se utilizarán tablas de frecuencias absolutas y relativas para estudiar variables categóricas (como el día de la semana o los aeropuertos); medidas de resumen (media, mediana, desviación estándar) para cuantificar en 
    minutos la magnitud de los retrasos; y segmentaciones agrupadas para contrastar el rendimiento operativo entre los distintos modelos de aeronaves y nodos de la red. 
    """, unsafe_allow_html=True)
##############################################################################################

st.divider()

############################################################################################

st.subheader("1.5 Limitaciones")

col_vettel, col_hamilton, col_verstappen = st.columns(3)
###############################################################################################
#### LADO IZQUIERDO PA ####
with col_vettel:
    st.markdown("""
        <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
        <h5 style="color: #304b7a; margin-top: 0; font-family: sans-serif;"> Limitación temporal </h5>
        <p style="font-size: 14px; color: #304b7a; font-family: sans-serif;
        ">
        ### info aqui###
        </p>
        </div>
        """, unsafe_allow_html=True)
################################################################################################
#### LADO CENTRAL PA ####
with col_hamilton:
    st.markdown("""
        <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
        <h5 style="color: #475569; margin-top: 0; font-family: sans-serif;"> Limitación espacial: </h5>
        <p style="font-size: 14px; color: #475569; font-family: sans-serif;
        ">
        ### info aqui###
        </p>
        </div>
        """, unsafe_allow_html=True)
################################################################################################
#### LADO DERECHO PA ####
with col_verstappen:
    st.markdown("""
        <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
        <h5 style="color: #1E3A8A; margin-top: 0; font-family: sans-serif;"> Limitación de datos </h5>
        <p style="font-size: 14px; color: #1E3A8A; font-family: sans-serif;
        ">
        ### info aqui###
        </p>
        </div>
        """, unsafe_allow_html=True) 
#################################################################################################

st.markdown(""" #### ​**Variables no contempladas**""")
st.markdown("""
 ###########info aqui########
""", unsafe_allow_html=True)

##################################################################################################

st.divider()