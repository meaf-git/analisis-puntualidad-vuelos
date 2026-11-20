from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Conclusiones", page_icon="🎉", layout="wide")

# ==============================================================================
# CSS UNIFICADO CON APP.PY
# ==============================================================================
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
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarNav"] span {
        display: none !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        display: inline !important;
    }
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarUserContent"] {
        opacity: 0 !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarUserContent"] {
        opacity: 1 !important;
        visibility: visible !important;
        height: auto !important;
        transition: opacity 0.3s ease-in-out;
    }
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
    section[data-testid="stSidebar"]:not(:hover)::before {
        content: "";
        display: block;
        width: 34px;
        height: 34px;
        margin: 20px auto 0 auto;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23F4D03F'%3E%3Cpath d='M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z'/%3E%3C/svg%3E");
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BARRA LATERAL INFERIOR (UNIFICADA CON APP.PY)
# ==============================================================================
st.sidebar.divider()
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; padding: 6px 0 10px 0;">
    <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="#F4D03F">
        <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
    </svg>
    <span style="font-size: 20px; font-weight: 700; color: #F8FAFC;">Proyecto de computación</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption("Hallazgos y conclusiones operativas")

# ==============================================================================
# CONSULTA A LA BASE DE DATOS
# ==============================================================================
raiz = Path(__file__).resolve().parents[1]
ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"
if not ruta_base.is_file():
    ruta_base = raiz / "denormalizacion_vuelos.duckdb"

try:
    if not ruta_base.is_file():
        raise FileNotFoundError(f"No se encontró {ruta_base.name}")

    with duckdb.connect(str(ruta_base), read_only=True) as conexion:
        df_top_aero = conexion.execute(
            "SELECT * FROM lim_vuelos LIMIT 50000"
        ).fetchdf()

except (OSError, duckdb.Error) as error:
    st.error(f"No se pudo consultar la base de datos: {error}")
    st.stop()

# ==============================================================================
# CONTENIDO PRINCIPAL: CONCLUSIONES
# ==============================================================================
st.title("Conclusiones")
st.caption("Hallazgos del análisis de retrasos de la red aérea.")

col_origen = next(
    (c for c in df_top_aero.columns if "origen" in c.lower() or "departure_airport" in c.lower() or "salida_aero" in c.lower()),
    df_top_aero.columns[0]
)

df_top_aero["demora_calc"] = (
    pd.to_datetime(df_top_aero["salida_real"]) - pd.to_datetime(df_top_aero["salida_programada"])
).dt.total_seconds() / 60.0

resumen_aero = (
    df_top_aero.groupby(col_origen, as_index=False)
    .agg(demora_promedio=("demora_calc", "mean"), total_vuelos=("demora_calc", "count"))
)


def a_min_seg(minutos):
    """Convierte minutos decimales a 'X min Y s'."""
    m = int(minutos)
    s = round((minutos - m) * 60)
    if s == 60:
        m, s = m + 1, 0
    return f"{m} min {s} s"


def renderizar_top_aeropuertos(titulo_bloque, subtitulo_bloque, min_vuelos, key_chart):
    st.markdown(f"#### {titulo_bloque}")
    st.caption(subtitulo_bloque)

    ranking = (
        resumen_aero[resumen_aero["total_vuelos"] >= min_vuelos]
        .sort_values("demora_promedio", ascending=False)
        .head(10)
        .copy()
    )

    if ranking.empty:
        st.info(f"No hay aeropuertos con al menos {min_vuelos} vuelos en el conjunto de datos.")
        return

    ranking["etiqueta"] = ranking["demora_promedio"].apply(a_min_seg)
    ranking["demora_promedio"] = ranking["demora_promedio"].round(2)

    peor_aero = ranking.iloc[0][col_origen]
    peor_etiqueta = ranking.iloc[0]["etiqueta"]
    peor_vuelos = int(ranking.iloc[0]["total_vuelos"])

    st.info(
        f"**Mayor demora promedio:** el aeropuerto **{peor_aero}** encabeza el ranking "
        f"con **{peor_etiqueta}** por salida ({peor_vuelos:,} vuelos)."
    )

    fig_barras = px.bar(
        ranking.sort_values("demora_promedio", ascending=True),
        x="demora_promedio",
        y=col_origen,
        orientation="h",
        text="etiqueta",
        color="demora_promedio",
        color_continuous_scale="OrRd",
        hover_data={"total_vuelos": ":,", "etiqueta": False},
        labels={
            "demora_promedio": "Demora promedio (min)",
            col_origen: "Aeropuerto",
            "total_vuelos": "Vuelos analizados"
        }
    )
    fig_barras.update_traces(texttemplate="%{text}", textposition="outside")
    fig_barras.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=20, t=10, b=10),
        height=380,
        xaxis_title="Minutos promedio de retraso",
        xaxis_range=[0, ranking["demora_promedio"].max() * 1.35],
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_barras, use_container_width=True, key=key_chart)


#conclusiones finalees 
st.divider()

st.markdown("""Finalmente, se concluye que los retrasos de esta red aérea son un problema de eventos extremos, no de reloj ni de factores geográficos: casi todos los vuelos pierden unos pocos minutos, y un grupo reducido, pierde horas sin un patrón horario, espacial o semanal demostrable y realmente significativo.""")

st.markdown("""**1.** El promedio engaña: casi todos los vuelos estudiados se retrasan, pero por muy poco tiempo. El 95,7 % de las salidas aéreas tienen algún retraso, con una mediana de 3 min y un percentil 90 de 6 min. La media (12 min 12 s) es cuatro veces la mediana, ya que el 4,8 % de los vuelos (796) acumula el 76,4 % de todos los minutos perdidos (155.764 de 203.758 minutos). Sin ese grupo, la media se reduce a 3 min. La puntualidad de la red se decide evitando los eventos graves, no recortando minutos sueltos.""")

