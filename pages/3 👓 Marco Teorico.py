import streamlit as st

st.set_page_config(page_title="Marco Teorico", page_icon="👓", layout="wide")
st.title("Marco Teorico")
#######################################################################################
#### LA INFO #####
st.markdown(""" 
El análisis de la puntualidad aérea en Rusia requiere comprender un contexto geopolítico y 
operativo particular. Históricamente, el espacio aéreo ruso ha estado marcado por tensiones
 geopolíticas y divisiones regionales. Las aerolíneas internacionales se han visto 
 históricamente condicionadas por restricciones de sobrevuelo, derivadas de sanciones de 
 países occidentales, restricciones en el suministro de combustible y riesgos de seguridad 
 asociados a zonas de conflicto militar. Esta dinámica ha generado una división operativa: 
 por un lado, las aerolíneas de países con prohibiciones de acceso o que evitan el espacio 
 aéreo por motivos de seguridad, y por el otro, las aerolíneas de países aliados que se 
 benefician de las rutas transiberianas.

 Por otra parte, dada la vasta extensión territorial de Rusia, los vuelos internos no son 
 un lujo, sino una necesidad crítica para la conectividad del país. Esta dependencia del 
 transporte aéreo interno obliga a los aeropuertos rusos a manejar normas de seguridad y 
 operativas sumamente rigurosas. A pesar de la compleja situación geopolítica y del 
 aislamiento parcial con Occidente, Rusia mantiene su compromiso de cumplir con los 
 estándares globales de aviación civil, como los establecidos por la Organización de 
 Aviación Civil Internacional, con el fin de evitar una desconexión total del transporte 
 de pasajeros y mantener la operatividad de sus vuelos con países aliados.

""", unsafe_allow_html=True)
########################################################################################

st.divider()

