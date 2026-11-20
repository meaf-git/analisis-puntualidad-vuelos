import streamlit as st
from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
import pydeck as pdk

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

st.set_page_config(
    page_title="Resultados y análisis",
    page_icon="📊",
    layout="wide"
)

st.title("Resultados y análisis de la puntualidad")

st.write(
    "En esta sección se presentan los resultados correspondientes "
    "a los cinco objetivos específicos de la investigación."
)

st.caption(
    "Período de estudio: 16 de julio al 15 de agosto de 2017."
)

st.divider()
raiz = Path(__file__).resolve().parents[1]
ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"

if not ruta_base.is_file():
    st.error("No se encontró la base DuckDB.")
    st.stop()


def consultar(sql, parametros=None):
    with duckdb.connect(
        str(ruta_base),
        read_only=True
    ) as conexion:
        return conexion.execute(
            sql,
            parametros or []
        ).fetchdf()

control = consultar("""
    SELECT
        COUNT(*) AS vuelos,
        MIN(CAST(salida_prog_local AS DATE)) AS desde,
        MAX(CAST(salida_prog_local AS DATE)) AS hasta
    FROM v_analisis_vuelos_limpios
""")

if int(control.loc[0, "vuelos"]) == 0:
    st.warning("No hay vuelos en la muestra limpia.")
    st.stop()

st.caption(
    f"Muestra limpia: {int(control.loc[0, 'vuelos']):,} vuelos"
)

umbral = 0

st.subheader("Indicadores generales")

total_registrados = consultar("""
    SELECT COUNT(*) AS total
    FROM vuelos
""").loc[0, "total"]

vuelos_analizados = int(control.loc[0, "vuelos"])

proporcion = (
    vuelos_analizados / total_registrados
) * 100
resumen_retrasos = consultar("""
    SELECT
        SUM(
            CASE
                WHEN retraso_salida_min > ?
                    OR retraso_llegada_min > ?
                THEN 1
                ELSE 0
            END
        ) AS vuelos_retrasados,

        AVG(
            CASE
                WHEN retraso_salida_min > ?
                THEN retraso_salida_min
            END
        ) AS promedio_salida,

        AVG(
            CASE
                WHEN retraso_llegada_min > ?
                THEN retraso_llegada_min
            END
        ) AS promedio_llegada

    FROM v_analisis_vuelos_limpios
""", [umbral, umbral, umbral, umbral]).loc[0]

cantidad_retrasados = int(
    resumen_retrasos["vuelos_retrasados"]
)

porcentaje_retrasados = (
    cantidad_retrasados / vuelos_analizados
) * 100
columna1, columna2, columna3 = st.columns(3)

with columna1:
    st.metric(
        "Vuelos registrados",
        f"{total_registrados:,.0f}",
        border=True
    )

    st.metric(
        "Vuelos analizados",
        f"{vuelos_analizados:,}",
        border=True
    )


with columna2:
    st.metric(
        "Proporción analizada",
        f"{proporcion:.2f} %",
        border=True
    )

    st.metric(
        "Vuelos retrasados",
        f"{porcentaje_retrasados:.2f} %",
        border=True
    )

with columna3:
    st.metric(
        "Demora media de salida",
        f'{resumen_retrasos["promedio_salida"]:.2f} min',
        border=True
    )

    st.metric(
        "Demora media de llegada",
        f'{resumen_retrasos["promedio_llegada"]:.2f} min',
        border=True
    )


st.caption(
    "Cada vuelo con retraso en salida, llegada o ambas "
    "se cuenta una sola vez. Los promedios se calculan "
    "entre los vuelos retrasados en cada fase."
)
with st.expander("Criterios del análisis", expanded=True):
    st.markdown(
        """
        - Se analizan los vuelos que completaron su recorrido:
          estado **Arrived**.
        - Se comparan los horarios programados con los reales.
        - Se considera retraso toda demora **mayor de 0 minutos** respecto al horario programado.
        - Las comparaciones por horario y día utilizan
          la salida programada local del aeropuerto de origen.
        """
    )

def resumir_por(campo):
    permitidos = {
        "franja_horaria",
        "origen",
        "destino",
        "modelo_aeronave",
        "dia_semana"
    }
    if campo not in permitidos:
        raise ValueError("Agrupación no permitida")

    return consultar(f"""
        SELECT
            {campo} AS grupo,
            COUNT(*) AS vuelos,
            SUM(CASE WHEN retraso_salida_min > ?
                THEN 1 ELSE 0 END) AS salida_retrasada,
            SUM(CASE WHEN retraso_llegada_min > ?
                THEN 1 ELSE 0 END) AS llegada_retrasada,
            AVG(CASE WHEN retraso_salida_min > ?
                THEN retraso_salida_min END) AS media_salida,
            AVG(CASE WHEN retraso_llegada_min > ?
                THEN retraso_llegada_min END) AS media_llegada
        FROM v_analisis_vuelos_limpios
        GROUP BY {campo}
        ORDER BY {campo}
    """, [umbral, umbral, umbral, umbral])

def mostrar_grupo(tabla, fase):
    tabla = tabla.copy()
    casos = fase + "_retrasada"
    media = "media_" + fase
    tabla["porcentaje"] = (
        100 * tabla[casos] / tabla["vuelos"]
    )

    st.dataframe(tabla.round(2), hide_index=True)
    st.caption("Frecuencia del retraso en porcentaje")
    st.bar_chart(
        tabla.set_index("grupo")[["porcentaje"]]
    )
    st.caption("Demora media entre retrasados en minutos")
    st.bar_chart(
        tabla.set_index("grupo")[[media]]
    )

pestanas = st.tabs(
    [
        "Objetivo 1",
        "Objetivo 2",
        "Objetivo 3",
        "Objetivo 4",
        "Objetivo 5",
    ]
)


def presentar_objetivo(titulo, objetivo, pregunta):
    st.header(titulo)
    st.write(objetivo)

    st.subheader("Pregunta de analisis")
    st.write(pregunta)


with pestanas[0]:
    presentar_objetivo(
        "Frecuencia y magnitud de los retrasos",
        (
            "Cuantificar la frecuencia y magnitud de los retrasos "
            "registrados en las salidas y llegadas de los vuelos, "
            "mediante la comparación entre los horarios programados "
            "y los horarios reales."
        ),
        "¿Cuántos vuelos se retrasaron y de cuántos minutos fueron "
        "sus retrasos de salida y llegada?"
    )

    datos_graficos = consultar("""
        SELECT
            retraso_salida_min,
            retraso_llegada_min
        FROM v_analisis_vuelos_limpios
    """)
    rangos = [
        "A tiempo",
        "Leve: 1–30 min",
        "Moderado: 31–60 min",
        "Severo: más de 60 min"
    ]

    colores = {
        "A tiempo": "#F6E39A",
        "Leve: 1–30 min": "#E6C975",
        "Moderado: 31–60 min": "#C9A956",
        "Severo: más de 60 min": "#C9A956"
    }

    columnas_histogramas = st.columns(2)

    fases = [
        ("retraso_salida_min", "salida"),
        ("retraso_llegada_min", "llegada")
    ]

    for posicion, (campo, fase) in enumerate(fases):
        clasificacion = pd.cut(
            datos_graficos[campo],
            bins=[
                -float("inf"),
                0,
                30,
                60,
                float("inf")
            ],
            labels=rangos
        )

        conteo = (
            clasificacion
            .value_counts(sort=False)
            .rename_axis("Rango")
            .reset_index(name="Vuelos")
        )

        grafico = px.bar(
            conteo,
            x="Rango",
            y="Vuelos",
            color="Rango",
            color_discrete_map=colores,
            category_orders={"Rango": rangos},
            text="Vuelos",
            title=f"Vuelos por rango de retraso de {fase}"
        )

        grafico.update_traces(
            textposition="outside",
            texttemplate="%{y:,.0f}",
            cliponaxis=False
        )

        grafico.update_layout(
            showlegend=False,
            xaxis_title=None,
            yaxis_title="Cantidad de vuelos",
            yaxis_range=[
                0,
                conteo["Vuelos"].max() * 1.15
            ],
            height=450
        )

        with columnas_histogramas[posicion]:
            st.plotly_chart(
                grafico,
                width="stretch",
                key=f"objetivo1_rangos_{fase}"
            )

    

    st.caption(
        "Valores negativos: anticipación. "
        "Cero: puntualidad exacta. "
        "Valores positivos: retraso. "
        "Se incluyen todos los vuelos analizados."
    )


    columnas_adicionales = st.columns(2)

    with columnas_adicionales[0]:
        estados = pd.DataFrame({
            "Estado": [
                "Puntual",
                "Retrasado"
            ],
            "Vuelos": [
                vuelos_analizados - cantidad_retrasados,
                cantidad_retrasados
            ]
        })

        grafico_puntualidad = px.pie(
            estados,
            names="Estado",
            values="Vuelos",
            hole=0.65,
            color="Estado",
            color_discrete_map={
                "Puntual": "#C9A956",
                "Retrasado": "#F6E39A"
            },
            title="Vuelos según su puntualidad"
        )

        grafico_puntualidad.update_traces(
            textinfo="percent",
            textposition="outside"
        )

        grafico_puntualidad.add_annotation(
            text=f"{vuelos_analizados:,}",
            x=0.5,
            y=0.5,
            showarrow=False,
            font_size=24
        )

        st.plotly_chart(
            grafico_puntualidad,
            use_container_width=True
        )

        st.caption(
            "Retrasado: supera el umbral en salida "
            "o llegada. Cada vuelo se cuenta una vez."
        )

    with columnas_adicionales[1]:
        grafico_dispersion = px.scatter(
            datos_graficos,
            x="retraso_salida_min",
            y="retraso_llegada_min",
            title="Relación entre retrasos de salida y llegada",
            labels={
                "retraso_salida_min":
                    "Diferencia de salida (min)",
                "retraso_llegada_min":
                    "Diferencia de llegada (min)"
            },
            color_discrete_sequence=["#C9A956"],
            opacity=0.5
        )

        st.plotly_chart(
            grafico_dispersion,
            use_container_width=True
        )

  
