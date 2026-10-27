-- LIMPIEZA FINAL (BASE DE DATOS NORMALIZADA)

-- A. Copiar solo las columnas que se utilizarán para dar respuesta a los objetivos

CREATE TABLE lim_aeropuertos (
    codigo    TEXT PRIMARY KEY CHECK (length(codigo) = 3),
    nombre    TEXT NOT NULL,
    ciudad_id INTEGER NOT NULL REFERENCES ciudades (ciudad_id)
);

INSERT INTO lim_aeropuertos 
SELECT codigo, nombre, ciudad_id
FROM aeropuertos;

CREATE TABLE lim_aeronaves (
    codigo TEXT PRIMARY KEY,
    modelo TEXT NOT NULL
);

INSERT INTO lim_aeronaves 
SELECT codigo, modelo 
FROM aeronaves;

CREATE TABLE lim_rutas (
    numero_vuelo    TEXT PRIMARY KEY,
    origen          TEXT NOT NULL REFERENCES aeropuertos (codigo),
    destino         TEXT NOT NULL REFERENCES aeropuertos (codigo),
    aeronave_codigo TEXT NOT NULL REFERENCES aeronaves (codigo),
    duracion_min    INTEGER NOT NULL CHECK (duracion_min > 0),
    CHECK (origen <> destino)
);

INSERT INTO lim_rutas 
SELECT numero_vuelo, origen, destino, aeronave_codigo, duracion_min 
FROM rutas;