st.markdown("""**2.** La red tiene dos estados, normal o rota; el retraso “moderado” no existe. Ningún vuelo se retrasa entre 16 y 123 min. Esa ausencia es la firma de una falla (avería, cierre, espera de equipo o tripulación) y no de un sistema que se satura poco a poco, porque una saturación dejaría retrasos de todos los tamaños. La gravedad es real: 596 vuelos, uno de cada 28, llegan con 3 horas o más de retraso, el umbral desde el cual la normativa europea (European Parliament & Council of the European Union) reconoce compensación (solo como referencia de gravedad, no como aplicación jurídica a esta red).""")

st.markdown("""**3.** No hay efecto cascada horario: la hora de salida no explica los retrasos. Las medias por franja son casi idénticas (día: 12 min 2 s, tarde: 12 min 10 s, noche: 12 min 39 s) y el porcentaje de retrasos graves oscila solo entre 3,9 % y 5,3 % según la hora. La literatura ubica la propagación de retrasos en la rotación de aeronaves y en redes saturadas, información que esta base no contempla.""")

# Gráficos de retrasos por aeropuerto
col_50, col_100 = st.columns(2)
with col_50:
    renderizar_top_aeropuertos(
        "Terminales de flujo medio (mínimo 50 vuelos)",
        "Top 10 con el promedio más alto de minutos de retraso en salida.",
        min_vuelos=50,
        key_chart="top_aero_50"
    )
with col_100:
    renderizar_top_aeropuertos(
        "Terminales de alto tráfico (mínimo 100 vuelos)",
        "Top 10 con el promedio más alto de minutos de retraso en salida.",
        min_vuelos=100,
        key_chart="top_aero_100"
    )

st.markdown("""**4.** Los cuellos de botella son un efecto del filtro y de unas pocas rutas con mala racha, no aeropuertos deficientes. ULY (Ulyánovsk) lidera con 24 min 24 s, pero tiene 97 vuelos y diez de ellos son retrasos de varias horas; sin esos diez, es un aeropuerto común. Esos diez salen de dos rutas, ULY–RTW (7) y ULY–SVO (3); algo parecido ocurre en CSY–SVO, PES–TJM y OVS–KJA (5 retrasos graves en 31 vuelos cada una). Un aeropuerto regional con entre 2 y 8 destinos, no sufre “congestionamiento sostenido”, sino que sufre rutas puntuales con constantes inconvenientes.""")

st.markdown("""El ranking también cambia según el mínimo de vuelos que se exija. Con 50 vuelos como mínimo (79 de los 104 aeropuertos de origen), ULY lidera con 24 min 24 s; con 100 (49 aeropuertos, el 82 % de los vuelos), ULY sale de la lista y el primero es CSY con 16 min 31 s; con 200 (19 aeropuertos), es OVS con 15 min 17 s, y con 300 (los 10 mayores), es SVX con 14 min 42 s. De los diez aeropuertos del gráfico de la aplicación, solo tres (CSY, PES y OVS) siguen en el top 10 al subir el mínimo a 100, y la media del top 10 baja de 17 min 37 s a 15 min 3 s, 13 min 44 s y 12 min 17 s a medida que se exige más volumen, hasta acercarse al promedio de toda la red (12 min 12 s). La alerta de ULY es, por tanto, un resultado del corte de 50 vuelos: vista la red completa, ningún aeropuerto se separa de forma sostenida del resto.""")

st.markdown("""La geografía tampoco ordena el problema. Ocho de los diez aeropuertos están en la Rusia europea (zonas de Moscú y Samara), pero la demora media es prácticamente la misma a cualquier distancia. La Rusia europea promedia 12 min 28 s, y el resto del país (Urales, Siberia y el Lejano Oriente), 12 min 7 s; asimismo, los grandes centros de conexión (hubs) de Moscú y San Petersburgo (SVO, DME, VKO, LED) rinden como el resto (12 min 27 s frente a 12 min 5 s).""")

st.markdown("""**5.** En el aire no se gana ni se pierde tiempo: el retraso de salida se hereda prácticamente por completo, por lo que salir puntual garantiza casi completamente llegar a tiempo (con una tolerancia de 15 min). La correlación entre ambos retrasos es de r = 0,999 y la duración real del vuelo difiere de la programada en menos de un segundo (0,39 s) de promedio. Por otro lado, al condicionar esta correlación a los vuelos con menos de 15 min de retraso, la correlación es moderadamente menor (r = 0,73), lo que indica que esa primera correlación está inflada por la distancia enorme entre los vuelos normales (0–11 min) y los graves (124–277 min), que además son dos grupos separados sin nada en medio.""")

st.markdown("""En ruta, el único factor que pesa es la duración del trayecto: cuanto más largo es el vuelo, más fácil es que aterrice unos minutos desviado de lo programado, incluso si despegó puntual. Es lógico, porque más tiempo en el aire significa más ocasiones para que pequeños ajustes se acumulen. Se debe considerar que estas son desviaciones de minutos, que no tienen relación con los retrasos de horas que sí dañan a la red. Todo esto confirma que la puntualidad se juega en tierra (preparación, embarque y despacho), no en el aire.""")

st.subheader("Recomendaciones")
st.markdown("""Para futuros análisis, se recomienda reportar siempre la mediana, el percentil 90 y el porcentaje de retrasos graves junto a la media, así como ampliar el periodo de estudio y registrar tanto la matrícula de las aeronaves como los códigos de causa de las demoras. Asimismo, conviene modelar la probabilidad de sufrir un retraso superior a 15 min empleando la duración del vuelo, el aeropuerto y el día como variables explicativas.""")