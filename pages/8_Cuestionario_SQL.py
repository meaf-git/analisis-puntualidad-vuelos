import streamlit as st
import pandas as pd
import duckdb
from utils.db import get_supabase_client

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

st.set_page_config(page_title="Cuestionario SQL", page_icon="🥵", layout="wide")
st.title("Cuestionario SQL")

consultas = st.tabs(
    [
        "Pregunta 1",
        "Pregunta 2",
        "Pregunta 3",
        "Pregunta 4",
        "Pregunta 5",
    ]
)
with consultas[0]:

    st.markdown(""" info aqui """, unsafe_allow_html=True )

with consultas[1]:
    
    st.header("Pregunta 2. Mayores saltos diarios de venta")

    st.write(
        "Identificar los ocho dias con mayor aumento absoluto del importe total de las reservas "
        "respecto al dia calendario inmediatamente anterior, excluyendo los primeros catorce dias de la serie."
    )

    consulta_2 = """
    WITH ventas_diarias AS (
        SELECT
            CAST(
                CAST(book_date AS TIMESTAMPTZ)
                AT TIME ZONE 'Europe/Moscow'
                AS DATE
            ) AS fecha,
            COUNT(*) AS reservas,
            SUM(total_amount) AS importe
        FROM bookings
        GROUP BY 1
    ),
    serie AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                ORDER BY fecha
            ) AS numero_dia
        FROM ventas_diarias
    ),
    comparacion AS (
        SELECT
            actual.fecha,
            actual.reservas,
            actual.importe,
            anterior.importe AS importe_anterior,
            actual.importe - anterior.importe AS aumento
        FROM serie AS actual
        JOIN serie AS anterior
            ON anterior.fecha = actual.fecha - INTERVAL 1 DAY
        WHERE actual.numero_dia > 14
    ),
    clasificacion AS (
        SELECT
            *,
            RANK() OVER (
                ORDER BY aumento DESC
            ) AS puesto_aumento,
            RANK() OVER (
                ORDER BY aumento ASC
            ) AS puesto_caida
        FROM comparacion
    )
    SELECT
        puesto_aumento,
        fecha,
        reservas AS cantidad_reservas,
        importe AS importe_dia,
        importe_anterior AS importe_dia_anterior,
        aumento AS aumento_absoluto,
        ROUND(
            100.0 * aumento / NULLIF(importe_anterior, 0),
            2
        ) AS variacion_porcentual,
        ROUND(
            100.0 * importe /
            NULLIF(
                (SELECT MAX(importe) FROM ventas_diarias),
                0
            ),
            2
        ) AS porcentaje_del_maximo_diario,
        puesto_caida AS puesto_ranking_caidas
    FROM clasificacion
    ORDER BY
        puesto_aumento,
        fecha
    LIMIT 8;
    """
    st.code(consulta_2, language="sql")

    # Cargar la tabla bookings directamente desde Supabase con caché
    @st.cache_data(ttl=600)
    def cargar_bookings_supabase():
        supabase = get_supabase_client()

        total = (
            supabase.table("bookings")
            .select("book_ref", count="exact", head=True)
            .execute()
            .count
        )

        if total is None or total == 0:
            raise ValueError("No se pudo verificar el total de reservas.")

        registros = []

        while len(registros) < total:
            inicio = len(registros)

            respuesta = (
                supabase.table("bookings")
                .select("book_ref, book_date, total_amount")
                .order("book_ref")
                .range(inicio, inicio + 999)
                .execute()
            )

            lote = respuesta.data or []

            if not lote:
                raise ValueError("La descarga de reservas quedó incompleta.")

            registros.extend(lote)

        datos = pd.DataFrame(registros)

        if len(datos) != total or datos["book_ref"].nunique() != total:
            raise ValueError("La descarga tiene reservas faltantes o duplicadas.")

        return datos

    try:
        with st.spinner("Cargando datos desde Supabase..."):
            bookings = cargar_bookings_supabase()
    except Exception as error:
        st.error("No se pudo conectar o cargar la tabla 'bookings' desde Supabase.")
        st.exception(error)
        st.stop()

    # Ejecutar la consulta SQL usando DuckDB sobre el DataFrame obtenido de Supabase
    try:
        resultado_2 = duckdb.query(consulta_2).df()
    except Exception as error:
        st.error("Error al ejecutar la consulta SQL.")
        st.exception(error)
        st.stop()

    st.subheader("Resultados")
    st.dataframe(resultado_2, hide_index=True)

    st.subheader("Interpretación de los resultados")

    st.write(
        "El mayor aumento se registró el 14 de julio de 2017. "
        "El importe de las reservas pasó de 432.826.700 el día "
        "anterior a 460.449.000, un aumento de 27.622.300, "
        "equivalente al 6,38 %."
    )

    st.write(
        "El mayor aumento diario no corresponde necesariamente "
        "al día con mayor importe de reservas. El 14 de agosto "
        "registró el importe máximo de toda la serie, con "
        "524.600.500, pero ocupa el octavo puesto por aumento."
    )

    st.write(
        "El puesto en el ranking de caídas se calcula entre "
        "todos los días considerados, antes de seleccionar "
        "estos ocho resultados. El puesto 1 corresponde a la "
        "mayor caída; por eso los mayores aumentos aparecen "
        "en los últimos puestos de ese ranking."
    )