-- Tomar solo vuelos 'Arrived' (estado_id = 5), con fechas unificadas y retrasos precalculados.
--  Se descartan los vuelos que no salieron y aterrizaron, es decir, que no tienen salida real y/o llegada real (NULL).
--  Quedan solo los de estado "Arrived", siendo 16.707
--  Al obtener las fechas originales con la hora UTC+03 de Moscow (Moscú) para todos los aeropuertos de todas las ciudades, 
--  se elimina este formato y se acomoda el formato datetime. Los retrasos no se alteran.
-- Además, se agrega la hora local de salida (hora de Moscu + (utc_offset_origen - 3) y el día de la semana.

CREATE TABLE lim_vuelos (
    vuelo_id              INTEGER PRIMARY KEY,
    numero_vuelo          TEXT    NOT NULL REFERENCES rutas (numero_vuelo),
    origen                TEXT    NOT NULL REFERENCES aeropuertos (codigo),
    destino               TEXT    NOT NULL REFERENCES aeropuertos (codigo),
    aeronave_codigo       TEXT    NOT NULL REFERENCES aeronaves (codigo),
    salida_programada     TEXT    NOT NULL,
    salida_real           TEXT    NOT NULL, 
    llegada_programada    TEXT    NOT NULL,
    llegada_real          TEXT    NOT NULL, -- hora en UTC+3
    retraso_salida_min    INTEGER NOT NULL,
    retraso_llegada_min   INTEGER NOT NULL, -- retraso en min
    salida_prog_local     TEXT    NOT NULL, 
    hora_salida_local     INTEGER NOT NULL CHECK (hora_salida_local BETWEEN 0 AND 23), -- hora local de los aeropuertos de origen
    franja_horaria        TEXT    NOT NULL,
    dia_semana_num        INTEGER NOT NULL CHECK (dia_semana_num BETWEEN 1 AND 7),  -- 1 = Lunes, 2 = Martes...
    dia_semana            TEXT    NOT NULL,
    salio_a_tiempo        INTEGER NOT NULL CHECK (salio_a_tiempo IN (0,1)),   -- retraso_salida  <= 0
    llego_a_tiempo        INTEGER NOT NULL CHECK (llego_a_tiempo IN (0,1)),   -- retraso_llegada <= 0
    salio_a_tiempo_llego_tarde INTEGER NOT NULL CHECK (salio_a_tiempo_llego_tarde IN (0,1)), 
    demora_salida_15      INTEGER NOT NULL CHECK (demora_salida_15  IN (0,1)), -- retraso_salida  > 15 (según criterio IATA)
    demora_llegada_15     INTEGER NOT NULL CHECK (demora_llegada_15 IN (0,1)), -- retraso_llegada > 15
    CHECK (llegada_real  > salida_real),
    CHECK (llegada_programada > salida_programada)
);

INSERT INTO lim_vuelos
WITH base AS (
    SELECT v.vuelo_id,
           v.numero_vuelo,
           r.origen,
           r.destino,
           r.aeronave_codigo,
           substr(v.salida_programada,  1, 19) AS sp, --recortando a datetime
           substr(v.salida_real,        1, 19) AS sr,
           substr(v.llegada_programada, 1, 19) AS lp,
           substr(v.llegada_real,       1, 19) AS lr,
           CASE c.zona_horaria
              WHEN 'Europe/Kaliningrad' THEN 2
              WHEN 'Europe/Moscow'      THEN 3
              WHEN 'Europe/Volgograd'   THEN 3
              WHEN 'Europe/Samara'      THEN 4
              WHEN 'Asia/Yekaterinburg' THEN 5
              WHEN 'Asia/Omsk'          THEN 6
              WHEN 'Asia/Novosibirsk'   THEN 7
              WHEN 'Asia/Novokuznetsk'  THEN 7
              WHEN 'Asia/Krasnoyarsk'   THEN 7
              WHEN 'Asia/Irkutsk'       THEN 8
              WHEN 'Asia/Chita'         THEN 9
              WHEN 'Asia/Yakutsk'       THEN 9
              WHEN 'Asia/Vladivostok'   THEN 10
              WHEN 'Asia/Magadan'       THEN 11
              WHEN 'Asia/Sakhalin'      THEN 11
              WHEN 'Asia/Kamchatka'     THEN 12
              WHEN 'Asia/Anadyr'        THEN 12
           END AS utc_offset_h                   -- Ciudades y desplazamiento UTC de cada zona horaria
                       -- (verificando con la base de datos tz de IANA: Volgograd=+3, Magadan=+11, Chita=+9, Novosibirsk=+7)
    FROM vuelos v
    JOIN rutas       r ON r.numero_vuelo = v.numero_vuelo
    JOIN aeropuertos a ON a.codigo       = r.origen
    JOIN ciudades    c ON c.ciudad_id    = a.ciudad_id
    WHERE v.estado_id = 5                      -- 'Arrived', con horas de salida y de llegada reales
      AND v.salida_real  IS NOT NULL
      AND v.llegada_real IS NOT NULL
),
calc AS (
    SELECT *,
           (strftime('%s', sr) - strftime('%s', sp)) / 60 AS ds,
           (strftime('%s', lr) - strftime('%s', lp)) / 60 AS da, --cálculo de retrasos en minutos
           datetime(sp, printf('%+d hours', utc_offset_h - 3)) AS sp_local --cálculo de salida programada en hora local
    FROM base
)
SELECT vuelo_id, numero_vuelo, origen, destino, aeronave_codigo,
       sp, sr, lp, lr,
       ds, da,
       sp_local,
       CAST(strftime('%H', sp_local) AS INTEGER),
       CASE WHEN CAST(strftime('%H', sp_local) AS INTEGER) < 6  THEN '1. Madrugada (00-05)'
            WHEN CAST(strftime('%H', sp_local) AS INTEGER) < 12 THEN '2. Dia (06-11)'
            WHEN CAST(strftime('%H', sp_local) AS INTEGER) < 18 THEN '3. Tarde (12-17)'
            ELSE                                                     '4. Noche (18-23)' END,
       CASE strftime('%w', sp_local) WHEN '0' THEN 7 ELSE CAST(strftime('%w', sp_local) AS INTEGER) END,
       CASE strftime('%w', sp_local) WHEN '1' THEN 'Lunes'  WHEN '2' THEN 'Martes' WHEN '3' THEN 'Miercoles'
                                     WHEN '4' THEN 'Jueves' WHEN '5' THEN 'Viernes' WHEN '6' THEN 'Sabado'
                                     ELSE 'Domingo' END,
       ds <= 0,
       da <= 0,
       ds <= 0 AND da > 0,
       ds > 15,
       da > 15
FROM calc;

CREATE INDEX ix_vuelos_ruta   ON vuelos (numero_vuelo);
CREATE INDEX ix_vuelos_origen ON vuelos (origen);
CREATE INDEX ix_vuelos_destino ON vuelos (destino);
CREATE INDEX ix_vuelos_aeronave ON vuelos (aeronave_codigo); --Para facilitar los group by

-- Eliminando laa tablas originales
DROP TABLE aircrafts_data;
DROP TABLE airports_data;
DROP TABLE seats;
DROP TABLE tickets;
DROP TABLE flights;
DROP TABLE bookings;
DROP TABLE boarding_passes;
DROP TABLE ticket_flights;