########################################################################################
#### CONCEPTOS ####
st.header("Conceptos de Aviación")
########################################################################################
col_izq, col_centro, col_der = st.columns(3)
########################################################################################
#### COLUMNA IZQUIERDA ####
with col_izq:
    st.markdown("#### **• Puntualidad:**")
    st.markdown("""
    En la aviación se refiere a que los vuelos y las operaciones se ejecutan de acuerdo con los tiempos programados. 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Cumplimiento de Horarios:**")
    st.markdown("""
    Mide qué tan de cerca todos los elementos de las operaciones de una aerolínea o aeropuerto siguen el horario publicado, 
    incluyendo no solo salidas y llegadas sino también el manejo en tierra, mantenimiento y cambios de tripulación. 
    A menudo se mide usando el porcentaje de vuelos dentro de una ventana establecida (±5 o ±15 minutos) del horario, 
    permitiendo a los operadores identificar y corregir desviaciones de procesos.

    """, unsafe_allow_html=True)

    st.markdown("#### **• Block Time:**")
    st.markdown("""
    Es el intervalo desde que una aeronave sale de la puerta (off-block) hasta que se estaciona en la puerta de 
    destino (in-block). 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Tiempo de Escala (Turnaround Time):**")
    st.markdown("""
    Se define como el período de tiempo que transcurre entre el momento en que una aeronave se detiene por completo en 
    la puerta de embarque al finalizar un vuelo y el momento en que inicia su movimiento para emprender el siguiente vuelo. 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Puntualidad Operacional (OTP):**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

###########################################################################################
#### COLUMNA CENTRAL ####
with col_centro:

    st.markdown("#### **• Hora Real de Entrada en Bloque:**")
    st.markdown("""
    EL PARRAFO AQUI
    
    • Salida a Tiempo (En Hora):
    
    • Umbral de Tolerancia Operativa (+15min):
    
    • Retraso (Delay):
    """, unsafe_allow_html=True)

    st.markdown("#### **• Hora Programada de Salida del Bloque:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)
    
    st.markdown("#### **• Hora Real de Salida del Bloque:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)
###########################################################################################
#### COLUMNA DERECHA ####
with col_der:
    st.markdown("#### **• Horario programado vs. horario real (scheduled vs. actual):**")
    st.markdown("""
    INFO AQUI PLIS

    •

    •
    """, unsafe_allow_html=True)   

    st.markdown("#### **• Estado del vuelo (Arrived):**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Frecuencia vs. magnitud:**")
    st.markdown("""
    INFO AQUI PLIS

    •

    •
    """, unsafe_allow_html=True)
##########################################################################################
st.markdown("#### **• Puntualidad de salida vs. llegada:**")

col_salida, col_llegada = st.columns(2)
#######################################################################################################################################
#### SALIDA ####    
with col_salida:
    st.markdown("""
            <div style="background-color: #4d90d2; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
            <h5 style="color: #FFFFFF; margin-top: 0; font-family: sans-serif;"> Puntualidad de Salida </h5>
            <p style="font-size: 14px; color: #FFFFFF; font-family: sans-serif;
            ">
            ### info aqui###
            </p>
            </div>
            """, unsafe_allow_html=True)
#########################################################################################################################################
#### LLEGADA ####
with col_llegada:
    st.markdown("""
            <div style="background-color: #396a9a; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
            <h5 style="color: #FFFFFF; margin-top: 0; font-family: sans-serif;"> Puntualidad de Llegada </h5>
            <p style="font-size: 14px; color: #FFFFFF; font-family: sans-serif;
            ">
            ### info aqui###
            </p>
            </div>
            """, unsafe_allow_html=True)
#########################################################################################

st.divider()

#########################################################################################
######## titulo de la seccion########

st.header("Factores de dinámica temporal y propagación del retraso")  

###################################################################################
###### sub topicS de la seccion ######

st.subheader("• Efecto dominó / efecto red (ripple effect)")

st.markdown(""" 
desde aqui
informacion
hasta aqui 
""", unsafe_allow_html=True)

##################################################################################

st.subheader("• Franjas horarias y slots")

st.markdown(""" 
desde aqui
informacion
hasta aqui 
""", unsafe_allow_html=True)

#########################################################################################

st.subheader("• Patrones temporales semanales (estacionalidad operativa)")

st.markdown(""" 
desde aqui
informacion
hasta aqui 
""", unsafe_allow_html=True)

#########################################################################################

st.divider()

#########################################################################################

#########################################################################################
######## titulo de la segunda seccion ########

st.header("Factores de Infraestructura y flota")  

col_sol, col_luna, col_malte = st.columns(3)

###################################################################################
###### sub topic de la seccion ######
with col_sol:
    st.markdown("""
    <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
    <h5 style="color: #022157; margin-top: 0; font-family: sans-serif;"> Nodos de la red aérea (aeropuertos) </h5>
    <p style="font-size: 14px; color: #022157; font-family: sans-serif;
    ">
    ### info aqui###
    </p>
    </div>
    """, unsafe_allow_html=True)
##################################################################################
with col_luna:
    st.markdown("""
    <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
    <h5 style="color: #022157; margin-top: 0; font-family: sans-serif;"> Tipología de aeronaves </h5>
    <p style="font-size: 14px; color: #022157; font-family: sans-serif;
    ">
    ### info aqui###
    </p>
    </div>
    """, unsafe_allow_html=True)
#########################################################################################
with col_malte:
    st.markdown("""
    <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
    <h5 style="color: #022157; margin-top: 0; font-family: sans-serif;"> Tiempo de rotación (turnaround time) </h5>
    <p style="font-size: 14px; color: #022157; font-family: sans-serif;
    ">
    ### info aqui###
    </p>
    </div>
    """, unsafe_allow_html=True)
#########################################################################################

st.divider()

#########################################################################################
##### titulo de la tercera seccion ######## 
st.header("Factores contextuales")

col_papa, col_mama = st.columns(2)

#######################################################################################################################################
#### PAPA ####    
with col_papa:
    st.subheader("• Factores de gestión del tráfico aéreo (ATM/ATFM):")
    
    st.markdown(""" 
    desde aqui
    informacion
    hasta aqui 
    """, unsafe_allow_html=True)

#########################################################################################################################################
#### MAMA ####
with col_mama:
    st.subheader("• Factores de aerolínea y tierra:")
        
    st.markdown(""" 
    desde aqui
    informacion
    hasta aqui 
    """, unsafe_allow_html=True)

    st.subheader("• Factores meteorológicos:")
            
    st.markdown(""" 
    desde aqui
    informacion
    hasta aqui 
    """, unsafe_allow_html=True)
#########################################################################################

st.divider()

#########################################################################################
######## titulo y descripcion de la cuarta seccion ########
st.header("Estadıstica descriptiva")

st.markdown(""" 
desde aqui
informacion
hasta aqui 
""", unsafe_allow_html=True)

##########################################################################################

col_messi, col_cr7, col_kros = st.columns(3)

##########################################################################################
####### COLUMNA IZQUIERDA COMO MESSI ###########
with col_messi:
    
    st.markdown("#### **• Medidas de tendencia central:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Media aritmética:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Mediana:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)
#########################################################################################
######## COLUMNA DERECHA COMO CR7 ###########
with col_cr7:

    st.markdown("#### **• Moda:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Medidas de dispersión y variabilidad:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Varianza:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)
#######################################################################################
##### COLUMNA MEDIO CAMPO COMO KROS ###########
with col_kros:
    st.markdown("#### **• Desviación estándar:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    st.markdown("#### **• Medidas de posición (cuartiles):**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)

    with st.expander("Mas detalles", expanded=False):
        st.markdown("""
        •

        •

        •
        """, unsafe_allow_html=True)    

    st.markdown("#### **• Coeficiente de correlacion de Pearson:**")
    st.markdown("""
    INFO AQUI PLIS
    """, unsafe_allow_html=True)
#############################################################################

st.divider() 