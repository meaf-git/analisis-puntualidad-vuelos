import streamlit as st

st.set_page_config(page_title="Marco Metódico", page_icon="🧠", layout="wide")

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
    [data-testid="stSidebarNav"] a:any-link,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] a:any-link {
        color: #454545 !important;
    }
    .metodo-denormalizacion {
        max-width: 82ch;
    }
    .metodo-denormalizacion h3 {
        margin-top: 1.2rem;
    }
    .metodo-denormalizacion .metodo-tabla {
        color: #454545;
        background-color: #e9e9e9;
        border-radius: 4px;
        padding: 0.08em 0.3em;
        font-family: ui-monospace, monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("Marco Metódico")

st.subheader("Proceso de Normalización de los datos")
st.markdown("""
<section class="metodo-denormalizacion">
  <h3>Primera forma normal (1FN): valores atómicos</h3>
  <p>Inicialmente, campos como los nombres de las ciudades, aeropuertos o modelos de
  aviones se encontraban aglomerados en objetos JSON multilingües (ruso), mientras que
  las coordenadas geográficas estaban unidas en un solo texto. Para cumplir con la
  atomicidad de la Primera Forma Normal (1FN), en el diseño final estos valores se
  desaglomeraron en columnas atómicas individuales
  (<span class="metodo-tabla">nombre</span>, <span class="metodo-tabla">nombre_ru</span>,
  <span class="metodo-tabla">longitud</span> y <span class="metodo-tabla">latitud</span>),
  permitiendo un manejo directo de los datos sin tener que procesar cadenas compuestas.</p>

  <h3>Tercera forma normal (3FN): catálogos independientes</h3>
  <p>Para erradicar las dependencias transitivas y alcanzar la Tercera Forma Normal (3FN),
  se extrajeron catálogos independientes, siendo la creación de la tabla
  <span class="metodo-tabla">ciudades</span> la modificación más evidente. Anteriormente,
  el nombre de la ciudad y su zona horaria residían directamente en la tabla de
  aeropuertos, lo que generaba duplicación si una misma ciudad poseía varios aeropuertos.
  Al aislar las ciudades con su propia clave primaria, se eliminó esa redundancia.</p>

  <p>Del mismo modo, textos repetitivos como las condiciones de tarifa ('Economy',
  'Business') y los estados de vuelo ('Scheduled', 'Arrived') se transformaron en las
  tablas de soporte <span class="metodo-tabla">clases_tarifarias</span> y
  <span class="metodo-tabla">estados_vuelo</span>, reemplazando cadenas de texto pesadas
  por IDs enteros ligeros.</p>

  <h3>Separación entre el itinerario y el evento real</h3>
  <p>Asimismo, en el núcleo del negocio se aplicó una descomposición semántica al separar
  el itinerario conceptual del evento real. La tabla <span class="metodo-tabla">rutas</span>
  pasó a definir la plantilla fija del trayecto (origen, destino, aeronave asignada por
  defecto y duración estimada), mientras que la tabla
  <span class="metodo-tabla">vuelos</span> se reservó únicamente para registrar las
  ejecuciones físicas en el tiempo, controlando sus fechas, horas reales y estados de
  operación.</p>

  <h3>Reservas, pasajes y embarque (2FN)</h3>
  <p>Finalmente, el diseño garantiza la integridad del proceso de compra y abordaje
  alineando las claves primarias compuestas propias de la Segunda Forma Normal. La
  transacción comercial se divide entre la reserva (la compra global) y el pasaje
  (asociado a un pasajero). Como un pasaje puede incluir varios tramos o escalas, la
  tabla <span class="metodo-tabla">cupones</span> resuelve esta relación de muchos a
  muchos, conectando el pasaje con el vuelo correspondiente y fijando el costo del
  tramo.</p>

  <p>A su vez, la tarjeta de embarque valida su emisión, vinculando su clave foránea
  compuesta directamente a la pareja
  (<span class="metodo-tabla">numero_pasaje</span>, <span class="metodo-tabla">vuelo_id</span>)
  de los cupones, asegurando que nadie pueda recibir un pase de abordaje para un vuelo si
  previamente no adquirió un cupón para ese trayecto específico. Todo esto se complementa
  con reglas de validación en la base de datos (CHECK y UNIQUE) que impiden incoherencias
  horarias, coordenadas fuera de rango o la asignación de un mismo asiento a dos
  pasajeros en el mismo vuelo.</p>
</section>
""", unsafe_allow_html=True)


st.subheader("Denormalización de los datos")
from pathlib import Path
diagrama = Path(__file__).resolve().parents[1]/ "assets" / "denormalizacion_vuelos.svg"
st.image(diagrama.read_text(encoding="utf-8"), width="stretch")
st.markdown("""
<section class="metodo-denormalizacion">
  <h3>De las tablas originales al modelo de análisis</h3>
  <p>Partimos de la base normalizada y de los vuelos seleccionados durante la
  limpieza. En DuckDB creamos siete dimensiones para describir los vuelos:
  fecha, franja horaria, aeropuerto, ruta, aeronave, estado y rango de demora.
  Una misma dimensión de aeropuertos sirve para identificar el origen y el
  destino de cada vuelo. Esto permite agrupar las demoras por cualquiera de
  los dos sin tener que reconstruir la información del aeropuerto en cada consulta.</p>

  <h3>Programación y cálculo de demoras</h3>
  <p>La tabla <span class="metodo-tabla">hechos_vuelos</span> conservó los
  <strong>33.121 vuelos programados</strong>. En
  <span class="metodo-tabla">hechos_demoras</span> incluimos los
  <strong>16.773 vuelos con salida real registrada</strong>.
  Cuando faltaba la hora real de llegada, las medidas que dependían de esa
  hora quedaron sin valor.</p>

  <p>Calculamos el retraso de salida y el de llegada restando a cada hora real
  la hora programada correspondiente. La duración real se obtuvo con la
  diferencia entre la llegada y la salida reales. Para medir los minutos
  recuperados, restamos el retraso de llegada al de salida. Si un vuelo salió
  20 minutos tarde y llegó 12 minutos tarde, recuperó 8 minutos durante el trayecto.</p>

  <h3>Qué vuelos usamos para el análisis</h3>
  <p>Integramos las medidas y los datos descriptivos en
  <span class="metodo-tabla">vuelos_denormalizados</span>. La tabla tiene
  <strong>44 campos y una fila por vuelo</strong>. Contiene los
  <strong>16.707 vuelos completados</strong> que pasaron la limpieza, del 16 de
  julio al 15 de agosto de 2017. Esa selección permite comparar salida y llegada
  con registros que cuentan con ambas horas reales.</p>

  <p>Para clasificar cada vuelo por día y franja usamos la hora programada local
  del aeropuerto de origen, calculada durante la limpieza. Así, una salida
  programada a las 8:00 se agrupa en la franja de 06:00 a 11:59 de su aeropuerto.</p>

  <h3>Verificación y uso de los datos</h3>
  <p>Creamos cinco vistas para preparar los datos y consultarlos en Streamlit y
  Power BI. Antes de usar la tabla consolidada, verificamos que tuviera los mismos
  16.707 identificadores de la selección limpia, que cada vuelo apareciera una
  sola vez y que sus retrasos coincidieran con las diferencias entre los horarios
  programados y reales. Conservamos los minutos de demora por vuelo para aplicar
  el umbral que corresponda a cada indicador.</p>
</section>
""", unsafe_allow_html=True)
