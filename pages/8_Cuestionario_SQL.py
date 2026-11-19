from inspect import signature

import streamlit as st
import pandas as pd
import duckdb
from utils.db import get_supabase_client

st.set_page_config(page_title="Cuestionario SQL", layout="wide")

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

st.title("Cuestionario SQL")

consulta_1 = """
WITH ruta_dir AS (
    SELECT 
        f.departure_airport AS dep,
        f.arrival_airport AS arr,
        COUNT(tf.ticket_no) AS tramos,
        SUM(tf.amount) AS ingreso
    FROM flights f
    JOIN ticket_flights tf ON f.flight_id = tf.flight_id
    GROUP BY f.departure_airport, f.arrival_airport
),
pares_rutas AS (
    SELECT 
        r1.dep AS aero1_code,
        r1.arr AS aero2_code,
        r1.tramos AS tramos_12,
        r1.ingreso AS ingreso_12,
        COALESCE(r2.tramos, 0) AS tramos_21,
        COALESCE(r2.ingreso, 0) AS ingreso_21,
        (r1.ingreso + COALESCE(r2.ingreso, 0)) AS ingreso_total
    FROM ruta_dir r1
    LEFT JOIN ruta_dir r2 
        ON r1.dep = r2.arr AND r1.arr = r2.dep
    WHERE r1.dep < r1.arr
),
pares_con_puesto AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY ingreso_total DESC) AS puesto,
        aero1_code,
        aero2_code,
        tramos_12,
        tramos_21,
        ingreso_12,
        ingreso_21,
        ingreso_total
    FROM pares_rutas
)
SELECT 
    p.puesto AS "Puesto",
    json_extract_string(CAST(ap1.airport_name AS JSON), '$.en') AS "Aeropuerto A",
    json_extract_string(CAST(ap2.airport_name AS JSON), '$.en') AS "Aeropuerto B",
    (p.tramos_12 + p.tramos_21) AS "Tramos Vendidos Totales",
    p.ingreso_12 AS "Ingreso A hacia B",
    p.ingreso_21 AS "Ingreso B hacia A",
    p.ingreso_total AS "Ingreso Total",
    ROUND((p.ingreso_total * 100.0) / (SELECT SUM(amount) FROM ticket_flights), 4) AS "Porcentaje sobre Red (%)",
    ROUND(((p.ingreso_12 - p.ingreso_21) * 100.0) / NULLIF(p.ingreso_21, 0), 2) AS "Desequilibrio (%)"
FROM pares_con_puesto p
JOIN airports_data ap1 ON p.aero1_code = ap1.airport_code
JOIN airports_data ap2 ON p.aero2_code = ap2.airport_code
ORDER BY p.puesto
LIMIT 10;
""".strip()

consulta_2 = """
WITH ventas_diarias AS (
    SELECT
        CAST(
            CAST(book_date AS TIMESTAMPTZ)
            AT TIME ZONE 'Europe/Moscow'
            AS DATE
        ) AS fecha,
        COUNT(*) AS reservas,
        SUM(total_amount::numeric) AS importe
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
        ON anterior.fecha = actual.fecha - 1
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
""".strip()

# Los datos se leen de Supabase y esta consulta se ejecuta en DuckDB.
consulta_3 = """
WITH vuelos_modelo AS (
    SELECT 
        a.aircraft_code,
        a.model,
        a.range,
        COUNT(f.flight_id) AS cantidad_vuelos,
        AVG(
            EXTRACT(
                EPOCH FROM (
                    CAST(f.actual_arrival AS TIMESTAMPTZ)
                    - CAST(f.actual_departure AS TIMESTAMPTZ)
                )
            ) / 3600.0
        ) AS duracion_media
    FROM flights f
    JOIN aircrafts_data a ON f.aircraft_code = a.aircraft_code
    WHERE f.status = 'Arrived'
    GROUP BY a.aircraft_code, a.model, a.range
),
modelo_ordenado AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (ORDER BY range ASC) AS numero_orden,
        (SELECT COUNT(*) FROM flights WHERE status = 'Arrived') AS total_vuelos_llegados
    FROM vuelos_modelo
),
comparacion AS (
    SELECT 
        actual.*,
        anterior.duracion_media AS duracion_anterior,
        anterior.range AS autonomia_anterior
    FROM modelo_ordenado actual
    LEFT JOIN modelo_ordenado anterior 
        ON actual.numero_orden = anterior.numero_orden + 1
)
SELECT 
    numero_orden AS "Número de orden",
    model->>'en' AS "Modelo de avión",
    range AS "Autonomía",
    cantidad_vuelos AS "Cantidad de vuelos",
    ROUND(100.0 * cantidad_vuelos / total_vuelos_llegados, 2) AS "Porcentaje de vuelos (%)",
    ROUND(duracion_media, 2) AS "Duración media (horas)",
    ROUND((duracion_media - duracion_anterior), 2) AS "Diferencia de duración",
    (range - autonomia_anterior) AS "Diferencia de autonomía",
    RANK() OVER (ORDER BY duracion_media DESC) AS "Puesto por duración media"
FROM comparacion
ORDER BY range ASC;
""".strip()

