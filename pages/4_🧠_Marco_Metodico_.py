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
st.subheader("Denormalización de los datos")

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
