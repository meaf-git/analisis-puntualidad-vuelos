import streamlit as st
from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

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
        "A tiempo": "#2563EB",
        "Leve: 1–30 min": "#0F766E",
        "Moderado: 31–60 min": "#F59E0B",
        "Severo: más de 60 min": "#DC2626"
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
                "Puntual": "#2563EB",
                "Retrasado": "#F91616"
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
            color_discrete_sequence=["#2563EB"],
            opacity=0.5
        )

        st.plotly_chart(
            grafico_dispersion,
            use_container_width=True
        )

  
from plotly.subplots import make_subplots

with pestanas[1]:
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
        "Se considera salida retrasada toda demora mayor de cero minutos. "
        "Los promedios incluyen unicamente los vuelos con demora de salida "
        "en cada grupo. Los porcentajes se calculan sobre todos los vuelos"
        "del grupo. Se utiliza la salida programada local del aeropuerto de origen."
    )

    # Los totales se calculan sobre los vuelos, no promediando promedios.
    datos_vis_obj2 = consultar("""
        SELECT
            COALESCE(franja_horaria, 'Total') AS franja,
            COALESCE(dia_semana, 'Total') AS dia,
            COUNT(*) AS vuelos,
            SUM(CASE WHEN retraso_salida_min > 15 THEN 1 ELSE 0 END)
                AS retrasados,
            AVG(CASE WHEN retraso_salida_min > 15
                     THEN retraso_salida_min END) AS promedio
        FROM v_analisis_vuelos_limpios
        GROUP BY GROUPING SETS (
            (franja_horaria, dia_semana),
            (franja_horaria),
            (dia_semana),
            ()
        )
    """)
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
        figura.update_yaxes(gridcolor="#E8EDF4", zeroline=False)
        return figura

    def _fila_objetivo2(titulo, figura, interpretacion, clave, nota=None):
        st.markdown(f"#### {titulo}")
        grafico, texto = st.columns([2, 1], gap="large")
        with grafico:
            with st.container(border=True):
                st.plotly_chart(figura, width="stretch", key=clave)
                if nota:
                    st.caption(nota)
        with texto:
            st.markdown("**Interpretación**")
            st.write(interpretacion)
        st.divider()

    orden_vis_obj2 = franjas_vis_obj2["franja"].tolist()
    dias_vis_obj2 = [
        "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"
    ]
    paleta_vis_obj2 = ["#168CF0", "#32339B", "#E76F3C", "#139E8E"]
    colores_vis_obj2 = {
        franja: paleta_vis_obj2[i % len(paleta_vis_obj2)]
        for i, franja in enumerate(orden_vis_obj2)
    }
    etiquetas_vis_obj2 = {
        "franja": "Franja horaria",
        "promedio": "Demora promedio de vuelos con retraso >15 min",
        "porcentaje": "Vuelos con retraso >15 min (%)",
        "vuelos": "Total de vuelos",
        "retrasados": "Vuelos con retraso de salida >15 min"
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
    st.caption(
        "Criterio de los gráficos: se cuentan como retrasados los vuelos "
        "con demora de salida >15 minutos. Sus promedios incluyen únicamente "
        "esos vuelos. Las tasas usan como denominador todos los vuelos "
        "de cada franja. Los KPI conservan su criterio original."
    )

    # 1. Tabla con formato condicional, conservando sus totales ponderados.
    matriz_vis_obj2 = datos_vis_obj2.pivot(
        index="franja", columns="dia", values="promedio"
    ).reindex(
        index=orden_vis_obj2 + ["Total"],
        columns=dias_vis_obj2 + ["Total"]
    )
    matriz_vis_obj2.index.name = "Franja horaria"
    matriz_vis_obj2.columns.name = None
    celdas_vis_obj2 = matriz_vis_obj2.loc[orden_vis_obj2, dias_vis_obj2]
    minimo_vis_obj2 = celdas_vis_obj2.min().min()
    amplitud_vis_obj2 = celdas_vis_obj2.max().max() - minimo_vis_obj2

    def _color_celda_objetivo2(valor):
        if pd.isna(valor):
            return ""
        posicion = (valor - minimo_vis_obj2) / amplitud_vis_obj2 if amplitud_vis_obj2 else 0.5
        tonos = ["#D6EEE7", "#E8F0D2", "#FFF1BD", "#FFD5AB", "#F4A6A6"]
        indice = max(0, min(4, int(posicion * 5)))
        return f"background-color: {tonos[indice]}; color: #1E293B"

    st.markdown("#### Demora promedio (>15 min) por día y franja horaria")
    grafico, texto = st.columns([2, 1], gap="large")
    with grafico:
        with st.container(border=True):
            st.dataframe(
                matriz_vis_obj2.style.apply(
                    lambda columna: columna.map(_color_celda_objetivo2),
                    subset=pd.IndexSlice[orden_vis_obj2, dias_vis_obj2]
                ).set_properties(
                    subset=pd.IndexSlice[["Total"], :],
                    **{"font-weight": "bold", "background-color": "#E8EEF8"}
                ).set_properties(
                    subset=pd.IndexSlice[:, ["Total"]],
                    **{"font-weight": "bold"}
                ).format(precision=2, decimal=",", na_rep="—"),
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
                f"{_numero_objetivo2(valores_vis_obj2.max())} minutos. "
                "Se promedian únicamente las demoras >15 min. "
                "Los colores cálidos destacan promedios más altos. "
                "Los totales se calculan sobre los vuelos de cada grupo; "
                "no son un promedio simple de las celdas."
            )
    st.divider()

    # 2. Columnas: magnitud de las demoras >15 min.
    magnitud_objetivo2 = px.bar(
        franjas_vis_obj2, x="franja", y="promedio", color="franja",
        text="promedio", color_discrete_map=colores_vis_obj2,
        labels=etiquetas_vis_obj2, category_orders={"franja": orden_vis_obj2}
    )
    magnitud_objetivo2.update_traces(
        texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False,
        marker_line_width=0, width=0.5
    )
    _estilo_objetivo2(magnitud_objetivo2)
    base_prom_vis_obj2 = math.floor(franjas_vis_obj2["promedio"].min())
    tope_prom_vis_obj2 = max(
        base_prom_vis_obj2 + 2, math.ceil(franjas_vis_obj2["promedio"].max())
    )
    magnitud_objetivo2.update_yaxes(
        range=[base_prom_vis_obj2, tope_prom_vis_obj2], dtick=1
    )
    magnitud_objetivo2.update_xaxes(title_text="")
    _fila_objetivo2(
        "Magnitud del retraso (>15 min) por franja horaria", magnitud_objetivo2,
        f"La franja {mayor_prom_vis_obj2['franja']} registra el mayor "
        f"promedio: {_numero_objetivo2(mayor_prom_vis_obj2['promedio'])} min. "
        f"La franja {menor_prom_vis_obj2['franja']} presenta el menor: "
        f"{_numero_objetivo2(menor_prom_vis_obj2['promedio'])} min. "
        "Estos promedios corresponden exclusivamente a los vuelos "
        "con demora de salida >15 min.",
        "objetivo2_magnitud",
        "El eje vertical comienza en "
        f"{_numero_objetivo2(base_prom_vis_obj2, 0)} min para ampliar las diferencias. "
        "Compara los valores indicados sobre las barras."
    )

    # 3. Barras horizontales: noche, tarde y día de arriba hacia abajo.
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
        range=[math.floor(tasas_vis_obj2["porcentaje"].min()),
               math.ceil(tasas_vis_obj2["porcentaje"].max())],
        ticksuffix=" %", tickformat=".1f", dtick=0.5,
        title_text="Vuelos con retraso de salida >15 min (%)"
    )
    porcentajes_objetivo2.update_yaxes(title_text="", showgrid=False)
    _fila_objetivo2(
        "Porcentaje de vuelos retrasados por franja", porcentajes_objetivo2,
        f"La mayor tasa corresponde a {mayor_tasa_vis_obj2['franja']}: "
        f"{_numero_objetivo2(mayor_tasa_vis_obj2['porcentaje'])} %. "
        f"La menor corresponde a {menor_tasa_vis_obj2['franja']}: "
        f"{_numero_objetivo2(menor_tasa_vis_obj2['porcentaje'])} %. "
        "El denominador es el total de vuelos de cada franja.",
        "objetivo2_porcentajes",
        "El eje horizontal se amplía alrededor de las tasas para mostrar "
        "sus diferencias, como en Power BI."
    )

    # 4. Columnas y curva. Orden por cantidad: tarde, día, noche.
    frecuencia_vis_obj2 = franjas_vis_obj2.sort_values("retrasados", ascending=False)
    combinado_objetivo2 = make_subplots(specs=[[{"secondary_y": True}]])
    combinado_objetivo2.add_trace(
        go.Bar(
            x=frecuencia_vis_obj2["franja"], y=frecuencia_vis_obj2["retrasados"],
            name="Vuelos con retraso >15 min", marker_color="#168CF0",
            width=0.55, text=frecuencia_vis_obj2["retrasados"],
            texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False,
            hovertemplate="%{x}<br>Vuelos con retraso >15 min: %{y:,.0f}<extra></extra>"
        ), secondary_y=False
    )
    combinado_objetivo2.add_trace(
        go.Scatter(
            x=frecuencia_vis_obj2["franja"], y=frecuencia_vis_obj2["porcentaje"],
            name="Tasa de retrasos >15 min", mode="lines+markers",
            line=dict(color="#25258A", width=3, shape="spline", smoothing=1.0),
            marker=dict(size=8, color="#25258A", line=dict(color="white", width=1)),
            hovertemplate="%{x}<br>Tasa: %{y:.2f} %<extra></extra>"
        ), secondary_y=True
    )
    _estilo_objetivo2(combinado_objetivo2, 450)
    combinado_objetivo2.update_layout(hovermode="x unified")
    combinado_objetivo2.update_xaxes(
        categoryorder="array", categoryarray=frecuencia_vis_obj2["franja"].tolist()
    )
    combinado_objetivo2.update_yaxes(
        title_text="Vuelos con retraso >15 min", secondary_y=False,
        range=[0, max(1, frecuencia_vis_obj2["retrasados"].max() * 1.15)]
    )
    tasa_min_vis_obj2 = frecuencia_vis_obj2["porcentaje"].min()
    tasa_max_vis_obj2 = frecuencia_vis_obj2["porcentaje"].max()
    margen_tasa_vis_obj2 = max(0.04, (tasa_max_vis_obj2 - tasa_min_vis_obj2) * 0.18)
    combinado_objetivo2.update_yaxes(
        title_text="Vuelos con retraso (%)", secondary_y=True,
        range=[max(0, tasa_min_vis_obj2 - margen_tasa_vis_obj2),
               tasa_max_vis_obj2 + margen_tasa_vis_obj2],
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
        "El suavizado une las tasas observadas; no añade mediciones entre franjas."
    )

    # 5. Burbujas: promedio y cantidad de vuelos con demora >15 min.
    dispersion_objetivo2 = px.scatter(
        franjas_vis_obj2, x="promedio", y="retrasados", color="franja",
        size="retrasados", size_max=28, color_discrete_map=colores_vis_obj2,
        labels=etiquetas_vis_obj2, category_orders={"franja": orden_vis_obj2},
        hover_data={"vuelos": True, "porcentaje": ":.2f", "promedio": ":.2f"}
    )
    dispersion_objetivo2.update_traces(
        marker=dict(opacity=0.9, line=dict(color="white", width=2))
    )
    _estilo_objetivo2(dispersion_objetivo2)
    dispersion_objetivo2.update_xaxes(
        range=[base_prom_vis_obj2 - 1, tope_prom_vis_obj2 + 1],
        showgrid=True, gridcolor="#E8EDF4"
    )
    dispersion_objetivo2.update_yaxes(
        range=[0, max(1, franjas_vis_obj2["retrasados"].max() * 1.18)]
    )
    _fila_objetivo2(
        "Demora promedio y cantidad de vuelos con retraso >15 min", dispersion_objetivo2,
        "Cada burbuja representa una franja. El eje horizontal muestra el "
        "retraso promedio de sus vuelos con demora >15 min; el vertical y el tamaño, "
        "la cantidad de vuelos con demora >15 min. "
        f"{mayor_cant_vis_obj2['franja']} reúne más vuelos retrasados, "
        f"mientras que {mayor_prom_vis_obj2['franja']} registra el mayor promedio.",
        "objetivo2_dispersion"
    )



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