consulta_5 = """
WITH pasajeros AS (
    SELECT bp.flight_id, t.book_ref, bp.ticket_no,
           TRY_CAST(regexp_extract(bp.seat_no, '^[0-9]+') AS INTEGER) AS fila
    FROM boarding_passes bp
    JOIN tickets t ON t.ticket_no = bp.ticket_no
    WHERE bp.seat_no IS NOT NULL
), metricas AS (
    SELECT a.aircraft_code,
           json_extract_string(CAST(a.model AS JSON), '$.en') AS modelo_avion,
           COUNT(*) AS cantidad_parejas,
           COUNT(*) FILTER (WHERE p1.fila = p2.fila) AS parejas_misma_fila,
           COUNT(*) FILTER (WHERE ABS(p1.fila - p2.fila) <= 1) AS parejas_cercanas,
           (SELECT COUNT(DISTINCT TRY_CAST(regexp_extract(s.seat_no, '^[0-9]+') AS INTEGER))
            FROM seats s
            WHERE s.aircraft_code = a.aircraft_code) AS filas_distintas
    FROM pasajeros p1
    JOIN pasajeros p2 ON p1.flight_id = p2.flight_id
                     AND p1.book_ref = p2.book_ref
                     AND p1.ticket_no < p2.ticket_no
    JOIN flights f ON f.flight_id = p1.flight_id
    JOIN aircrafts_data a ON a.aircraft_code = f.aircraft_code
    GROUP BY a.aircraft_code, a.model
)
SELECT RANK() OVER (
           ORDER BY 100.0 * parejas_misma_fila / cantidad_parejas DESC
       ) AS puesto,
       modelo_avion,
       cantidad_parejas,
       parejas_misma_fila,
       ROUND(100.0 * parejas_misma_fila / cantidad_parejas, 2) AS porcentaje_misma_fila,
       ROUND(100.0 * parejas_cercanas / cantidad_parejas, 2) AS porcentaje_misma_o_contigua,
       filas_distintas
FROM metricas
ORDER BY puesto, modelo_avion;
""".strip()

consulta_6 = """
WITH salidos AS (                                   -- CTE considerando solo vuelos que salieron
    SELECT flight_no,
           CAST(CAST(scheduled_departure AS TIMESTAMPTZ)
                AT TIME ZONE 'Europe/Moscow' AS DATE) AS dia,    -- día programado (hora local)
           aircraft_code,
           -- retraso grave (>60 min)
           CAST(date_diff('second',
                          CAST(scheduled_departure AS TIMESTAMPTZ),
                          TRY_CAST(actual_departure AS TIMESTAMPTZ)) > 3600 AS INTEGER) AS grave
    FROM flights
    WHERE status IN ('Arrived', 'Departed')         -- llegaron o en vuelo
),
pares AS (                                          -- SELF JOIN para vuelo del día D con el del día D+1
    SELECT a.aircraft_code,                         -- modelo del Día 1
           a.grave AS g1,
           b.grave AS g2
    FROM salidos a
    JOIN salidos b
      ON  b.flight_no = a.flight_no
      AND b.dia       = a.dia + 1
)
SELECT m.nombre_modelo                                             AS "Modelo de avión",
       m.pares                                                     AS "Pares de días consecutivos",
       m.graves_1                                                  AS "Pares con retraso grave en el día 1",
       ROUND(100.0 * m.graves_1 / m.pares, 2)                      AS "Porcentaje de retraso grave día 1",
       ROUND(100.0 * m.rep_si / m.graves_1, 2)                     AS "Porcentaje grave del día 2 si día 1 grave",
       ROUND(100.0 * m.rep_no / (m.pares - m.graves_1), 2)         AS "Porcentaje grave del día 2 si día 1 no grave",
       ROUND(1.0 * m.rep_si * (m.pares - m.graves_1)
                 / NULLIF(m.rep_no * m.graves_1, 0), 2)            AS "Cociente de repetición",
       ROUND(100.0 * m.rep_si / m.graves_1 - g.pct_global, 2)      AS "Diferencia vs. base",
       ROUND(100.0 * m.pares / SUM(m.pares) OVER (), 2)            AS "Porcentaje de pares entre los modelos mostrados",
       RANK() OVER (ORDER BY 1.0 * m.rep_si * (m.pares - m.graves_1)
                           / NULLIF(m.rep_no * m.graves_1, 0) DESC) AS "Puesto por cociente"
FROM (                                              -- subconsulta para los agregados por modelo
    SELECT json_extract_string(CAST(ac.model AS JSON), '$.en') AS nombre_modelo,
           COUNT(*)                  AS pares,
           SUM(p.g1)                 AS graves_1,
           SUM(p.g1 * p.g2)          AS rep_si,        -- grave -> grave
           SUM((1 - p.g1) * p.g2)    AS rep_no         -- no grave -> grave
    FROM pares p
    JOIN aircrafts_data ac ON ac.aircraft_code = p.aircraft_code
    GROUP BY ac.aircraft_code, ac.model
    HAVING SUM(p.g1) >= 30
) m
CROSS JOIN (                                        -- porcentaje de repetición en toda la base
    SELECT 100.0 * SUM(g1 * g2) / SUM(g1) AS pct_global FROM pares
) g
ORDER BY "Puesto por cociente";
""".strip()