from plotly.subplots import make_subplots

with pestanas[1]:
    from plotly.subplots import make_subplots

    presentar_objetivo(
        "Retrasos según el horario programado",
        (
            "Analizar la incidencia de los retrasos según el horario "
            "programado de salida, con el propósito de identificar "
            "las franjas horarias que presentan mayor frecuencia "
            "y magnitud de retrasos."
        ),
        "¿Qué franjas de salida programada presentan mayor "
        "proporción de vuelos retrasados y demoras más largas?"
    )

    st.caption(
        "Una salida se considera retrasada si su demora supera 0 minutos. "
        "El promedio incluye solo esas salidas y la tasa usa todas las salidas "
        "analizadas en el grupo. La fecha y la franja corresponden al horario "
        "programado local del aeropuerto de origen."
    )

    dias_vis_obj2 = {
        "Lunes": "Lunes", "Martes": "Martes", "Miercoles": "Miércoles",
        "Jueves": "Jueves", "Viernes": "Viernes", "Sabado": "Sábado",
        "Domingo": "Domingo",
    }
    franjas_disponibles_obj2 = consultar("""
        SELECT DISTINCT franja_horaria
        FROM v_analisis_vuelos_limpios
        ORDER BY franja_horaria
    """)["franja_horaria"].tolist()

    fecha_min_obj2 = pd.Timestamp(control.loc[0, "desde"]).date()
    fecha_max_obj2 = pd.Timestamp(control.loc[0, "hasta"]).date()
    col_fecha, col_dia, col_franja = st.columns(3)
    fechas_obj2 = col_fecha.date_input(
        "Fecha", value=(fecha_min_obj2, fecha_max_obj2),
        min_value=fecha_min_obj2, max_value=fecha_max_obj2,
        format="DD/MM/YYYY", key="obj2_fecha"
    )
    dia_obj2 = col_dia.selectbox(
        "Día de la semana", [None, *dias_vis_obj2],
        format_func=lambda dia: dias_vis_obj2.get(dia, "Todos"), key="obj2_dia"
    )
    franja_obj2 = col_franja.selectbox(
        "Franja horaria", [None, *franjas_disponibles_obj2],
        format_func=lambda franja: franja or "Todas", key="obj2_franja"
    )
    # Al escoger solo un extremo, se muestra ese día.
    fechas_obj2 = fechas_obj2 or (fecha_min_obj2, fecha_max_obj2)

    # Los totales agrupan vuelos individuales en cada nivel de la matriz.
    datos_vis_obj2 = consultar("""
        SELECT
            COALESCE(franja_horaria, 'Total') AS franja,
            COALESCE(dia_semana, 'Total') AS dia,
            COUNT(retraso_salida_min) AS vuelos,
            COUNT(*) FILTER (WHERE retraso_salida_min > 0) AS retrasados,
            AVG(retraso_salida_min) FILTER (WHERE retraso_salida_min > 0) AS promedio,
            COUNT(*) FILTER (
                WHERE retraso_salida_min > 0 AND retraso_salida_min < 15
            ) AS retraso_menor,
            COUNT(*) FILTER (WHERE retraso_salida_min > 60) AS retraso_severo,
            COUNT(*) FILTER (WHERE retraso_salida_min <= 0) AS sin_retraso
        FROM v_analisis_vuelos_limpios
        WHERE CAST(salida_prog_local AS DATE) BETWEEN ? AND ?
          AND (? IS NULL OR dia_semana = ?)
          AND (? IS NULL OR franja_horaria = ?)
        GROUP BY GROUPING SETS (
            (franja_horaria, dia_semana),
            (franja_horaria),
            (dia_semana),
            ()
        )
    """, [
        fechas_obj2[0], fechas_obj2[-1], dia_obj2, dia_obj2, franja_obj2, franja_obj2
    ])
    datos_vis_obj2["porcentaje"] = (
        100 * datos_vis_obj2["retrasados"] / datos_vis_obj2["vuelos"]
    )
    franjas_vis_obj2 = datos_vis_obj2[
        (datos_vis_obj2["franja"] != "Total")
        & (datos_vis_obj2["dia"] == "Total")
    ].sort_values("franja").copy()

    def _numero_objetivo2(valor, decimales=2):
        return (
            f"{valor:,.{decimales}f}"
            .replace(",", "_").replace(".", ",").replace("_", ".")
        )

    total_obj2 = datos_vis_obj2.loc[
        (datos_vis_obj2["franja"] == "Total") & (datos_vis_obj2["dia"] == "Total")
    ].iloc[0]
    tarjetas_obj2 = [
        ("Retraso menor (>0 y <15 min)", "retraso_menor", 0, ""),
        ("Retraso severo (>60 min)", "retraso_severo", 0, ""),
        ("Sin retraso", "sin_retraso", 0, ""),
        ("% de salidas retrasadas", "porcentaje", 2, " %"),
        ("Promedio de retraso de salida", "promedio", 3, " min"),
    ]
    for columna, (titulo, campo, decimales, unidad) in zip(
        st.columns(len(tarjetas_obj2)), tarjetas_obj2
    ):
        valor = total_obj2[campo]
        valor_visible = (
            f"{_numero_objetivo2(valor, decimales)}{unidad}" if pd.notna(valor) else "—"
        )
        columna.metric(titulo, valor_visible, border=True)

    def _estilo_objetivo2(figura, altura=420):
        figura.update_layout(
            template="plotly_white",
            height=altura,
            paper_bgcolor="#F8FAFC",
            plot_bgcolor="#FFFFFF",
            font=dict(family="Arial, sans-serif", size=13, color="#243247"),
            margin=dict(l=30, r=35, t=40, b=110),
            legend=dict(
                orientation="h", yanchor="top", y=-0.27,
                xanchor="left", x=0, title_text="", font_size=11
            ),
            separators=",.",
            hoverlabel=dict(bgcolor="#FFFFFF", font_size=13)
        )
        figura.update_xaxes(showgrid=False, zeroline=False)
        figura.update_yaxes(gridcolor="#F6F7EF", zeroline=False)
        return figura

    def _fila_objetivo2(titulo, figura, interpretacion, clave, nota=None):
        st.markdown(f"#### {titulo}")
        grafico, texto = st.columns([2, 1], gap="large")
        with grafico:
            with st.container(border=True):
                es_grafico_de_barras = clave in {
                    "objetivo2_magnitud",
                    "objetivo2_porcentajes",
                    "objetivo2_frecuencia_tasa",
                    "objetivo2_dispersion",
                }
                if es_grafico_de_barras:
                    figura.update_layout(
                        paper_bgcolor="#021559",
                        plot_bgcolor="#021559",
                        font_color="#FFFFFF",
                        legend_font_color="#FFFFFF",
                        hoverlabel=dict(bgcolor="#021559", font_color="#FFFFFF"),
                    )
                    figura.update_xaxes(
                        tickfont_color="#FFFFFF",
                        title_font_color="#FFFFFF",
                    )
                    figura.update_yaxes(
                        tickfont_color="#FFFFFF",
                        title_font_color="#FFFFFF",
                        gridcolor="#35477E",
                    )
                    figura.update_traces(
                        outsidetextfont_color="#FFFFFF",
                        insidetextfont_color="#021559",
                        selector=dict(type="bar"),
                    )
                    figura.update_traces(
                        textfont_color="#FFFFFF",
                        selector=dict(type="scatter", mode="lines+markers+text"),
                    )
                st.plotly_chart(
                    figura,
                    width="stretch",
                    key=clave,
                    theme=None if es_grafico_de_barras else "streamlit",
                )
                if nota:
                    st.caption(nota)
        with texto:
            st.markdown("**Interpretación**")
            st.write(interpretacion)
        st.divider()

    if not total_obj2["vuelos"]:
        st.info("No hay vuelos para la fecha, el día y la franja seleccionados.")
    elif not total_obj2["retrasados"]:
        st.info("Las salidas de esta selección tienen una tasa de retrasos de 0 %.")
    else:
        orden_vis_obj2 = franjas_vis_obj2["franja"].tolist()
        dias_matriz_obj2 = [dia_obj2] if dia_obj2 else list(dias_vis_obj2)
        paleta_vis_obj2 = ["#F6E39A", "#E6C975", "#C9A956", "#139E8E"]
        colores_vis_obj2 = {
            franja: paleta_vis_obj2[i % len(paleta_vis_obj2)]
            for i, franja in enumerate(orden_vis_obj2)
        }
        etiquetas_vis_obj2 = {
            "franja": "Franja horaria",
            "promedio": "Retraso promedio de salida (min)",
            "porcentaje": "Salidas retrasadas (%)",
            "vuelos": "Total de vuelos",
            "retrasados": "Salidas retrasadas"
        }
        mayor_prom_vis_obj2 = franjas_vis_obj2.loc[
            franjas_vis_obj2["promedio"].idxmax()
        ]
        menor_prom_vis_obj2 = franjas_vis_obj2.loc[
            franjas_vis_obj2["promedio"].idxmin()
        ]
        mayor_tasa_vis_obj2 = franjas_vis_obj2.loc[
            franjas_vis_obj2["porcentaje"].idxmax()
        ]
        menor_tasa_vis_obj2 = franjas_vis_obj2.loc[
            franjas_vis_obj2["porcentaje"].idxmin()
        ]

        st.divider()

        # 1. Tabla con formato condicional, conservando sus totales ponderados.
        orden_matriz_obj2 = orden_vis_obj2[::-1]
        matriz_vis_obj2 = datos_vis_obj2.pivot(
            index="franja", columns="dia", values="promedio"
        ).reindex(
            index=orden_matriz_obj2 + ["Total"],
            columns=dias_matriz_obj2 + ["Total"]
        ).rename(columns=dias_vis_obj2)
        dias_matriz_obj2 = [dias_vis_obj2[dia] for dia in dias_matriz_obj2]
        matriz_vis_obj2.index.name = "Franja horaria"
        matriz_vis_obj2.columns.name = None
        celdas_vis_obj2 = matriz_vis_obj2.loc[orden_matriz_obj2, dias_matriz_obj2]
        minimo_vis_obj2 = celdas_vis_obj2.min().min()
        amplitud_vis_obj2 = celdas_vis_obj2.max().max() - minimo_vis_obj2

        def _color_celda_objetivo2(valor):
            if pd.isna(valor):
                return ""
            posicion = (valor - minimo_vis_obj2) / amplitud_vis_obj2 if amplitud_vis_obj2 else 0.5
            tonos = ["#D6EEE7", "#E8F0D2", "#FFF1BD", "#FFD5AB", "#F4A6A6"]
            indice = max(0, min(4, int(posicion * 5)))
            return f"background-color: {tonos[indice]}; color: #1E293B"

        st.markdown("#### Retraso promedio por día y franja horaria")
        grafico, texto = st.columns([2, 1], gap="large")
        with grafico:
            with st.container(border=True):
                st.dataframe(
                    matriz_vis_obj2.style.apply(
                        lambda columna: columna.map(_color_celda_objetivo2),
                        subset=pd.IndexSlice[orden_matriz_obj2, dias_matriz_obj2]
                    ).set_properties(
                        subset=pd.IndexSlice[["Total"], :],
                        **{"font-weight": "bold", "background-color": "#E8EEF8"}
                    ).set_properties(
                        subset=pd.IndexSlice[:, ["Total"]],
                        **{"font-weight": "bold"}
                    ).format(precision=3, decimal=",", na_rep="—"),
                    width="stretch", hide_index=False
                )
        with texto:
            st.markdown("**Interpretación**")
            valores_vis_obj2 = celdas_vis_obj2.stack().dropna()
            if not valores_vis_obj2.empty:
                franja_max_vis_obj2, dia_max_vis_obj2 = valores_vis_obj2.idxmax()
                st.write(
                    f"La combinación {dia_max_vis_obj2} / {franja_max_vis_obj2} "
                    f"registra el mayor promedio: "
                    f"{_numero_objetivo2(valores_vis_obj2.max(), 3)} minutos. "
                    "Se promedian únicamente las demoras mayores de 0 min. "
                    "Los colores cálidos destacan promedios más altos. "
                    "Cada total se calcula a partir de los vuelos del grupo."
                )
        st.divider()

        # 2. Columnas: magnitud del retraso promedio.
        magnitud_objetivo2 = px.bar(
            franjas_vis_obj2, x="franja", y="promedio", color="franja",
            text="promedio", color_discrete_map=colores_vis_obj2,
            labels=etiquetas_vis_obj2, category_orders={"franja": orden_vis_obj2}
        )
        magnitud_objetivo2.update_traces(
            texttemplate="%{y:.3f}", textposition="outside", cliponaxis=False,
            marker_line_width=0, width=0.5
        )
        _estilo_objetivo2(magnitud_objetivo2)
        magnitud_objetivo2.update_yaxes(
            range=[0, franjas_vis_obj2["promedio"].max() * 1.18]
        )
        magnitud_objetivo2.update_xaxes(title_text="")
        _fila_objetivo2(
            "Magnitud del retraso por franja horaria", magnitud_objetivo2,
            f"La franja {mayor_prom_vis_obj2['franja']} registra el mayor "
            f"promedio: {_numero_objetivo2(mayor_prom_vis_obj2['promedio'], 3)} min. "
            f"La franja {menor_prom_vis_obj2['franja']} presenta el menor: "
            f"{_numero_objetivo2(menor_prom_vis_obj2['promedio'], 3)} min. "
            "Estos promedios corresponden exclusivamente a los vuelos "
            "con demora de salida mayor de 0 min.",
            "objetivo2_magnitud"
        )

        # 3. Barras horizontales, ordenadas por tasa de mayor a menor.
        tasas_vis_obj2 = franjas_vis_obj2.sort_values("porcentaje", ascending=False)
        porcentajes_objetivo2 = px.bar(
            tasas_vis_obj2, x="porcentaje", y="franja", orientation="h",
            color="franja", text="porcentaje",
            color_discrete_map=colores_vis_obj2, labels=etiquetas_vis_obj2,
            category_orders={"franja": tasas_vis_obj2["franja"].tolist()}
        )
        porcentajes_objetivo2.update_traces(
            texttemplate="%{x:.2f} %", textposition="inside",
            insidetextanchor="end", textfont=dict(color="white", size=14),
            marker_line_width=0, width=0.55
        )
        _estilo_objetivo2(porcentajes_objetivo2, 350)
        porcentajes_objetivo2.update_xaxes(
            range=[0, 105], ticksuffix=" %", dtick=20,
            title_text="Salidas retrasadas (%)"
        )
        porcentajes_objetivo2.update_yaxes(title_text="", showgrid=False, autorange="reversed")
        _fila_objetivo2(
            "Porcentaje de vuelos retrasados por franja", porcentajes_objetivo2,
            f"La mayor tasa corresponde a {mayor_tasa_vis_obj2['franja']}: "
            f"{_numero_objetivo2(mayor_tasa_vis_obj2['porcentaje'])} %. "
            f"La menor corresponde a {menor_tasa_vis_obj2['franja']}: "
            f"{_numero_objetivo2(menor_tasa_vis_obj2['porcentaje'])} %. "
            "El denominador es el total de vuelos de cada franja.",
            "objetivo2_porcentajes"
        )

        # 4. Columnas y curva. Orden por cantidad: tarde, día, noche.
        frecuencia_vis_obj2 = franjas_vis_obj2.sort_values("retrasados", ascending=False)
        combinado_objetivo2 = make_subplots(specs=[[{"secondary_y": True}]])
        combinado_objetivo2.add_trace(
            go.Bar(
                x=frecuencia_vis_obj2["franja"], y=frecuencia_vis_obj2["retrasados"],
                name="Salidas retrasadas", marker_color="#F6E39A",
                width=0.55, text=frecuencia_vis_obj2["retrasados"],
                texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False,
                hovertemplate="%{x}<br>Salidas retrasadas: %{y:,.0f}<extra></extra>"
            ), secondary_y=False
        )
        combinado_objetivo2.add_trace(
            go.Scatter(
                x=frecuencia_vis_obj2["franja"], y=frecuencia_vis_obj2["porcentaje"],
                name="Tasa de salidas retrasadas", mode="lines+markers+text",
                text=frecuencia_vis_obj2["porcentaje"].map(
                    lambda tasa: f"{_numero_objetivo2(tasa)} %"
                ),
                textposition="top center",
                line=dict(color="#9670BF", width=3, shape="spline", smoothing=1.0),
                marker=dict(size=8, color="#9670BF", line=dict(color="white", width=1)),
                hovertemplate="%{x}<br>Tasa: %{y:.2f} %<extra></extra>"
            ), secondary_y=True
        )
        _estilo_objetivo2(combinado_objetivo2, 450)
        combinado_objetivo2.update_layout(hovermode="x unified")
        combinado_objetivo2.update_xaxes(
            categoryorder="array", categoryarray=frecuencia_vis_obj2["franja"].tolist()
        )
        combinado_objetivo2.update_yaxes(
            title_text="Salidas retrasadas", secondary_y=False,
            range=[0, max(1, frecuencia_vis_obj2["retrasados"].max() * 1.15)]
        )
        tasa_min_vis_obj2 = frecuencia_vis_obj2["porcentaje"].min()
        tasa_max_vis_obj2 = frecuencia_vis_obj2["porcentaje"].max()
        margen_tasa_vis_obj2 = max(0.04, (tasa_max_vis_obj2 - tasa_min_vis_obj2) * 0.18)
        combinado_objetivo2.update_yaxes(
            title_text="Vuelos con retraso (%)", secondary_y=True,
            range=[max(0, tasa_min_vis_obj2 - margen_tasa_vis_obj2),
                   min(100, tasa_max_vis_obj2 + margen_tasa_vis_obj2)],
            tickformat=".2f", ticksuffix=" %", showgrid=False
        )
        detalle_tasas_vis_obj2 = "; ".join(
            f"{fila.franja}: {_numero_objetivo2(fila.porcentaje)} %"
            for fila in frecuencia_vis_obj2.itertuples()
        )
        mayor_cant_vis_obj2 = frecuencia_vis_obj2.iloc[0]
        _fila_objetivo2(
            "Frecuencia y tasa de retrasos por franja horaria", combinado_objetivo2,
            f"{mayor_cant_vis_obj2['franja']} concentra la mayor cantidad: "
            f"{_numero_objetivo2(mayor_cant_vis_obj2['retrasados'], 0)} vuelos. "
            f"La línea representa las tasas: {detalle_tasas_vis_obj2}. "
            "La franja con más vuelos retrasados no necesariamente tiene "
            "la mayor proporción de retrasos.",
            "objetivo2_frecuencia_tasa",
            "Barras: eje izquierdo. Curva: eje derecho ampliado. "
            "Los marcadores indican las tasas observadas en cada franja."
        )

        # 5. Burbujas: promedio y cantidad de salidas retrasadas.
        dispersion_objetivo2 = px.scatter(
            franjas_vis_obj2, x="promedio", y="retrasados", color="franja",
            size="retrasados", size_max=28, color_discrete_map=colores_vis_obj2,
            labels=etiquetas_vis_obj2, category_orders={"franja": orden_vis_obj2},
            hover_data={"vuelos": True, "porcentaje": ":.2f", "promedio": ":.3f"}
        )
        dispersion_objetivo2.update_traces(
            marker=dict(opacity=0.9, line=dict(color="white", width=2))
        )
        _estilo_objetivo2(dispersion_objetivo2)
        dispersion_objetivo2.update_xaxes(
            showgrid=True, gridcolor="#E8EDF4"
        )
        dispersion_objetivo2.update_yaxes(
            range=[0, max(1, franjas_vis_obj2["retrasados"].max() * 1.18)]
        )
        _fila_objetivo2(
            "Demora promedio y cantidad de salidas retrasadas", dispersion_objetivo2,
            "Cada burbuja representa una franja. El eje horizontal muestra el "
            "retraso promedio de las salidas retrasadas. El eje vertical y el "
            "tamaño de la burbuja muestran cuántas salidas se retrasaron. "
            f"{mayor_cant_vis_obj2['franja']} reúne más vuelos retrasados, "
            f"mientras que {mayor_prom_vis_obj2['franja']} registra el mayor promedio.",
            "objetivo2_dispersion"
        )

