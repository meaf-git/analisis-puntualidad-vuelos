import streamlit as st
from pathlib import Path

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
        width: 100%;
        max-width: 100%;
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
diagrama_normalizacion = Path(__file__).resolve().parents[1] / "assets" / "esquema_relacional_vuelosFormato.svg"
st.image(diagrama_normalizacion.read_text(encoding="utf-8"), width="stretch")
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

  <h3>Segunda forma normal (2FN): reservas, pasajes y embarque</h3>
  <p>El diseño garantiza la integridad del proceso de compra y abordaje alineando las
  claves primarias compuestas propias de la Segunda Forma Normal. La transacción
  comercial se divide entre la reserva (la compra global) y el pasaje (asociado a un
  pasajero). Como un pasaje puede incluir varios tramos o escalas, la tabla
  <span class="metodo-tabla">cupones</span> resuelve esta relación de muchos a muchos,
  conectando el pasaje con el vuelo correspondiente y fijando el costo del tramo.</p>

  <p>A su vez, la tarjeta de embarque valida su emisión, vinculando su clave foránea
  compuesta directamente a la pareja
  (<span class="metodo-tabla">numero_pasaje</span>, <span class="metodo-tabla">vuelo_id</span>)
  de los cupones, asegurando que nadie pueda recibir un pase de abordaje para un vuelo si
  previamente no adquirió un cupón para ese trayecto específico. Todo esto se complementa
  con reglas de validación en la base de datos (CHECK y UNIQUE) que impiden incoherencias
  horarias, coordenadas fuera de rango o la asignación de un mismo asiento a dos
  pasajeros en el mismo vuelo.</p>

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
</section>
""", unsafe_allow_html=True)

st.subheader("Proceso de limpieza de los datos")
st.markdown("""
<section class="metodo-denormalizacion">
  <p>Para lograr la estandarización y validación de los datos, el proceso se apoya en
  dos repositorios de referencia de la industria geográfica y aeronáutica. Por un lado,
  se utiliza el Repositorio TZ (Base de Datos de Zonas Horarias de IANA / tz database)
  dentro del bloque <span class="metodo-tabla">CASE c.zona_horaria</span> para mapear
  identificadores geográficos estándar (como 'Europe/Moscow', 'Asia/Yekaterinburg' o
  'Asia/Kamchatka') a sus desplazamientos horarios reales respecto al tiempo universal
  coordinado (desde UTC+2 hasta UTC+12). Esto permite convertir las horas originales,
  registradas inicialmente en horario de Moscú, a la hora local exacta de cada
  aeropuerto de origen.</p>

  <p>Por otro lado, se emplean los estándares de la industria aeronáutica (ANA / IATA).
  La estructura sigue las convenciones de codificación de la aviación civil, utilizando
  códigos IATA de tres letras para identificar los aeropuertos y códigos estándar para
  las aeronaves, además de aplicar criterios operacionales internacionales como el
  umbral de demora de 15 minutos (&gt; 15 min) definido por la IATA para clasificar los
  retrasos significativos tanto en salida como en llegada.</p>

  <h3>Primera Etapa: selección y depuración de tablas</h3>
  <p>En esta primera fase se crean versiones limpias de las tablas normalizadas
  existentes, aplicando restricciones estrictas de integridad (PRIMARY KEY, FOREIGN KEY,
  NOT NULL y CHECK) y conservando únicamente las columnas útiles para el análisis
  posterior. De este modo, se conforma la tabla
  <span class="metodo-tabla">lim_aeropuertos</span>, que almacena el código IATA
  (validando una longitud exacta de 3 caracteres), el nombre del aeropuerto y su
  identificador de ciudad; la tabla <span class="metodo-tabla">lim_aeronaves</span>, que
  contiene el código identificador y el modelo del avión; y finalmente la tabla
  <span class="metodo-tabla">lim_rutas</span>, encargada de registrar el número de vuelo,
  los aeropuertos de origen y destino (validando mediante CHECK que ambos sean
  distintos), el código de aeronave y la duración estimada en minutos (asegurando que sea
  mayor a cero).</p>

  <h3>Segunda Etapa: limpieza, conversión horaria y cálculo de variables</h3>
  <p>Mediante el uso de CTEs, se depura y transforma la tabla de vuelos
  (<span class="metodo-tabla">lim_vuelos</span>) comenzando por el filtrado de registros
  válidos. Para ello, se conservan únicamente los vuelos completados
  (<span class="metodo-tabla">estado_id = 5</span>, correspondiente a 'Arrived') que
  posean marcas de tiempo reales tanto de salida como de llegada (IS NOT NULL),
  descartando así vuelos cancelados o incompletos y obteniendo un total de 16.707
  registros válidos. Asimismo, se normaliza el formato de fecha y hora recortando las
  cadenas de texto a los primeros 19 caracteres (YYYY-MM-DD HH:MM:SS) mediante la función
  <span class="metodo-tabla">substr()</span> para eliminar el sufijo de zona horaria
  (+03), logrando unificar el formato datetime sin alterar los tiempos de retraso.</p>

  <p>Posteriormente, se realiza la conversión a hora local
  (<span class="metodo-tabla">sp_local</span>) cruzando el aeropuerto de origen con su
  respectiva ciudad y zona horaria IANA TZ. Esto permite calcular el diferencial respecto
  a la hora de Moscú (<span class="metodo-tabla">utc_offset_h - 3</span>) y obtener la
  hora local programada de salida. Con las marcas de tiempo unificadas, se calculan los
  minutos exactos de retraso en salida (<span class="metodo-tabla">ds</span>) y llegada
  (<span class="metodo-tabla">da</span>) mediante la diferencia de timestamps Unix
  (<span class="metodo-tabla">strftime('%s', ...)</span>), y se determina tanto el número
  de día de la semana (del 1 = Lunes al 7 = Domingo) como su nombre correspondiente en
  español.</p>

  <p>Adicionalmente, a partir de la hora local extraída (de 0 a 23), los vuelos se
  clasifican en 4 franjas horarias específicas:</p>
  <ol>
    <li>Madrugada (00-05)</li>
    <li>Día (06-11)</li>
    <li>Tarde (12-17)</li>
    <li>Noche (18-23)</li>
  </ol>

  <p>Por último, para facilitar las consultas analíticas posteriores, se generan 5
  indicadores booleanos (con valores 0 o 1):</p>
  <ol>
    <li><span class="metodo-tabla">salio_a_tiempo</span>: retraso en salida &le; 0 minutos.</li>
    <li><span class="metodo-tabla">llego_a_tiempo</span>: retraso en llegada &le; 0 minutos.</li>
    <li><span class="metodo-tabla">salio_a_tiempo_llego_tarde</span>: salió puntual (&le; 0) pero llegó con retraso (&gt; 0).</li>
    <li><span class="metodo-tabla">demora_salida_15</span>: retraso en salida mayor a 15 minutos (criterio IATA).</li>
    <li><span class="metodo-tabla">demora_llegada_15</span>: retraso en llegada mayor a 15 minutos.</li>
  </ol>

  <h3>Tercera: indexación y eliminación de tablas originales innecesarias</h3>
  <p>Para finalizar el proceso y optimizar el rendimiento de la base de datos, se definen
  cuatro índices (<span class="metodo-tabla">ix_vuelos_ruta</span>,
  <span class="metodo-tabla">ix_vuelos_origen</span>,
  <span class="metodo-tabla">ix_vuelos_destino</span> e
  <span class="metodo-tabla">ix_vuelos_aeronave</span>) destinados a agilizar las futuras
  consultas de agrupación (GROUP BY) y filtrado. Concluida esta estructuración, se ejecuta
  DROP TABLE sobre las ocho tablas originales en inglés
  (aircrafts_data, airports_data, seats, tickets, flights, bookings, boarding_passes y
  ticket_flights), esto con el propósito de liberar espacio y conservar exclusivamente las
  tablas limpias.</p>
</section>
""", unsafe_allow_html=True)


st.subheader("Proceso de Denormalización de los datos")
diagrama = Path(__file__).resolve().parents[1] / "assets" / "denormalizacion_vuelos.svg"
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