# Las columnas y las claves de orden corresponden a la base original de vuelos.
fuentes_pregunta_1 = (
    ("flights", ("flight_id", "departure_airport", "arrival_airport"), ("flight_id",)),
    ("ticket_flights", ("ticket_no", "flight_id", "amount"), ("ticket_no", "flight_id")),
    ("airports_data", ("airport_code", "airport_name"), ("airport_code",)),
)
fuentes_pregunta_2 = (
    ("bookings", ("book_ref", "book_date", "total_amount"), ("book_ref",)),
)
fuentes_pregunta_3 = (
    ("flights", ("flight_id", "aircraft_code", "status", "actual_departure", "actual_arrival"), ("flight_id",)),
    ("aircrafts_data", ("aircraft_code", "model", "range"), ("aircraft_code",)),
)
fuentes_pregunta_5 = (
    ("tickets", ("ticket_no", "book_ref"), ("ticket_no",)),
    ("boarding_passes", ("ticket_no", "flight_id", "seat_no"), ("ticket_no", "flight_id")),
    ("flights", ("flight_id", "aircraft_code"), ("flight_id",)),
    ("aircrafts_data", ("aircraft_code", "model"), ("aircraft_code",)),
    ("seats", ("aircraft_code", "seat_no"), ("aircraft_code", "seat_no")),
)
fuentes_pregunta_6 = (
    ("flights", ("flight_id", "flight_no", "scheduled_departure", "actual_departure",
                 "status", "aircraft_code"), ("flight_id",)),
    ("aircrafts_data", ("aircraft_code", "model"), ("aircraft_code",)),
)


def leer_tabla(supabase, nombre, columnas, claves):
    registros = []
    cursor = None

    while True:
        consulta = supabase.table(nombre).select(",".join(columnas)).limit(1000)
        for clave in claves:
            consulta = consulta.order(clave)

        if cursor is not None:
            if len(claves) == 1:
                consulta = consulta.gt(claves[0], cursor[0])
            else:
                primera, segunda = claves
                valor_primero, valor_segundo = cursor
                consulta = consulta.gte(primera, valor_primero).or_(
                    f"{primera}.gt.{valor_primero},"
                    f"and({primera}.eq.{valor_primero},{segunda}.gt.{valor_segundo})"
                )

        filas = consulta.execute().data
        if not filas:
            break

        siguiente = tuple(filas[-1][clave] for clave in claves)
        if siguiente == cursor:
            raise ValueError(f"La lectura de {nombre} no avanzó a la siguiente página.")

        registros.extend(tuple(fila[columna] for columna in columnas) for fila in filas)
        cursor = siguiente

    if not registros:
        raise ValueError(f"Supabase no devolvió filas de {nombre}. Revisa el permiso de lectura.")

    return pd.DataFrame.from_records(registros, columns=columnas)


@st.cache_data(persist="disk", show_spinner="Leyendo tablas de Supabase y calculando el resultado…")
def calcular_resultado(sql, fuentes, proyecto_url):
    # El URL forma parte de la clave de caché para separar los proyectos de Supabase.
    supabase = get_supabase_client()
    with duckdb.connect(":memory:") as conexion:
        for nombre, columnas, claves in fuentes:
            conexion.register(nombre, leer_tabla(supabase, nombre, columnas, claves))
        return conexion.execute(sql).df()