####################################################################################################################
#### objetivo 3 #### PROMEDIO DE RETRASO DE SALIDA ####
with pestanas[2]:
    presentar_objetivo(
        "Comparación entre aeropuertos",
        (
            "Comparar el comportamiento de los retrasos entre "
            "los diferentes aeropuertos de origen y destino, "
            "a fin de identificar diferencias en el cumplimiento "
            "de los horarios programados."
        ),
        "¿Cómo varían los retrasos de salida entre los orígenes "
        "y los retrasos de llegada entre los destinos?"
    )
    st.markdown ("""Los retrasos de salida en los orígenes se concentran en los principales 
    centros urbanos con alto volumen de vuelos, aunque las demoras más prolongadas ocurren 
    de forma puntual en aeropuertos secundarios con cuellos de botella operativos o climáticos. 
    En contraste, los retrasos de llegada en los destinos registran sus mayores promedios principalmente 
    en aeropuertos regionales de menor tráfico, lo que indica que la impuntualidad en los destinos responde 
    más a restricciones de infraestructura local y clima extremo que al tamaño de la red.""",unsafe_allow_html=True)

    st.subheader ("Promedio de retraso en salida (Aeropuerto)")
    ####################################################################################
    col_jesu, col_oliver = st.columns (2)
    ####################################################################################
    #### grafico del mapa ####
    with col_jesu:
        datos_mapa = consultar("""
            SELECT
                a.nombre AS nombre_aeropuerto,
                v.origen AS ciudad_origen,
                a.latitud AS lat,
                a.longitud AS lon,
                COUNT(*) AS total_vuelos,
                ROUND(AVG(v.retraso_salida_min), 2) AS promedio_retraso_salida
            FROM v_analisis_vuelos_limpios v
            JOIN aeropuertos a ON v.origen = a.codigo
            WHERE v.estado = 'Arrived' AND v.retraso_salida_min > 0
            GROUP BY v.origen, a.latitud, a.longitud, a.nombre
        """)

        if not datos_mapa.empty:
            # 1. Ajustamos el radio proporcional al total de vuelos salidos
            # Multiplicamos por un factor en metros para que el radio refleje el volumen real en el mapa
            datos_mapa["radio"] = datos_mapa["total_vuelos"] * 600
            min_retraso = datos_mapa["promedio_retraso_salida"].min()
            max_retraso = datos_mapa["promedio_retraso_salida"].max()

        # 2. Asignamos colores en formato RGBA basados en el retraso promedio (escala tipo Viridis)
            def color_personalizado(val):
                if pd.isna(val) or max_retraso == min_retraso:
                    t = 0.0
                else:
                    t = (val - min_retraso) / (max_retraso - min_retraso)
                    t = max(0.0, min(1.0, t)) # Normalizar entre 0 y 1
                
                # Interpolar entre #A0D1FF (160, 209, 255) y #A38600 (163, 134, 0)
                r = int(160 + t * (163 - 160))
                g = int(209 + t * (134 - 209))
                b = int(255 + t * (0 - 255))
                return [r, g, b, 200] # RGBA con opacidad

            datos_mapa["color_rgb"] = datos_mapa["promedio_retraso_salida"].apply(color_personalizado)
            datos_mapa["promedio_retraso_salida_fmt"] = datos_mapa["promedio_retraso_salida"].round(2)

        # 3. Configuramos la capa de dispersión geográfica en PyDeck
            capa_aeropuertos = pdk.Layer(
                "ScatterplotLayer",
                data=datos_mapa,
                get_position="[lon, lat]",
                get_radius="radio",          # Proporcional a los vuelos salidos
                get_fill_color="color_rgb",  # Color según los minutos de retraso promedio
                pickable=True,
                auto_highlight=True,
                radius_min_pixels=3,         # Tamaño mínimo para aeropuertos pequeños
                radius_max_pixels=15,        # Tamaño máximo para los hubs principales
                stroked=True,
                get_line_color=[255, 255, 255, 200],
                line_width_min_pixels=1
            )

            # 4. Centramos la cámara en la región de Rusia y Europa oriental
            punto_medio = pdk.ViewState(
                latitude=60.0,
                longitude=85.0,
                zoom=2.8,
                pitch=0
            )

            # 5. Tooltip interactivo idéntico al comportamiento en Power BI
            tooltip_config = {
                "html": "<b>Aeropuerto:</b> {nombre_aeropuerto}<br/>"
                        "<b>Total vuelos con salida registrada:</b> {total_vuelos}<br/>"
                        "<b>Retraso Promedio:</b> {promedio_retraso_salida_fmt} min",
                "style": {
                    "backgroundColor": "#FFFFFF",
                    "color": "#1E293B",
                    "fontFamily": "Arial, sans-serif",
                    "padding": "10px",
                    "borderRadius": "6px"
                }
            }

            # Construcción final del objeto de mapa
            mapa_pydeck = pdk.Deck(
                layers=[capa_aeropuertos],
                initial_view_state=punto_medio,
                map_style="light",  # Estilo de mapa claro, limpio y profesional (tipo Carto Positron / Power BI)
                tooltip=tooltip_config
            )

            with st.container(border=True):
                st.pydeck_chart(mapa_pydeck, use_container_width=True)
                st.caption(
                    "El tamaño de los círculos es **proporcional al total de vuelos salidos**, "
                    "y el color representa el promedio de retraso en la salida (minutos)."
                )
        else:
            st.warning("No hay datos geográficos disponibles para mostrar el mapa.")
    #############################################################################################################################
    #### INTERPRETACION ####
        with col_oliver:

            st.markdown("**Interpretación**")
            st.markdown(
            """Los principales aeropuertos de los grandes centros urbanos concentran la 
            mayor parte de las salidas, lo que evidencia una fuerte correlación entre 
            el volumen de vuelos y la magnitud de la red. Aunque las terminales situadas 
            en la cima del ranking registran los promedios de retraso más altos, las demoras 
            más prolongadas no siempre coinciden con los aeropuertos de mayor tráfico, 
            lo que apunta a la existencia de cuellos de botella operativos o meteorológicos 
            en regiones específicas."""
            ,unsafe_allow_html=True
            )

            with st.expander("**TABLA DE PROMEDIOS DE RETRASO DE SALIDA**", expanded=False):
                df_tabla = consultar("""
                    SELECT
                        a.nombre AS nombre_aeropuerto,
                        COUNT(*) AS "Total vuelos con salida registrada",
                        ROUND(AVG(v.retraso_salida_min), 2) AS "Promedio Retraso Salida (Min)"
                    FROM v_analisis_vuelos_limpios v
                    JOIN aeropuertos a ON v.origen = a.codigo
                    WHERE v.estado = 'Arrived' AND v.retraso_salida_min > 0
                    GROUP BY a.nombre, v.origen, a.latitud, a.longitud
                    ORDER BY "Promedio Retraso Salida (Min)" DESC
                """)
                st.dataframe(df_tabla, use_container_width=True, hide_index=True, height=283)
