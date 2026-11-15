import streamlit as st
####################################################################################################
#### Barrita de la izquierda y creo que la letra ####
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
##################################################################################
st.set_page_config(page_title="Resumen", page_icon="💥", layout="wide")

##############################################################
#### cuadrito bonito del resumen ####
##############################################################
#### cuadrito del resumen ####
with st.expander("**RESUMEN**", expanded=False):
    st.markdown("""
     Este estudio consiste en un análisis cuantitativo de la base de datos de operaciones aéreas para evaluar el rendimiento, 
     los tiempos y el flujo de los vuelos registrados. Con el objetivo de procesar y explotar estos datos para identificar 
     patrones de retrasos, evaluar la eficiencia en los tiempos de tránsito y despegue, y generar métricas confiables 
     que faciliten la comprensión del rendimiento operativo de las rutas analizadas
    """, unsafe_allow_html=True)
#######################################################################################################
### INTRODUCCION ###
st.title("Introduccion")
########################################################################################################
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
La puntualidad es la capacidad, el hábito y el valor de cumplir con las obligaciones, citas, tareas o horarios en el momento 
exacto que se ha acordado. Por su parte la Real Academia Española, lo define como “el cuidado y la diligencia en llegar a una
 hora convenida o en realizar una acción a su debido tiempo”. En las aerolíneas, la puntualidad impacta directamente en la 
 eficiencia logística, la reducción de costos y la fluidez general del tránsito aéreo. La misma también define la credibilidad 
 ante el pasajero, siendo este un punto clave para obtener su confianza y convertirlo en un viajero frecuente. 

La puntualidad, además, es un indicador de algo más profundo: confiabilidad. Cuando un pasajero reserva un vuelo, deposita 
su confianza en llegar a tiempo a su destino. Un retraso puede ser entendible; pero la reiteración de retrasos no lo es. 
Por ello, las compañías aéreas intentan mantener altos niveles de puntualidad para lograr construir una reputación sólida 
y generar lealtad entre sus pasajeros.

Bajo estos precedentes, el presente trabajo se propone evaluar el cumplimiento de los horarios programados de salida y llegada 
de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017,
 mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales. El objetivo central es 
 investigar, mediante técnicas de estadística descriptiva, cómo variables específicas, tales como la franja horaria de salida 
 (scheduled_departure), el día de la semana, el aeropuerto de origen/destino y el tipo de aeronave (aircraft_code, model), 
 influyen en la frecuencia y magnitud de los retrasos, medidos a partir de la desviación entre los horarios reales y programados.

""", unsafe_allow_html=True)
########################################################################################################
### ESTRUCTURA DEL INFORME ###
st.subheader("Estructura del informe")
st.markdown(""" la estructura del informe
""", unsafe_allow_html=True)
########################################################################################################