def mostrar_resultado(numero, consulta, fuentes, carga_automatica):
    st.subheader("Resultados")

    if not carga_automatica:
        estado = f"pregunta_{numero}_cargada"
        if not st.session_state.get(estado, False):
            if not st.button("Cargar resultados desde Supabase", key=f"cargar_pregunta_{numero}"):
                return None
            st.session_state[estado] = True

    try:
        proyecto_url = st.secrets["SUPABASE_URL"]
    except (KeyError, FileNotFoundError):
        st.error(
            "Este Streamlit no tiene configurada la conexión a Supabase. "
            "Abre la app publicada del equipo o pide a quien la administra "
            "que configure la conexión de lectura de esta copia."
        )
        return None

    if st.button("Actualizar resultados desde Supabase", key=f"actualizar_pregunta_{numero}"):
        calcular_resultado.clear(consulta, fuentes, proyecto_url)

    try:
        return calcular_resultado(consulta, fuentes, proyecto_url)
    except Exception as error:
        st.error(f"No se pudo leer el resultado de la pregunta {numero} desde Supabase. {error}")
        return None


def mostrar_pregunta_1(carga_automatica):
    st.header("Pregunta 1. Ingresos por Par de Aeropuertos")
    st.write(
        "Muestra los diez pares de mayor ingreso total con su puesto, los dos aeropuertos, "
        "los tramos vendidos en ambos sentidos y el análisis financiero y de desequilibrio."
    )
    with st.expander("Ver consulta SQL", expanded=False):
        st.code(consulta_1, language="sql")
    
    resultado_1 = mostrar_resultado(1, consulta_1, fuentes_pregunta_1, carga_automatica)
    if resultado_1 is None:
        return
    if resultado_1.empty:
        st.info("La consulta no devolvió resultados.")
        return

    st.dataframe(resultado_1, hide_index=True)

    st.subheader("Interpretación de los resultados")
    st.write(
        "Los resultados muestran los pares de aeropuertos con mayor volumen de ingresos acumulados "
        "en ambas direcciones, ordenados del 1 al 10, permitiendo evaluar el peso de cada ruta "
        "sobre el total de la red y su asimetría o desequilibrio comercial."
    )


def mostrar_pregunta_2(carga_automatica):
    st.header("Pregunta 2. Mayores saltos diarios de venta")
    st.write(
        "Identificar los ocho días con mayor aumento absoluto del importe total de las reservas "
        "respecto al día calendario inmediatamente anterior, excluyendo los primeros catorce días de la serie."
    )
    with st.expander("Ver consulta SQL", expanded=False):
        st.code(consulta_2, language="sql")
    resultado_2 = mostrar_resultado(2, consulta_2, fuentes_pregunta_2, carga_automatica)
    if resultado_2 is None:
        return
    if resultado_2.empty:
        st.info("La consulta no devolvió resultados.")
        return

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


def mostrar_pregunta_3(carga_automatica):
    st.header("Pregunta 3. Escalera de Autonomía de la Flota")
    st.write(
        "Comparamos la autonomía y la duración real media de los vuelos por modelo de avión, "
        "ordenados de menor a mayor autonomía y cruzados con el modelo anterior."
    )
    with st.expander("Ver consulta SQL", expanded=False):
        st.code(consulta_3, language="sql")

    resultado_3 = mostrar_resultado(3, consulta_3, fuentes_pregunta_3, carga_automatica)
    if resultado_3 is None:
        return

    st.dataframe(resultado_3, hide_index=True)

    st.subheader("Interpretación de los resultados")
    st.write(
        "Los resultados nos ordenanlos modelos de aeronaves según su autonomía, permitiendo analizar "
        "si los aviones con mayor rango efectivamente operan vuelos más largos en promedio, "
        "así como la variacion en la duración y autonomía respecto al modelo precedente."
    )