##################################################################################################################################
    st.divider ()
    ##################################################################################################################################
    #### PROMEDIO DE RETRASO DE LLEGADA ####
    st.subheader ("Promedio de retraso en ""llegada"" (Aeropuerto)")
    col_haliburton, col_rudy = st.columns (2)
    ##################################################################################################################################
    with col_haliburton:
            datos_mapi = consultar("""
            SELECT
                a.nombre AS nombre_aeropuerto,
                v.origen AS ciudad_origen,
                a.latitud AS lat,
                a.longitud AS lon,
                COUNT(*) AS total_vuelos,
                ROUND(AVG(v.retraso_llegada_min), 2) AS promedio_retraso_llegada
            FROM v_analisis_vuelos_limpios v
            JOIN aeropuertos a ON v.origen = a.codigo
            WHERE v.estado = 'Arrived' AND v.retraso_llegada_min > 0
            GROUP BY v.origen, a.latitud, a.longitud, a.nombre
        """)

            if not datos_mapi.empty:
                # 1. Ajustamos el radio proporcional al total de vuelos salidos
                # Multiplicamos por un factor en metros para que el radio refleje el volumen real en el mapa
                datos_mapi["radio"] = datos_mapi["total_vuelos"] * 600
                min_retraso = datos_mapi["promedio_retraso_llegada"].min()
                max_retraso = datos_mapi["promedio_retraso_llegada"].max()

            # 2. Asignamos colores en formato RGBA basados en el retraso promedio (escala tipo Viridis)
                def color_personalizado(val):
                    if pd.isna(val) or max_retraso == min_retraso:
                        t = 0.0
                    else:
                        t = (val - min_retraso) / (max_retraso - min_retraso)
                        t = max(0.0, min(1.0, t)) # Normalizar entre 0 y 1
                
                    # Interpolar entre #A0D1FF (160, 209, 255) y #A38600 (163, 134, 0)
                    r = int(160 + t * (163 - 160))
                    g = int(209 + t * (134 - 209))
                    b = int(255 + t * (0 - 255))
                    return [r, g, b, 200] # RGBA con opacidad

                datos_mapi["color_rgb"] = datos_mapi["promedio_retraso_llegada"].apply(color_personalizado)
                datos_mapi["promedio_retraso_llegada_fmt"] = datos_mapi["promedio_retraso_llegada"].round(2)

            # 3. Configuramos la capa de dispersión geográfica en PyDeck
                capa_aeropuertos = pdk.Layer(
                    "ScatterplotLayer",
                    data=datos_mapi,
                    get_position="[lon, lat]",
                    get_radius="radio",          # Proporcional a los vuelos salidos
                    get_fill_color="color_rgb",  # Color según los minutos de retraso promedio
                    pickable=True,
                    auto_highlight=True,
                    radius_min_pixels=3,         # Tamaño mínimo para aeropuertos pequeños
                    radius_max_pixels=15,        # Tamaño máximo para los hubs principales
                    stroked=True,
                    get_line_color=[255, 255, 255, 200],
                    line_width_min_pixels=1
                )

                # 4. Centramos la cámara en la región de Rusia y Europa oriental
                punto_medio = pdk.ViewState(
                    latitude=60.0,
                    longitude=85.0,
                    zoom=2.8,
                    pitch=0
                )

                # 5. Tooltip interactivo idéntico al comportamiento en Power BI
                tooltip_config = {
                    "html": "<b>Aeropuerto:</b> {nombre_aeropuerto}<br/>"
                            "<b>Total uelos con salida registrada:</b> {total_vuelos}<br/>"
                            "<b>Retraso Promedio:</b> {promedio_retraso_llegada_fmt} min",
                    "style": {
                        "backgroundColor": "#FFFFFF",
                        "color": "#1E293B",
                        "fontFamily": "Arial, sans-serif",
                        "padding": "10px",
                        "borderRadius": "6px"
                    }
                }

                # Construcción final del objeto de mapa
                mapa_pydeck = pdk.Deck(
                    layers=[capa_aeropuertos],
                    initial_view_state=punto_medio,
                    map_style="light",  # Estilo de mapa claro, limpio y profesional (tipo Carto Positron / Power BI)
                    tooltip=tooltip_config
                )

                with st.container(border=True):
                    st.pydeck_chart(mapa_pydeck, use_container_width=True)
                    st.caption(
                        "El tamaño de los círculos es **proporcional al total de vuelos salidos**, "
                        "y el color representa el promedio de retraso en la llegada (minutos)."
                    )
            else:
                st.warning("No hay datos geográficos disponibles para mostrar el mapa.")
        #############################################################################################################################
        #### INTERPRETACION ####
            with col_rudy:

                st.markdown("**Interpretación**")
                st.markdown(
                """Los aeropuertos secundarios o de menor volumen operativo suelen concentrar los mayores 
            promedios de retraso en la llegada, lo que evidencia que la impuntualidad no 
            depende exclusivamente de la magnitud del tráfico total. Aunque terminales 
            con un número reducido de operaciones como Ugolny o Ignatyevo encabezan la 
            lista con las demoras más elevadas del sistema, este comportamiento sugiere la 
            presencia de factores meteorológicos adversos o limitaciones en la infraestructura 
            regional que afectan la fluidez de sus arribos."""
                ,unsafe_allow_html=True
                )

                with st.expander("**TABLA DE PROMEDIOS DE RETRASO DE LLEGADA**", expanded=False):
                    df_tabla = consultar("""
                    SELECT
                        a.nombre AS nombre_aeropuerto,
                        COUNT(*) AS "Total vuelos con salida registrada",
                        ROUND(AVG(v.retraso_llegada_min), 2) AS "Promedio Retraso Llegada (Min)"
                    FROM v_analisis_vuelos_limpios v
                    JOIN aeropuertos a ON v.destino = a.codigo
                    WHERE v.estado = 'Arrived' 
                        AND v.retraso_llegada_min > 0
                    GROUP BY a.nombre
                    ORDER BY "Promedio Retraso Llegada (Min)" DESC
                """)
                    st.dataframe(df_tabla, use_container_width=True, hide_index=True, height=283)

    ############################################################################
