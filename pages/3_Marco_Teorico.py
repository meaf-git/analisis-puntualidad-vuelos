import streamlit as st
#############################################################################################################################
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
#############################################################################################################
st.set_page_config(page_title="Marco Teorico", page_icon="👓", layout="wide")
st.title("Marco Teorico")

#### LA INFO #####
st.markdown(""" 
El análisis de la puntualidad aérea en Rusia requiere comprender un contexto geopolítico y operativo particular. 
Históricamente, el espacio aéreo ruso ha estado marcado por tensiones geopolíticas y divisiones regionales. 
Las aerolíneas internacionales se han visto históricamente condicionadas por restricciones de sobrevuelo, derivadas 
de sanciones de países occidentales, restricciones en el suministro de combustible y riesgos de seguridad asociados a 
zonas de conflicto militar. Esta dinámica ha generado una división operativa: por un lado, las aerolíneas de países con 
prohibiciones de acceso o que evitan el espacio aéreo por motivos de seguridad, y por el otro, las aerolíneas de países 
aliados que se benefician de las rutas transiberianas.

Por otra parte, dada la vasta extensión territorial de Rusia, los vuelos internos no son un lujo, sino una necesidad crítica 
para la conectividad del país. Esta dependencia del transporte aéreo interno obliga a los aeropuertos rusos a manejar normas 
de seguridad y operativas sumamente rigurosas. A pesar de la compleja situación geopolítica y del aislamiento parcial con 
Occidente, Rusia mantiene su compromiso de cumplir con los estándares globales de aviación civil, como los establecidos por 
la Organización de Aviación Civil Internacional, con el fin de evitar una desconexión total del transporte de pasajeros y 
mantener la operatividad de sus vuelos con países aliados.
""", unsafe_allow_html=True)
########################################################################################

st.divider ()