def mostrar_pregunta_5(carga_automatica):
    st.header("Pregunta 5. Acompañantes y asignación de asientos")
    st.write(
        "Comparamos las filas asignadas a pasajeros de la misma reserva "
        "y del mismo vuelo, por modelo de avión."
    )
    with st.expander("Ver consulta SQL", expanded=False):
        st.code(consulta_5, language="sql")
    resultado_5 = mostrar_resultado(5, consulta_5, fuentes_pregunta_5, carga_automatica)
    if resultado_5 is None:
        return
    if resultado_5.empty:
        st.info("La consulta no devolvió parejas de pasajeros.")
        return

    st.dataframe(
        resultado_5.rename(columns={
            "puesto": "Puesto",
            "modelo_avion": "Modelo de avión",
            "cantidad_parejas": "Cantidad de parejas",
            "parejas_misma_fila": "Parejas en la misma fila",
            "porcentaje_misma_fila": "% misma fila",
            "porcentaje_misma_o_contigua": "% misma fila o contigua",
            "filas_distintas": "Filas distintas",
        }),
        hide_index=True,
    )

    lider = resultado_5.iloc[0]
    total = f"{int(lider['cantidad_parejas']):,}".replace(",", ".")
    misma = f"{int(lider['parejas_misma_fila']):,}".replace(",", ".")
    porcentaje = f"{lider['porcentaje_misma_fila']:.2f}".replace(".", ",")
    cercana = f"{lider['porcentaje_misma_o_contigua']:.2f}".replace(".", ",")

    st.subheader("Interpretación de los resultados")

    st.write(
        f"El {lider['modelo_avion']} ocupa el primer puesto. De {total} parejas, "
        f"{misma} se sentaron en la misma fila ({porcentaje} %). "
        f"El {cercana} % se sentó en la misma fila o a una fila de distancia."
    )

def mostrar_pregunta_6(carga_automatica):
    st.header("Pregunta 6. Repetición de retrasos graves")
    st.write(
        "Se mide si un vuelo que sale con retraso grave (más de 60 minutos) tiende a repetir este patrón "
        "al día siguiente, uniendo el mismo número de vuelo en días consecutivos por modelo de avión."
    )
    with st.expander("Ver consulta SQL", expanded=False):
        st.code(consulta_6, language="sql")
    resultado_6 = mostrar_resultado(6, consulta_6, fuentes_pregunta_6, carga_automatica)
    if resultado_6 is None:
        return
    if resultado_6.empty:
        st.info("La consulta no devuelve modelos con suficientes pares.")
        return

    st.dataframe(resultado_6, hide_index=True)

    def num(valor):
        return f"{valor:.2f}".replace(".", ",")

    primero = resultado_6.iloc[0]
    ultimo = resultado_6.iloc[-1]

    st.subheader("Interpretación de los resultados")

    st.write(
        f"Si los retrasos se debieran a causas persistentes, el cociente de repetición "
        f"sería significativamente mayor que 1. En este caso, va de {num(ultimo['Cociente de repetición'])} "
        f"a {num(primero['Cociente de repetición'])}."
    )
    st.write(
        f"El {primero['Modelo de avión']} tiene el cociente más alto: "
        f"{num(primero['Porcentaje grave del día 2 si día 1 grave'])} % de retraso grave el día 2 "
        f"cuando el día 1 fue grave, frente a "
        f"{num(primero['Porcentaje grave del día 2 si día 1 no grave'])} % cuando no lo fue. "
        f"El {ultimo['Modelo de avión']} tiene el más bajo "
        f"({num(ultimo['Diferencia vs. base'])} puntos porcentuales respecto a la base)."
    )
    if resultado_6["Cociente de repetición"].max() < 1.5:
        st.write(
            "Haber salido muy tarde un día influye mínimamente en la probabilidad de salir muy tarde "
            "al siguiente. Los retrasos graves parecen ocurrir de forma independiente de un día "
            "a otro, y no por motivos asociados al vuelo o al modelo formalmente."
        )
    else:
        st.write(
            "Al menos un modelo repite el retraso grave con más frecuencia que cuando "
            "el día anterior fue normal, lo que sugiere causas persistentes en esos casos específicamente."
        )
    st.write(
        f"Solo {len(resultado_6)} modelos tienen, al menos, 30 pares con retraso grave el primer "
        f"día, por lo que se debe tener cautela con las diferencias entre ellos."
    )


nombres_pestanas = [f"Pregunta {numero}" for numero in range(1, 7)]
pestanas_dinamicas = "on_change" in signature(st.tabs).parameters

if pestanas_dinamicas:
    pestanas = st.tabs(
        nombres_pestanas, default="Pregunta 2", key="preguntas_cuestionario", on_change="rerun"
    )
else:
    pestanas = st.tabs(nombres_pestanas)

preguntas_disponibles = {
    1: mostrar_pregunta_1,
    2: mostrar_pregunta_2,
    3: mostrar_pregunta_3,
    5: mostrar_pregunta_5,
    6: mostrar_pregunta_6,
}

for numero, pestana in enumerate(pestanas, start=1):
    if pestanas_dinamicas and not pestana.open:
        continue

    with pestana:
        mostrar_pregunta = preguntas_disponibles.get(numero)
        if mostrar_pregunta is None:
            st.info("Pregunta pendiente de incorporar.")
        else:
            mostrar_pregunta(pestanas_dinamicas)
