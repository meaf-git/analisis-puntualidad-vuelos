import streamlit as st
############################################################################################
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
##############################################################################################

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
st.title("Justificación")
st.markdown("""
El estudio de la puntualidad en el transporte aéreo es relevante debido a que es indicador clave que afecta al tránsito aéreo, la rentabilidad de las aerolíneas y la eficiencia en todo el sistema de aviación. En la actualidad, los pasajeros están dispuestos a pagar más por volar con aerolíneas que tienen un mejor historial de puntualidad. Dichas aerolíneas suelen tener márgenes de ganancias operativas superiores. Cada punto de mejora se traduce en millones de dólares de ahorro, ya que se reducen los costos asociados a los retrasos (como compensaciones a pasajeros, combustible extra y horas de tripulación) y se optimiza el uso de los aviones.

Desde una perspectiva académica, resulta significativo analizar cómo diversos factores influyen en las salidas y llegadas de los vuelos, mediante el uso de herramientas de análisis estadístico y modelado de datos que permitan identificar patrones, tendencias y correlaciones entre variables asociadas. Al cruzar variables temporales (día, hora) y operacionales (tipo de aeronave, aeropuertos de origen/destino), la investigación no solo describe el fenómeno, sino que generará información accionable. Este tipo de análisis puede contribuir a identificar áreas de alta incidencia geográfica y franjas horarias críticas, así como a generar conclusiones sobre futuras estrategias de optimización de la puntualidad, reducción de costos y mejora de la experiencia del pasajero en el sector aeronáutico.
""", unsafe_allow_html=True)
##############################################################################################

##############################################################################################
### OBJETIVOS ###
st.title("Objetivos")

st.subheader("1.1 Objetivo general")
st.markdown("""
     Evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017, mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales.
    """, unsafe_allow_html=True)

st.subheader("1.2 Objetivos específicos")
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
st.title("Variables de estudio")
##############################################################################################

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
            #######info aqui#######
        </p>
        <ul style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin-bottom: 12px; padding-left: 20px;">
            <li style="margin-bottom: 8px;"><b>Variables temporales:</b> 
            #######info aqui#######
            </li>
            <li><b>Variables operacionales:</b> 
            #######info aqui#######
            </li>
        </ul>
        <p style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin: 0;">
            #######terminas tu info aqui (ultimo parrafo)#######
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
###########################################################################################
#### UNIVERSO #####
st.title(" Universo y Unidad de Análisis")

col_kobe, col_lebron = st.columns(2)

###########################################################################################
#### LADO IZQUIERDO ####    
with col_kobe:
    st.markdown("#### **• Universo de programación:**")
    st.markdown("""
    #######info aqui#######
    """, unsafe_allow_html=True)

    st.markdown("#### **• Universo de operación:**")
    st.markdown("""
    #######info aqui#######
    """, unsafe_allow_html=True)
############################################################################################
#### LADO DERECHO ####

with col_lebron:
    
    st.markdown("#### **• Unidad de análisis:**")
    st.markdown("""
    #######info aqui#######
    """, unsafe_allow_html=True)
    
    st.markdown("#### **• Técnicas:**")
    st.markdown("""
    #######info aqui#######
    """, unsafe_allow_html=True)

##############################################################################################
#### LIMITACIONES #####

st.title(" Limitaciones")

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

st.title(""" ​**Variables no contempladas**""")
st.markdown("""
 ###########info aqui########
""", unsafe_allow_html=True)

##################################################################################################