########################################################################################
#### CONCEPTOS ####
st.title("Conceptos de Aviación")   
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
    Es el intervalo desde que una aeronave sale de la puerta (off-block) hasta que se estaciona en la puerta de destino (in-block). 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Tiempo de Escala (Turnaround Time):**")
    st.markdown("""
    Se define como el período de tiempo que transcurre entre el momento en que una aeronave se detiene por completo en la puerta de 
    embarque al finalizar un vuelo y el momento en que inicia su movimiento para emprender el siguiente vuelo. 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Puntualidad Operacional (OTP):**")
    st.markdown("""
    La Puntualidad Operacional (OTP) es una métrica fundamental en la industria de la aviación, utilizada por aerolíneas, 
    aeropuertos y reguladores de todo el mundo para medir la puntualidad de las operaciones de vuelo. 

    • Salida a Tiempo (En Hora):vuelo que sale entre 0 y 14 minutos después de la hora programada.
    
    • Umbral de Tolerancia Operativa (+15min):un vuelo que despega o se retira de la puerta hasta 14 minutos y 59 segundos tarde se sigue considerando "puntual" a nivel estadístico para la IATA (Asociación Internacional de Transporte Aéreo) y los organismos reguladores.
    
    • Retraso (Delay):a partir del minuto 15:00, el vuelo se clasifica formalmente como retrasado.
    """, unsafe_allow_html=True)

###########################################################################################
#### COLUMNA CENTRAL ####
with col_centro:

    st.markdown("#### **• Hora Real de Entrada en Bloque:**")
    st.markdown("""
    Se refiere a la hora real en la que la aeronave entra en el bloque (posición de estacionamiento) y 
    se detiene por completo. Marca el final oficial del vuelo y es el punto de partida para calcular el tiempo de escala. 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Hora Programada de Salida del Bloque:**")
    st.markdown("""
    Es la hora planificada y publicada en la que una aeronave está programada para dejar su puesto, establecida durante el 
    proceso de programación de la aerolínea con mucha antelación.
    """, unsafe_allow_html=True)
    
    st.markdown("#### **• Hora Real de Salida del Bloque:**")
    st.markdown("""
    Es el momento exacto en que una aeronave abandona físicamente su posición de estacionamiento, registrado por sistemas de tierra o reportado por la tripulación. 
    """, unsafe_allow_html=True)

###########################################################################################
#### COLUMNA DERECHA ####
with col_der:
    st.markdown("#### **• Horario programado vs. horario real (scheduled vs. actual):**")
    st.markdown("""
    Esta distinción es relevante porque la salida y la llegada no son simétricas. La diferencia matemática entre ambos
      constituye la magnitud del retraso. El retraso se define como la desviación matemática entre ambos horarios. 
      Un valor positivo indica que el vuelo se ejecutó después de lo programado (retraso), un valor negativo indica que 
      se ejecutó antes (adelanto).  
      
    •Retraso_salida=Hora_real_salida–Hora_programada_salida
    •Retraso_llegada=Hora_real_llegada–Hora_programada_llegada
    """, unsafe_allow_html=True)   

    st.markdown("#### **• Estado del vuelo (Arrived):**")
    st.markdown("""
    Un vuelo clasificado como "arrived" es aquel que completó su ciclo operativo, es decir, que despegó de su aeropuerto 
    de origen y aterrizó efectivamente en su aeropuerto de destino, registrando un horario real de llegada. 
    """, unsafe_allow_html=True)

    st.markdown("#### **• Frecuencia vs. magnitud:**")
    st.markdown("""
    Un vuelo puede tener una baja frecuencia de retrasos, pero cuando se retrasa, la magnitud puede ser tan alta que genere 
    un impacto severo en la red  y en la experiencia del pasajero. Para evaluar correctamente el cumplimiento de los horarios, 
    es necesario distinguir entre:

    •Frecuencia (conteo y porcentaje): se refiere a la cantidad de veces que ocurre un retraso. Estadísticamente, se mide como el conteo absoluto de vuelos afectados o como la proporción (porcentaje) de vuelos que superan su horario programado respecto al total de vuelos analizados..

    •Magnitud (minutos de desviación): se refiere a la intensidad o gravedad del retraso. 
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
            Se refiere al cumplimiento del horario en el aeropuerto de origen. Operativamente, se mide comparando el momento 
            real en que la aeronave se retira de los calzos (inicio del movimiento), frente al horario planificado para dicha acción.
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
            Se define como el grado de cumplimiento del horario programado en el aeropuerto de destino. Constituye el indicador que 
            mide la desviación temporal entre el momento en que un vuelo arriba efectivamente a su destino y el momento en que estaba 
            planificado que lo hiciera.
            </p>
            </div>
            """, unsafe_allow_html=True)
#########################################################################################

st.divider()

#########################################################################################
######## titulo de la seccion ########

st.title("Factores de dinámica temporal y propagación del retraso")  

###################################################################################
###### sub topicS de la seccion ######

st.subheader("• Efecto dominó / efecto red (ripple effect)")

st.markdown(""" 
Es un fenómeno operativo en el transporte aéreo donde un retraso inicial en un vuelo (derivado de las condiciones meteorológicas, problemas técnicos o congestión local) se propaga a través de la red. Esto provoca un efecto dominó que retrasa los siguientes vuelos de ese avión y su tripulación. Además, perjudica las conexiones de los pasajeros y multiplica los problemas en el resto de los aeropuertos.
""", unsafe_allow_html=True)

##################################################################################

st.subheader("• Franjas horarias y slots")

st.markdown(""" 
Se refiere a intervalos de tiempo específicos asignados a una aerolínea para llevar a cabo el aterrizaje o despegue de una aeronave en un aeropuerto congestionado o coordinado. El cumplimiento estricto de los slots (permiso de la aerolínea para que un avión pueda aterrizar y despegar en un aeropuerto en una hora y fecha en específico) es vital para que el aeropuerto siga en movimiento y evitar que todo se atasque, se ahorran sanciones y se evita que las terminales se llenen de gente.
""", unsafe_allow_html=True)

#########################################################################################

st.subheader("• Patrones temporales semanales (estacionalidad operativa)")

st.markdown(""" 
Son variaciones recurrentes en el volumen de tráfico aéreo, la demanda de pasajeros y los imprevistos retrasos que se repiten de forma sistemática en función de los días de la semana (por ejemplo, las horas pico cuando todos viajan por trabajo o en las salidas de fin de semana) o ciclos operativos regulares.
""", unsafe_allow_html=True)

#########################################################################################

st.divider ()

#########################################################################################
######## titulo de la segunda seccion ########

st.title("Factores de Infraestructura y flota")  

col_sol, col_luna, col_malte = st.columns(3)

###################################################################################
###### sub topic de la seccion ######
with col_sol:
    st.markdown("""
    <div style="background-color: #E2ECFD; border: 1.5px solid #91B8FC; border-radius: 12px; padding: 16px; height: 100%;">
    <h5 style="color: #022157; margin-top: 0; font-family: sans-serif;"> Nodos de la red aérea (aeropuertos) </h5>
    <p style="font-size: 14px; color: #022157; font-family: sans-serif;
    ">
    Estos son los centros de operaciones de la red. Incluyen tanto a los aeropuertos principales como a los secundarios, que es donde se concentran y distribuyen los aviones, la gente y la carga. Al final, lo que ocurra en estos lugares determina si todo el sistema funciona de manera correcta o se atasca.
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
    Es una clasificación para los diferentes tipos de aviones según su categoría, tamaño, capacidad de pasajeros, alcance y requerimientos técnicos. La tipología influye en los tiempos de servicio en tierra, la asignación de puertas de embarque y la compatibilidad con la infraestructura de los aeropuertos.
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
    Es el intervalo de tiempo necesario para que una aeronave llegue a la puerta de estacionamiento, complete el desembarque, la limpieza, el servicio de catering, el reabastecimiento de combustible, la carga de equipaje y el nuevo embarque de pasajeros, quedando lista para iniciar su siguiente vuelo. Cualquier demora en este proceso influye directamente en la puntualidad de la rotación.
    </p>
    </div>
    """, unsafe_allow_html=True)
#########################################################################################

st.divider ()

#########################################################################################
##### titulo de la tercera seccion ######## 
st.title("Factores contextuales")

col_papa, col_mama = st.columns(2)
#######################################################################################################################################
#### PAPA ####    
with col_papa:
    st.subheader("• Factores de gestión del tráfico aéreo (ATM/ATFM):")
    
    st.markdown(""" 
    La Air Traffic Management (ATM) y la Air Traffic Flow Management (ATFM) son los sistemas encargados de regular el 
    flujo de aeronaves en el espacio aéreo y en los aeropuertos para mantener la seguridad. Cuando la demanda de vuelos 
    supera la capacidad de un aeropuerto o de un sector aéreo, los controladores aplican restricciones. Esto obliga a las 
    aerolíneas a retener los aviones en tierra (generando retrasos en la salida) o a hacer esperas en el aire (generando 
    retrasos en la llegada).
    """, unsafe_allow_html=True)
    
#########################################################################################################################################
#### MAMA ####
with col_mama:
    st.subheader("• Factores de aerolínea y tierra:")
        
    st.markdown(""" 
    Corresponden a las ineficiencias en la operación terrestre. Incluyen problemas en el manejo de equipaje (handling), 
    demoras en el embarque de pasajeros, fallas técnicas no programadas de la aeronave, o la falta de disponibilidad de 
    tripulaciones. 
    """, unsafe_allow_html=True)

    st.subheader("• Factores meteorológicos:")
            
    st.markdown(""" 
    Las condiciones meteorológicas son las variables atmosféricas medibles, como temperatura, presión, viento, humedad, 
    nubosidad y precipitación, presentes en un lugar y momento específicos.  El clima puede obligar a reducir la tasa de 
    aterrizajes (disminuyendo la capacidad de la pista), retrasar las operaciones de carga y descarga, o impedir el despegue.  
    """, unsafe_allow_html=True)
#########################################################################################