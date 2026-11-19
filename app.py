from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.db import get_supabase_client
from fids_board import mostrar_tablero_vuelos  #modulo de tablero
import sqlite3



st.set_page_config(page_title="Análisis de vuelos", page_icon="✈️", layout="wide")

# ==============================================================================
# CSS DEFINITIVO: NATIVO SIN DUPLICAR, ICONOS VISIBLES Y HOVER SUAVE
# ==============================================================================
st.markdown("""
<style>
    /* 1. Eliminar botón superior nativo */
    [data-testid="collapsedControl"], button[kind="header"] {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Barra lateral contraída por defecto (ancho justo para los iconos) */
    section[data-testid="stSidebar"] {
        width: 75px !important;
        min-width: 75px !important;
        max-width: 75px !important;
        transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
    }
    
    /* 3. Expandir suavemente al hacer hover */
    section[data-testid="stSidebar"]:hover {
        width: 290px !important;
        min-width: 290px !important;
        max-width: 290px !important;
    }

    /* 4. Menú de páginas (arriba): ocultar solo el texto al contraer, manteniendo el icono visible */
    section[data-testid="stSidebar"]:not(:hover) [data-testid="stSidebarNav"] span {
        display: none !important;
    }
    section[data-testid="stSidebar"]:hover [data-testid="stSidebarNav"] span {
        display: inline !important;
    }

    /* 5. Contenido de usuario (abajo - Proyecto de computación): ocultar completo al no hacer hover */
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

    /* 6. Espaciado del menú de navegación */
    [data-testid="stSidebarNav"] ul li a {
        font-size: 15px !important;
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

raiz = Path(__file__).resolve().parent

# ==============================================================================
# BARRA LATERAL (ELEMENTOS INFERIORES: PROYECTO DE COMPUTACIÓN)
# ==============================================================================
st.sidebar.divider()
st.sidebar.title("Proyecto de computación")
seccion = st.sidebar.radio("Sección", ["Inicio", "Explorar vuelos", "Auditoría Supabase"])
st.sidebar.caption("Análisis de horarios y retrasos")

# ==============================================================================
# CONTENIDO PRINCIPAL
# ==============================================================================
st.title("Análisis de vuelos y retrasos")
st.caption("Estudio del cumplimiento de horarios en aeropuertos de Rusia")

ruta_base = raiz / "Base_de_datos" / "vuelos_final.duckdb"

try:
    if not ruta_base.is_file():
        raise FileNotFoundError(f"No se encontró {ruta_base.name}")

    with duckdb.connect(str(ruta_base), read_only=True) as conexion:
        total = conexion.execute(
            "SELECT COUNT(*) FROM vuelos"
        ).fetchone()[0]

        aptos = conexion.execute(
            "SELECT COUNT(*) FROM v_analisis_vuelos_limpios"
        ).fetchone()[0]

        fecha_min, fecha_max = conexion.execute(
            "SELECT MIN(CAST(salida_prog_local AS DATE)), "
            "MAX(CAST(salida_prog_local AS DATE)) FROM lim_vuelos"
        ).fetchone()

        otp_pct, demora_media = conexion.execute("""
            SELECT 
                ROUND(100.0 * SUM(CASE WHEN EXTRACT(EPOCH FROM (CAST(salida_real AS TIMESTAMP) - CAST(salida_programada AS TIMESTAMP)))/60.0 <= 15 THEN 1 ELSE 0 END) / COUNT(*), 1),
                ROUND(AVG(EXTRACT(EPOCH FROM (CAST(salida_real AS TIMESTAMP) - CAST(salida_programada AS TIMESTAMP)))/60.0), 1)
            FROM lim_vuelos
        """).fetchone()

        df_heatmap = None
        df_top_aero = None
        if seccion == "Inicio":
            df_heatmap = conexion.execute("""
                SELECT 
                    EXTRACT(ISODOW FROM CAST(salida_prog_local AS TIMESTAMP)) AS dia_num,
                    EXTRACT(HOUR FROM CAST(salida_prog_local AS TIMESTAMP)) AS hora,
                    ROUND(AVG(EXTRACT(EPOCH FROM (CAST(salida_real AS TIMESTAMP) - CAST(salida_programada AS TIMESTAMP))) / 60.0), 1) AS demora_min
                FROM lim_vuelos
                GROUP BY 1, 2
                ORDER BY 1, 2
            """).fetchdf()

            df_top_aero = conexion.execute("""
                SELECT * FROM lim_vuelos LIMIT 50000
            """).fetchdf()

        muestra = None
        if seccion == "Explorar vuelos":
            muestra = conexion.execute(
                "SELECT * FROM v_analisis_vuelos_limpios LIMIT 5000"
            ).fetchdf()

    if aptos > total:
        raise ValueError(
            "La vista limpia contiene más registros que la tabla vuelos."
        )

except (OSError, ValueError, duckdb.Error) as error:
    st.error(f"No se pudo consultar la base de datos: {error}")
    st.stop()



if seccion == "Inicio":
    df_tablero = pd.DataFrame([
        {"hora": "06:15", "vuelo": "SU 1120", "destino": "SOCHI (AER)",          "puerta": "A04", "estado": "EN HORA"},
        {"hora": "06:45", "vuelo": "S7 2045", "destino": "NOVOSIBIRSK (OVB)",    "puerta": "B12", "estado": "EMBARCANDO"},
        {"hora": "07:10", "vuelo": "DP 403",  "destino": "EKATERIMBURGO (SVX)",  "puerta": "C02", "estado": "EN HORA"},
        {"hora": "07:50", "vuelo": "SU 014",  "destino": "SAN PETERSBURGO (LED)","puerta": "A09", "estado": "RETRASADO"},
        {"hora": "08:20", "vuelo": "U6 261",  "destino": "KAZAN (KZN)",          "puerta": "B05", "estado": "EN HORA"},
        {"hora": "09:05", "vuelo": "FV 6012", "destino": "KALININGRADO (KGD)",   "puerta": "A14", "estado": "EN HORA"},
        {"hora": "09:40", "vuelo": "SU 1702", "destino": "VLADIVOSTOK (VVO)",    "puerta": "D01", "estado": "EMBARCANDO"},
        {"hora": "10:15", "vuelo": "S7 1015", "destino": "SAMARA (KUF)",         "puerta": "B08", "estado": "CANCELADO"},
        {"hora": "11:00", "vuelo": "UT 489",  "destino": "UFA (UFA)",            "puerta": "C07", "estado": "EN HORA"},
        {"hora": "11:35", "vuelo": "SU 1482", "destino": "KRASNOYARSK (KJA)",    "puerta": "A02", "estado": "RETRASADO"},
        {"hora": "12:10", "vuelo": "5N 231",  "destino": "MURMANSK (MMK)",       "puerta": "C11", "estado": "EN HORA"},
        {"hora": "12:55", "vuelo": "DP 185",  "destino": "MINERALNYE VODY (MRV)","puerta": "B03", "estado": "EN HORA"},
        {"hora": "13:30", "vuelo": "SU 1210", "destino": "OMSK (OMS)",           "puerta": "A11", "estado": "EMBARCANDO"},
        {"hora": "14:15", "vuelo": "S7 3021", "destino": "IRKUTSK (IKT)",        "puerta": "D06", "estado": "EN HORA"},
        {"hora": "15:00", "vuelo": "U6 157",  "destino": "CHELYABINSK (CEK)",    "puerta": "B15", "estado": "EN HORA"},
    ])

    mostrar_tablero_vuelos(df_tablero, filas_por_pagina=5)
    st.divider()

    st.subheader("Objetivo del panel")
    st.write(
        "Explorar los horarios programados y reales para estudiar "
        "los retrasos de salida y llegada de los vuelos."
    )

    columnas = st.columns(3)
    columnas[0].metric("Vuelos registrados", f"{total:,}")
    columnas[1].metric("Vuelos aptos para analizar", f"{aptos:,}", f"{round(aptos/total*100, 1)}% del total")
    columnas[2].metric("Vuelos excluidos del análisis", f"{total - aptos:,}")

    kpi_op = st.columns(2)
    kpi_op[0].metric("Puntualidad OTP (≤ 15 min)", f"{otp_pct or 0}%", "Estándar internacional IATA")
    kpi_op[1].metric("Demora promedio en salida", f"{demora_media or 0} min")

    st.write(
        "**Fechas de salida local de la tabla limpia:** "
        f"{fecha_min or 'Sin datos'} a {fecha_max or 'Sin datos'}"
    )
    st.html("""
    <div style="background: rgba(59, 130, 246, 0.10);
                padding: 20px 24px; border-radius: 10px;">

        <p style="font-size: 18px; line-height: 1.7; margin: 0 0 16px;">
            <strong>Vuelos incluidos:</strong>
            vuelos que completaron su recorrido (estado Arrived)
            y cuentan con horarios programados y reales
            de salida y llegada.
        </p>

        <p style="font-size: 18px; line-height: 1.7; margin: 0 0 16px;">
            <strong>Vuelos excluidos:</strong>
            vuelos en otros estados o con horarios incompletos,
            porque no permiten comparar los horarios programados
            con los reales y calcular los retrasos de salida y llegada.
        </p>

        <p style="font-size: 18px; line-height: 1.7; margin: 0;">
            Los vuelos excluidos se conservan en la base de datos.
        </p>

    </div>
    """)

    st.divider()
    st.subheader("Efecto cascada: Demora promedio por día y hora")
    st.caption("Identificación de franjas horarias con acumulación de retrasos en la red aérea.")

    dias_nombres = {
        1: "Lunes", 2: "Martes", 3: "Miércoles",
        4: "Jueves", 5: "Viernes", 6: "Sábado", 7: "Domingo"
    }
    df_heatmap["dia"] = df_heatmap["dia_num"].map(dias_nombres)

    matriz_calor = df_heatmap.pivot(index="dia", columns="hora", values="demora_min")
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    matriz_calor = matriz_calor.reindex([d for d in orden_dias if d in matriz_calor.index])

    fig_calor = px.imshow(
        matriz_calor,
        labels=dict(x="Hora del día (local)", y="Día de la semana", color="Demora (min)"),
        x=matriz_calor.columns,
        y=matriz_calor.index,
        color_continuous_scale="Cividis",
        aspect="auto",
        text_auto=".0f"
    )
    fig_calor.update_layout(
        xaxis=dict(dtick=1),
        margin=dict(l=10, r=10, t=20, b=10),
        height=380
    )
    st.plotly_chart(fig_calor, use_container_width=True)
    st.divider()
    st.subheader("Cuellos de botella: Top 10 aeropuertos con mayor demora")
    st.caption("Terminales con el promedio más alto de minutos de retraso en salida (mínimo 50 vuelos).")

    # Detecta automáticamente la columna de aeropuerto de origen
    col_origen = next(
        (c for c in df_top_aero.columns if "origen" in c.lower() or "departure_airport" in c.lower() or "salida_aero" in c.lower()),
        df_top_aero.columns[0]
    )

    df_top_aero["demora_calc"] = (
        pd.to_datetime(df_top_aero["salida_real"]) - pd.to_datetime(df_top_aero["salida_programada"])
    ).dt.total_seconds() / 60.0

    ranking = (
        df_top_aero.groupby(col_origen, as_index=False)
        .agg(demora_promedio=("demora_calc", "mean"), total_vuelos=("demora_calc", "count"))
    )
    ranking = ranking[ranking["total_vuelos"] >= 50].sort_values("demora_promedio", ascending=False).head(10)
    ranking["demora_promedio"] = ranking["demora_promedio"].round(1)

    if not ranking.empty:
        peor_aero = ranking.iloc[0][col_origen]
        peor_demora = ranking.iloc[0]["demora_promedio"]

        st.warning(f"⚠️ **Alerta de congestión:** El aeropuerto **{peor_aero}** lidera las demoras con un promedio de **{peor_demora} min** por salida.")

        fig_barras = px.bar(
            ranking.sort_values("demora_promedio", ascending=True),
            x="demora_promedio",
            y=col_origen,
            orientation="h",
            text="demora_promedio",
            color="demora_promedio",
            color_continuous_scale="OrRd",
            labels={"demora_promedio": "Demora promedio (min)", col_origen: "Aeropuerto"}
        )
        fig_barras.update_traces(texttemplate="%{text} min", textposition="outside")
        fig_barras.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=10, r=40, t=10, b=10),
            height=380,
            xaxis_title="Minutos promedio de retraso",
            yaxis_title=""
        )
        st.plotly_chart(fig_barras, use_container_width=True)


elif seccion == "Explorar vuelos":
    st.subheader("Explorador interactivo de vuelos aptos")
    st.caption("Filtra los registros de la vista limpia y descarga los resultados.")

    col_f1, col_f2 = st.columns([2, 1])
    busqueda = col_f1.text_input(
        "Buscar por número de vuelo, aeropuerto o ciudad:",
        placeholder="Ej. SU, SVO, LED..."
    )
    max_filas = col_f2.selectbox("Registros a mostrar:", [50, 100, 500, 1000], index=1)

    df_exp = muestra.copy()
    if busqueda.strip():
        mask = df_exp.astype(str).apply(
            lambda col: col.str.contains(busqueda.strip(), case=False, na=False)
        ).any(axis=1)
        df_exp = df_exp[mask]

    st.write(f"**Registros encontrados:** {len(df_exp):,}")
    st.dataframe(df_exp.head(max_filas), hide_index=True, use_container_width=True)

    csv = df_exp.head(max_filas).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Descargar vista actual en CSV",
        data=csv,
        file_name="vuelos_filtrados.csv",
        mime="text/csv"
    )
elif seccion == "Auditoría Supabase":
    #==============================================================================
    # conexion con supabase
    #==============================================================================
    try:
            # Inicializamos en supabase
            supabase = get_supabase_client()

            # Tablas de la base de datos origial
            tablas_disponibles = [
                "flights",
                "bookings",
                "tickets",
                "ticket_flights",
                "boarding_passes",
                "aircrafts_data",
                "airports_data",
                "seats"
            ]

            # Menú desplegable para elegir qué tabla ver en la app
            tabla_seleccionada = st.selectbox("Selecciona la tabla a consultar:", tablas_disponibles)

            # Consultar los datos de la tabla elegida (limitado a 500 registros para rendimiento)
            response = supabase.table(tabla_seleccionada).select("*").range(0,99999).execute()
            data = response.data

            if data:
                df_supabase = pd.DataFrame(data)
                st.dataframe(df_supabase, hide_index=True, use_container_width=True)
            else:
                st.warning(f"La tabla '{tabla_seleccionada}' está vacía o no se encontraron datos.")

    except Exception as e:
            st.error(f"Error al conectar o consultar Supabase: {e}")