with pestanas[3]:
    presentar_objetivo(
        "Comparación según la aeronave",
        (
            "Comparar la frecuencia y magnitud de los retrasos "
            "según el tipo de aeronave asignada a los vuelos, "
            "con el propósito de identificar diferencias "
            "en el cumplimiento de los horarios programados."
        ),
        "¿Qué diferencias de frecuencia y magnitud de retrasos "
        "se observan entre los modelos de aeronave?"
    )
    st.caption(
        "Filtros de control para el análisis de flotas y modelos de aeronave."
    )

    dias_vis_obj4 = {
        "Lunes": "Lunes", "Martes": "Martes", "Miercoles": "Miércoles",
        "Jueves": "Jueves", "Viernes": "Viernes", "Sabado": "Sábado", "Domingo": "Domingo"
    }
    
    franjas_disp_obj4 = consultar("""
        SELECT DISTINCT franja_horaria 
        FROM v_analisis_vuelos_limpios 
        WHERE franja_horaria IS NOT NULL 
        ORDER BY franja_horaria
    """)["franja_horaria"].tolist()

    modelos_disp_obj4 = consultar("""
        SELECT DISTINCT modelo_aeronave 
        FROM v_analisis_vuelos_limpios 
        WHERE modelo_aeronave IS NOT NULL 
        ORDER BY modelo_aeronave
    """)["modelo_aeronave"].tolist()

    fecha_min_obj4 = pd.Timestamp(control.loc[0, "desde"]).date()
    fecha_max_obj4 = pd.Timestamp(control.loc[0, "hasta"]).date()

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    fechas_obj4 = col_f1.date_input(
        "Rango de Fechas", value=(fecha_min_obj4, fecha_max_obj4),
        min_value=fecha_min_obj4, max_value=fecha_max_obj4,
        format="DD/MM/YYYY", key="obj4_fecha"
    )
    dia_obj4 = col_f2.selectbox(
        "Día de la semana", [None, *dias_vis_obj4],
        format_func=lambda d: dias_vis_obj4.get(d, "Todas"), key="obj4_dia"
    )
    franja_obj4 = col_f3.selectbox(
        "Franja Horaria", [None, *franjas_disp_obj4],
        format_func=lambda f: f or "Todas", key="obj4_franja"
    )
    modelo_obj4 = col_f4.selectbox(
        "Modelo de Aeronave", [None, *modelos_disp_obj4],
        format_func=lambda m: m or "Todas", key="obj4_modelo"
    )
    
    fechas_obj4 = fechas_obj4 or (fecha_min_obj4, fecha_max_obj4)

    datos_obj4 = consultar("""
        SELECT
            modelo_aeronave AS modelo,
            COUNT(*) AS total_vuelos,
            CAST(SUM(CASE WHEN demora_llegada_15 = 1 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS frec_llegada,
            CAST(SUM(CASE WHEN demora_salida_15 = 1 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS frec_salida,
            SUM(COALESCE(retraso_llegada_min, 0)) / COUNT(*) AS prom_llegada_min2,
            SUM(COALESCE(retraso_salida_min, 0)) / COUNT(*) AS prom_salida_min2
        FROM v_analisis_vuelos_limpios
        WHERE modelo_aeronave IS NOT NULL
          AND CAST(salida_prog_local AS DATE) BETWEEN ? AND ?
          AND (? IS NULL OR dia_semana = ?)
          AND (? IS NULL OR franja_horaria = ?)
          AND (? IS NULL OR modelo_aeronave = ?)
        GROUP BY modelo_aeronave
        ORDER BY frec_llegada DESC
    """, [
        fechas_obj4[0], fechas_obj4[-1],
        dia_obj4, dia_obj4,
        franja_obj4, franja_obj4,
        modelo_obj4, modelo_obj4
    ])

    if datos_obj4.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados en el Objetivo 4.")
    else:
        st.divider()

        # grafico
        st.markdown("#### Promedio Minutos Retraso Llegada y Promedio Minutos Retraso Salida por modelo")
        col_g1, col_i1 = st.columns([1.3, 0.7], gap="large")
        
        with col_g1:
            with st.container(border=True):
                fig_sup = px.bar(
                    datos_obj4,
                    x="modelo",
                    y=["frec_llegada", "frec_salida"],
                    barmode="group",
                    labels={"value": "", "modelo": "", "variable": ""},
                    color_discrete_map={
                        "frec_llegada": "#C9A956",
                        "frec_salida": "#F6E39A"
                    }
                )
                fig_sup.for_each_trace(lambda t: t.update(
                    name="Promedio Minutos Retraso Llegada" if t.name == "frec_llegada" else "Promedio Minutos Retraso Salida"
                ))
                fig_sup.update_layout(
                    template="plotly_white",
                    height=420,
                    margin=dict(b=120),
                    yaxis=dict(tickformat=".0%", showgrid=True, gridcolor="#eee"),
                    xaxis=dict(showgrid=False, tickangle=-25),
                    legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="left", x=0)
                )
                st.plotly_chart(fig_sup, use_container_width=True)

        with col_i1:
            st.markdown("##### Interpretación")
            st.markdown(
                "Se observa una tendencia consistente en los distintos modelos de aeronave donde las frecuencias de retraso "
                "en origen y destino mantienen proporciones muy cercanas. Los modelos con mayor índice de afectación "
                "superan ligeramente el umbral superior, evidenciando cuellos de botella operativos en determinados tipos de flota."
            )

        st.divider()

       # segundo grafico
        col_tabla_obj4, col_i_tabla = st.columns([1.1, 0.9], gap="large")

        with col_tabla_obj4:
            st.markdown("#### Detalle por Modelo de Aeronave")
            tabla_df = datos_obj4.sort_values("prom_llegada_min2", ascending=True).copy()
            
            total_v = int(tabla_df["total_vuelos"].sum())
            frec_total = (tabla_df["frec_llegada"] * tabla_df["total_vuelos"]).sum() / total_v
            prom_total = (tabla_df["prom_llegada_min2"] * tabla_df["total_vuelos"]).sum() / total_v

            tabla_mostrar = pd.DataFrame({
                "modelo": tabla_df["modelo"],
                "Total Vuelos": tabla_df["total_vuelos"].astype(int).astype(str),
                "% Frecuencia Retraso Llegada": tabla_df["frec_llegada"].map(lambda x: f"{x:.2f}".replace(".", ",")),
                "Promedio Minutos Retraso Llegada2": tabla_df["prom_llegada_min2"].round(0).astype(int).astype(str) + " min"
            })

            fila_total = pd.DataFrame([{
                "modelo": "Total",
                "Total Vuelos": str(total_v),
                "% Frecuencia Retraso Llegada": f"{frec_total:.2f}".replace(".", ","),
                "Promedio Minutos Retraso Llegada2": f"{round(prom_total):.0f} min"
            }])

            tabla_mostrar = pd.concat([tabla_mostrar, fila_total], ignore_index=True)

            def aplicar_estilo_tabla(row):
                if row.name == len(tabla_mostrar) - 1:
                    return ['background-color: #1E293B; color: white; font-weight: bold'] * len(row)
                elif row.name % 2 == 0:
                    return ['background-color: #F6E39A; color: white'] * len(row)
                else:
                    return ['background-color: transparent; color: white'] * len(row)

            st.dataframe(
                tabla_mostrar.style.apply(aplicar_estilo_tabla, axis=1),
                use_container_width=True,
                hide_index=True,
                height=360
            )

        with col_i_tabla:
            st.markdown("##### Interpretación")
            st.markdown(
                "El desglose por modelo permite identificar que aeronaves con mayor volumen operativo "
                "concentran la mayor cantidad de registros, permitiendo evaluar el impacto de los retrasos por cada tipo de flota."
            )

        st.divider()

        col_graf_obj4, col_i2 = st.columns([1.1, 0.9], gap="large")

        with col_graf_obj4:
            st.markdown("#### % Frecuencia Retraso Llegada y Salida por modelo")
            with st.container(border=True):
                fig_freq_obj4 = px.bar(
                    datos_obj4.sort_values("frec_llegada", ascending=True),
                    y="modelo",
                    x=["frec_llegada", "frec_salida"],
                    barmode="group",
                    orientation="h",
                    labels={"value": "", "modelo": "", "variable": ""},
                    color_discrete_map={
                        "frec_llegada": "#C9A956",
                        "frec_salida": "#F6E39A"
                    }
                )
                fig_freq_obj4.for_each_trace(lambda t: t.update(
                    name="% Frecuencia Retraso Llegada" if t.name == "frec_llegada" else "% Frecuencia Retraso Salida"
                ))
                fig_freq_obj4.update_layout(
                    template="plotly_white",
                    height=360,
                    xaxis=dict(
                        tickformat=".0%", 
                        showgrid=True, 
                        gridcolor="#C9A956", 
                        griddash="solid",
                        dtick=0.01
                    ),
                    yaxis=dict(showgrid=False),
                    legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="left", x=0)
                )
                st.plotly_chart(fig_freq_obj4, use_container_width=True)

        with col_i2:
            st.markdown("##### Interpretación")
            st.markdown(
                "Las frecuencias de retraso en llegada y salida muestran el comportamiento porcentual frente al total de operaciones, "
                "evidenciando qué modelos de aeronave presentan mayor recurrencia de demoras operativas superiores a los 15 minutos."
            )

