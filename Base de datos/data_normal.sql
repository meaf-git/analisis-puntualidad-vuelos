-- 2. CARGA DE DATOS (DML)

BEGIN TRANSACTION;

--- 1. Ciudades (parseo de columnas JSON)
INSERT INTO ciudades (nombre, nombre_ru, zona_horaria)
SELECT json_extract(city, '$.en'),
       MIN(json_extract(city, '$.ru')),
       MIN(timezone)
FROM airports_data
GROUP BY json_extract(city, '$.en')
ORDER BY 1;

--- 2. Aeropuertos (separación de coordenadas geográficas)
INSERT INTO aeropuertos (codigo, nombre, nombre_ru, ciudad_id, longitud, latitud)
SELECT a.airport_code,
       json_extract(a.airport_name, '$.en'),
       json_extract(a.airport_name, '$.ru'),
       c.ciudad_id, 
       CAST(substr(a.coordinates, 2, instr(a.coordinates, ',') - 2) AS REAL), -- recorte de cadena antes de la coma (longitud)
       CAST(substr(a.coordinates,
                   instr(a.coordinates, ',') + 1,
                   length(a.coordinates) - instr(a.coordinates, ',') - 1) AS REAL) -- recorte de cadena después de la coma (latitud)
FROM airports_data a
JOIN ciudades c ON c.nombre = json_extract(a.city, '$.en')
ORDER BY a.airport_code;

--- 3. Aeronaves (información bilingue)
INSERT INTO aeronaves (codigo, modelo, modelo_ru, autonomia_km)
SELECT aircraft_code,
       json_extract(model, '$.en'),
       json_extract(model, '$.ru'),
       range
FROM aircrafts_data
ORDER BY aircraft_code;

--- 4. Clases tarifarias (catálogo de tarifas)
INSERT INTO clases_tarifarias (clase_id, codigo, nombre, orden) VALUES
    (1, 'Economy',  'Economica', 1),
    (2, 'Comfort',  'Confort',   2),
    (3, 'Business', 'Ejecutiva', 3);

--- 5. Estados de vuelo (los posibles estados del vuelo)
INSERT INTO estados_vuelo (estado_id, codigo, descripcion) VALUES
    (1, 'Scheduled', 'Programado, aún no operado al cierre del volcado'),
    (2, 'On Time',   'En horario, aún no operado'),
    (3, 'Delayed',   'Con demora anunciada, aún no operado'),
    (4, 'Departed',  'En vuelo al cierre del volcado'),
    (5, 'Arrived',   'Completado'),
    (6, 'Cancelled', 'Cancelado');

--- 6. Asientos (asientos y su clase correspondiente)
INSERT INTO asientos (aeronave_codigo, numero, clase_id)
SELECT s.aircraft_code, s.seat_no, c.clase_id
FROM seats s
JOIN clases_tarifarias c ON c.codigo = s.fare_conditions;

--- 7. Rutas (cálculo de la duración aproximada en minutos a partir de las fechas programadas)
INSERT INTO rutas (numero_vuelo, origen, destino, aeronave_codigo, duracion_min)
SELECT flight_no,
       MIN(departure_airport),
       MIN(arrival_airport),
       MIN(aircraft_code),
       CAST(ROUND(MIN((julianday(scheduled_arrival || ':00') - julianday(scheduled_departure || ':00')) * 1440)) AS INTEGER) -- convierte diferencia de fechas a minutos
FROM flights
GROUP BY flight_no
ORDER BY flight_no;

--- 8. Vuelos (uso seguro de NULLIF para formateo de timestamps)
INSERT INTO vuelos (vuelo_id, numero_vuelo, estado_id, salida_programada, llegada_programada, salida_real, llegada_real)
SELECT f.flight_id,
       f.flight_no,
       e.estado_id,
       f.scheduled_departure || ':00', --para asegurar formato completo en minutos
       CASE WHEN substr(f.scheduled_arrival, 17, 1) = ':' --si la fecha incluye segundos, conserva los 19 caracteres. sino, toma 16 y añade :00
            THEN substr(f.scheduled_arrival, 1, 19) ELSE substr(f.scheduled_arrival, 1, 16) || ':00' END,
       CASE WHEN f.actual_departure IS NOT NULL AND f.actual_departure <> '\N' -- manejo de nulos
            THEN f.actual_departure || ':00' ELSE NULL END,
       CASE WHEN f.actual_arrival IS NOT NULL AND f.actual_arrival <> '\N' 
            THEN f.actual_arrival || ':00' ELSE NULL END
FROM flights f
JOIN estados_vuelo e ON e.codigo = f.status
ORDER BY f.flight_id;

--- 9. Reservas
INSERT INTO reservas (localizador, fecha_reserva)
SELECT book_ref, book_date || ':00'
FROM bookings
ORDER BY book_ref;

--- 10. Pasajes
INSERT INTO pasajes (numero_pasaje, localizador, pasajero_id)
SELECT ticket_no, book_ref, passenger_id
FROM tickets
ORDER BY ticket_no;

--- 11. Cupones
INSERT INTO cupones (numero_pasaje, vuelo_id, clase_id, monto)
SELECT tf.ticket_no, tf.flight_id, c.clase_id, tf.amount
FROM ticket_flights tf
JOIN clases_tarifarias c ON c.codigo = tf.fare_conditions;

--- 12. Tarjetas de embarque
INSERT INTO tarjetas_embarque (numero_pasaje, vuelo_id, numero_embarque, asiento)
SELECT ticket_no, flight_id, boarding_no, seat_no
FROM boarding_passes;

-- 3. VISTAS

CREATE VIEW v_vuelo AS --vuelo con cálculo proyectado de llegada e información de ruta
SELECT v.vuelo_id,
       v.numero_vuelo,
       r.origen,
       r.destino,
       r.aeronave_codigo,
       e.codigo AS estado,
       v.salida_programada,
       datetime(substr(v.salida_programada, 1, 19), '+' || r.duracion_min || ' minutes') || '+03:00' AS llegada_programada, --recalculando la fecha de llegada sumando la duración en minutos de la ruta
       v.salida_real,
       v.llegada_real
FROM vuelos v
JOIN rutas         r ON r.numero_vuelo = v.numero_vuelo
JOIN estados_vuelo e ON e.estado_id    = v.estado_id;



COMMIT;