with consultas[4]:
    st.header("Pregunta 5. Acompañantes y asignacion de asientos")
    
    consulta_5 = """
    WITH parejas_vuelo AS (
        SELECT 
            bp1.flight_id,
            t1.book_ref,
            bp1.ticket_no AS ticket_1,
            bp2.ticket_no AS ticket_2,
            (bp1.seat_no + 0 ) AS fila_1,
            (bp2.seat_no + 0 ) AS fila_2
        FROM boarding_passes bp1
        JOIN tickets t1 ON bp1.ticket_no = t1.ticket_no
        JOIN boarding_passes bp2 ON bp1.flight_id = bp2.flight_id
        JOIN tickets t2 ON bp2.ticket_no = t2.ticket_no
        WHERE t1.book_ref = t2.book_ref
        AND bp1.ticket_no < bp2.ticket_no 
        AND bp1.seat_no IS NOT NULL 
        AND bp2.seat_no IS NOT NULL
    ),
    metricas_modelo AS (
        SELECT 
            a.aircraft_code,
            json_extract(a.model, '$.en') AS modelo_ingles,
            COUNT(*) AS total_parejas,
            SUM(CASE WHEN pf.fila_1 = pf.fila_2 THEN 1 ELSE 0 END) AS parejas_misma_fila,
            SUM(CASE WHEN ABS(pf.fila_1 - pf.fila_2) <= 1 THEN 1 ELSE 0 END) AS parejas_filas_contiguas,
            (SELECT COUNT(DISTINCT (s.seat_no + 0))
            FROM seats s
            WHERE s.aircraft_code = a.aircraft_code) AS filas_distintas_modelo
        FROM parejas_vuelo pf
        JOIN flights f ON pf.flight_id = f.flight_id
        JOIN aircrafts_data a ON f.aircraft_code = a.aircraft_code
        GROUP BY a.aircraft_code, a.model
    ),
    porcentajes_calculados AS (
        SELECT 
            modelo_ingles,
            total_parejas,
            parejas_misma_fila,
            ROUND((parejas_misma_fila) * 100.0 / total_parejas, 2) AS porcentaje_misma_fila,
            ROUND((parejas_filas_contiguas) * 100.0 / total_parejas, 2) AS porcentaje_contiguas,
            filas_distintas_modelo,
            RANK() OVER (ORDER BY (parejas_misma_fila) * 100.0 / total_parejas DESC) AS puesto_modelo
        FROM metricas_modelo
    )
    SELECT 
        modelo_ingles AS "Modelo de Avión",
        total_parejas AS "Cantidad de Parejas",
        parejas_misma_fila AS "Parejas Misma Fila",
        porcentaje_misma_fila AS "Porcentaje Misma Fila (%)",
        porcentaje_contiguas AS "Porcentaje Filas Contiguas (%)",
        filas_distintas_modelo AS "Filas Distintas",
        puesto_modelo AS "Puesto"
    FROM porcentajes_calculados
    ORDER BY puesto_modelo ASC;

        """
    st.code(consulta_5, language="sql")
    