with pestanas[4]:
    presentar_objetivo(
        "Variación según el día de la semana",
        (
            "Examinar la variación de los retrasos según el día "
            "de la semana, con el propósito de identificar patrones "
            "temporales en el cumplimiento de los horarios programados."
        ),
        "¿Cómo cambian la frecuencia y la magnitud de los retrasos "
        "según el día de salida programada?"
    )
    st.caption(
        "Filtros de control para la variación semanal y rangos de retraso."
    )

    dias_vis_obj5 = {
        "Lunes": "Lunes", "Martes": "Martes", "Miercoles": "Miércoles",
        "Jueves": "Jueves", "Viernes": "Viernes", "Sabado": "Sábado", "Domingo": "Domingo"
    }
    
    franjas_disp_obj5 = consultar("""
        SELECT DISTINCT franja_horaria 
        FROM v_analisis_vuelos_limpios 
        WHERE franja_horaria IS NOT NULL 
        ORDER BY franja_horaria
    """)["franja_horaria"].tolist()

    fecha_min_obj5 = pd.Timestamp(control.loc[0, "desde"]).date()
    fecha_max_obj5 = pd.Timestamp(control.loc[0, "hasta"]).date()

    col_f1, col_f2, col_f3 = st.columns(3)
    fechas_obj5 = col_f1.date_input(
        "Rango de Fechas", value=(fecha_min_obj5, fecha_max_obj5),
        min_value=fecha_min_obj5, max_value=fecha_max_obj5,
        format="DD/MM/YYYY", key="obj5_fecha"
    )
    dia_obj5 = col_f2.selectbox(
        "Día de la semana", [None, *dias_vis_obj5],
        format_func=lambda d: dias_vis_obj5.get(d, "Todas"), key="obj5_dia"
    )
    franja_obj5 = col_f3.selectbox(
        "Franja Horaria", [None, *franjas_disp_obj5],
        format_func=lambda f: f or "Todas", key="obj5_franja"
    )
    
    fechas_obj5 = fechas_obj5 or (fecha_min_obj5, fecha_max_obj5)

    # Objetivo 5
    datos_dias = consultar("""
        SELECT
            CASE TRIM(dia_semana)
                WHEN 'Miércoles' THEN 'Miércoles'
                WHEN 'Miercoles' THEN 'Miércoles'
                WHEN 'Sábado' THEN 'Sábado'
                WHEN 'Sabado' THEN 'Sábado'
                ELSE TRIM(dia_semana)
            END AS dia_semana,
            ROUND(AVG(CASE WHEN retraso_salida_min > 0 THEN retraso_salida_min ELSE NULL END), 2) AS prom_salida_min,
            SUM(CASE WHEN retraso_salida_min > 0 AND retraso_salida_min < 60 THEN 1 ELSE 0 END) AS r_menor,
            SUM(CASE WHEN retraso_salida_min >= 60 THEN 1 ELSE 0 END) AS r_severo,
            COUNT(*) AS total_vuelos
        FROM v_analisis_vuelos_limpios
        WHERE dia_semana IS NOT NULL
          AND fecha_salida_local >= ? AND fecha_salida_local <= ?
          AND (? IS NULL OR TRIM(dia_semana) = ?)
          AND (? IS NULL OR franja_horaria = ?)
        GROUP BY 1
        ORDER BY 
            CASE 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Lunes' THEN 1 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Martes' THEN 2 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Miércoles' THEN 3 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Jueves' THEN 4 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Viernes' THEN 5 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Sábado' THEN 6 
                WHEN CASE TRIM(dia_semana)
                    WHEN 'Miércoles' THEN 'Miércoles'
                    WHEN 'Miercoles' THEN 'Miércoles'
                    WHEN 'Sábado' THEN 'Sábado'
                    WHEN 'Sabado' THEN 'Sábado'
                    ELSE TRIM(dia_semana)
                END = 'Domingo' THEN 7 
                ELSE 8 
            END
    """, [
        str(fechas_obj5[0]), str(fechas_obj5[-1]),
        dia_obj5, dia_obj5,
        franja_obj5, franja_obj5
    ])

    if datos_dias.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados en el Objetivo 5.")
    else:
        st.divider()
        
        mejor_fila = datos_dias.loc[datos_dias["prom_salida_min"].idxmin()] if not datos_dias.empty else None
        peor_fila = datos_dias.loc[datos_dias["prom_salida_min"].idxmax()] if not datos_dias.empty else None
        
        mejor_dia_val = mejor_fila["dia_semana"] if mejor_fila is not None else "N/A"
        peor_dia_val = peor_fila["dia_semana"] if peor_fila is not None else "N/A"
        
        fds_df = consultar("""
            SELECT ROUND(AVG(retraso_salida_min), 2) as prom FROM v_analisis_vuelos_limpios 
            WHERE retraso_salida_min > 0 AND TRIM(dia_semana) IN ('Sábado', 'Sabado', 'Domingo')
        """)
        sem_df = consultar("""
            SELECT ROUND(AVG(retraso_salida_min), 2) as prom FROM v_analisis_vuelos_limpios 
            WHERE retraso_salida_min > 0 AND TRIM(dia_semana) NOT IN ('Sábado', 'Sabado', 'Domingo')
        """)
        
        val_fds = fds_df.loc[0, "prom"] if not fds_df.empty and pd.notna(fds_df.loc[0, "prom"]) else 0
        val_sem = sem_df.loc[0, "prom"] if not sem_df.empty and pd.notna(sem_df.loc[0, "prom"]) else 0
        dif_fds_val = round(abs(val_fds - val_sem), 2)

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            with st.container(border=True):
                st.metric("Mejor Día Semana", str(mejor_dia_val))
        with kpi2:
            with st.container(border=True):
                st.metric("Peor Día Semana", str(peor_dia_val))
        with kpi3:
            with st.container(border=True):
                st.metric("Diferencia Fines de Semana", f"{dif_fds_val:.2f}".replace(".", ","))

        st.divider()

        st.markdown("#### Promedio Retraso Salida (Min) por nombre_dia")
        col_g1, col_i1 = st.columns([1.3, 0.7], gap="large")
        
        with col_g1:
            with st.container(border=True):
                fig_obj5_sup = px.bar(
                    datos_dias,
                    x="dia_semana",
                    y="prom_salida_min",
                    text="prom_salida_min",
                    labels={"dia_semana": "", "prom_salida_min": ""},
                    color_discrete_sequence=["#C9A956"]
                )
                fig_obj5_sup.update_traces(texttemplate='%{text:.0f} min', textposition='outside')
                fig_obj5_sup.update_layout(
                    template="plotly_white",
                    height=350,
                    margin=dict(b=40, t=30),
                    yaxis=dict(showgrid=True, gridcolor="#eee", range=[0, datos_dias["prom_salida_min"].max() * 1.2]),
                    xaxis=dict(showgrid=False, categoryorder="array", categoryarray=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
                )
                st.plotly_chart(fig_obj5_sup, use_container_width=True)

        with col_i1:
            st.markdown("##### Interpretación")
            st.markdown(
                f"El día **{mejor_dia_val}** registra el mejor comportamiento operativo con el menor promedio de minutos en salida, "
                f"mientras que **{peor_dia_val}** concentra las mayores demoras promedio, reflejando puntos de congestión a evaluar."
            )

        st.divider()

        col_g2, col_i2 = st.columns([1.3, 0.7], gap="large")

        with col_g2:
            st.markdown("#### Vuelos con salida registrada por nombre_dia y Rangos de Retraso")
            with st.container(border=True):
                df_pct = datos_dias.copy()
                suma_rangos = df_pct["r_menor"] + df_pct["r_severo"]
                suma_rangos = suma_rangos.replace(0, 1)
                
                df_pct["r_menor"] = (df_pct["r_menor"] / suma_rangos) * 100
                df_pct["r_severo"] = (df_pct["r_severo"] / suma_rangos) * 100

                df_melted = pd.melt(
                    df_pct,
                    id_vars=["dia_semana"],
                    value_vars=["r_menor", "r_severo"],
                    var_name="rango",
                    value_name="porcentaje"
                )
                
                mapa_rangos = {
                    "r_menor": "Retraso menor (>0 y <15 min)",
                    "r_severo": "Retraso severo (>=60 min)"
                }
                df_melted["rango"] = df_melted["rango"].map(mapa_rangos)

                fig_obj5_mid = px.bar(
                    df_melted,
                    x="dia_semana",
                    y="porcentaje",
                    color="rango",
                    barmode="stack",
                    labels={"porcentaje": "", "dia_semana": "", "rango": ""},
                    color_discrete_map={
                        "Retraso menor (>0 y <15 min)": "#F6E39A",
                        "Retraso severo (>=60 min)": "#C9A956"
                    }
                )
                fig_obj5_mid.update_layout(
                    template="plotly_white",
                    height=350,
                    xaxis=dict(showgrid=False, categoryorder="array", categoryarray=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]),
                    yaxis=dict(showgrid=True, gridcolor="#eee", range=[0, 100], ticksuffix="%"),
                    legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="left", x=0)
                )
                st.plotly_chart(fig_obj5_mid, use_container_width=True)

        with col_i2:
            st.markdown("##### Interpretación")
            st.markdown(
                "La distribución porcentual al 100% muestra la proporción exacta entre los retrasos menores y severos (>=60 min) a lo largo de los días de la semana."
            )

        st.divider()

        col_g3, col_i3 = st.columns([1.3, 0.7], gap="large")

        with col_g3:
            st.markdown("#### Promedio Retraso Salida (Min) por Fecha y Día de la Semana")
            with st.container(border=True):
                datos_lineas = consultar("""
                    SELECT
                        CAST(fecha_salida_local AS DATE) as fecha_vuelo,
                        CASE TRIM(dia_semana)
                            WHEN 'Miércoles' THEN 'Miércoles'
                            WHEN 'Miercoles' THEN 'Miércoles'
                            WHEN 'Sábado' THEN 'Sábado'
                            WHEN 'Sabado' THEN 'Sábado'
                            ELSE TRIM(dia_semana)
                        END AS dia_semana,
                        ROUND(AVG(CASE WHEN retraso_salida_min > 0 THEN retraso_salida_min ELSE NULL END), 2) AS prom_min
                    FROM v_analisis_vuelos_limpios
                    WHERE fecha_salida_local IS NOT NULL
                      AND fecha_salida_local >= ? AND fecha_salida_local <= ?
                      AND (? IS NULL OR TRIM(dia_semana) = ?)
                      AND (? IS NULL OR franja_horaria = ?)
                    GROUP BY 1, 2
                    ORDER BY fecha_vuelo
                """, [
                    str(fechas_obj5[0]), str(fechas_obj5[-1]),
                    dia_obj5, dia_obj5,
                    franja_obj5, franja_obj5
                ])

                if datos_lineas.empty:
                    st.info("No hay suficientes datos temporales para las líneas.")
                else:
                    fig_obj5_line = px.line(
                        datos_lineas,
                        x="fecha_vuelo",
                        y="prom_min",
                        color="dia_semana",
                        labels={"fecha_vuelo": "", "prom_min": "", "dia_semana": "Día"},
                        color_discrete_map={
                            "Lunes": "#FF69B4",      # Rosado
                            "Martes": "#A0522D",     # Marrón
                            "Miércoles": "#00BFFF",  # Azul vibrante
                            "Jueves": "#FFD700",     # Amarillo
                            "Viernes": "#D2691E",    # Naranja / Café claro
                            "Sábado": "#FFF8DC",     # Crema
                            "Domingo": "#800020"     # Vinotinto
                        }
                    )
                    fig_obj5_line.update_layout(
                        template="plotly_white",
                        height=350,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#eee"),
                        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="left", x=0)
                    )
                    st.plotly_chart(fig_obj5_line, use_container_width=True)

        with col_i3:
            st.markdown("##### Interpretación")
            st.markdown(
                "La evolución temporal de las líneas permite observar la tendencia continua de los retrasos por día de la semana "
                "a lo largo del período analizado, identificando picos específicos de inestabilidad operativa."
            )