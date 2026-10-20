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
la Justificacion
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