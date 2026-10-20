import streamlit as st

st.set_page_config(page_title="Resumen", page_icon="💥", layout="wide")

##############################################################
#### resumen (opcional el que lo quiera ver) ####
with st.expander("**RESUMEN**", expanded=False):
    st.markdown("""
     Este estudio consiste en un análisis cuantitativo de la base de datos de operaciones aéreas para evaluar el rendimiento, 
     los tiempos y el flujo de los vuelos registrados. Con el objetivo de procesar y explotar estos datos para identificar 
     patrones de retrasos, evaluar la eficiencia en los tiempos de tránsito y despegue, y generar métricas confiables 
     que faciliten la comprensión del rendimiento operativo de las rutas analizadas
    """, unsafe_allow_html=True)
#######################################################################################################
### INTRODUCCION ###
st.header("Introduccion")
#######################################################################################################
st.markdown( ### CUADRO BONITO (CON FRASE BONITA) ###
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
            Rigas Doganis, The Airline Business (2006)
        </h6>
        <p style="color: #1565c0; font-style: italic; font-size: 1.05rem; line-height: 1.6; margin: 0;">
           "Un retraso no es únicamente una pérdida de tiempo; es una alteración en cadena que afecta la eficiencia, 
           los costos operacionales y la satisfacción del usuario en la aviación moderna."
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
########################################################################################################
st.markdown(""" 
la info de la introduccion
""", unsafe_allow_html=True)
########################################################################################################

st.divider()

########################################################################################################
### ESTRUCTURA DEL INFORME ###
st.subheader("Estructura del informe")
st.markdown(""" la estructura del informe
""", unsafe_allow_html=True)
########################################################################################################

st.divider()