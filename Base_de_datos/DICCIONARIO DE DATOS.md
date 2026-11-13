# Documentación de Normalización y Diccionario de Datos

Documentación del proceso de normalización aplicado a la base de datos `travel.sqlite`  y descripción
campo por campo de las doce tablas del modelo resultante, con su procedencia,
tipo, restricciones y porcentaje de nulos medido sobre la base ya cargada.

Este documento sigue la secuencia cronológica del trabajo realizado: se presentan primero los datos de origen, luego el diagnóstico de la fuente y el proceso de normalización paso a paso, y concluye con el diccionario de datos del modelo resultante.

## Archivos actuales del proyecto

| Archivo | Contenido |
|---|---|
| `travel.sqlite` | Base de origen: 8 tablas sin normalizar. |
| `esquema_normal.sql` | DDL del modelo normalizado: 12 tablas con llaves, restricciones y dominios. |
| `data_normal.sql` | Carga de datos de la fuente hacia el modelo normalizado y creación de la vista `v_vuelo`. |


## Convención de procedencia

Cada campo del diccionario se marca con una de las siguientes tres etiquetas:

| Etiqueta | Significado |
|---|---|
| **FUENTE** | Se toma tal cual de `travel.sqlite`, sin modificar su valor (puede cambiar de nombre). |
| **DERIVADO** | Se calcula o se extrae de campos de la fuente mediante una regla explícita. |
| **CONSTRUIDO** | No existe en la fuente: es un catálogo o una clave definida durante la normalización. |


---

## 1. Datos originales

La base describe la operación de una aerolínea rusa. Los vuelos programados
cubren del **16 de julio al 14 de septiembre de 2017**, y las reservas se
registran entre el **21 de junio y el 15 de agosto de 2017**.

| Tabla de origen | Filas | Descripción |
|---|---:|---|
| `aircrafts_data` | 9 | Modelos de aeronave y su alcance. |
| `airports_data` | 104 | Aeropuertos: nombre y ciudad en JSON, coordenadas como `point`. |
| `flights` | 33.121 | Vuelos programados y, cuando se operaron, sus horas reales de salida y llegada. |
| `seats` | 1.339 | Asientos de cada modelo de aeronave y su respectiva clase ("Business", "Economy", "Comfort"). |
| `bookings` | 262.788 | Reservas con su monto total. |
| `tickets` | 366.733 | Pasajes asociados a una reserva. |
| `ticket_flights` | 1.045.726 | Segmentos de cada pasaje: vuelo, clase y monto. |
| `boarding_passes` | 579.686 | Tarjetas de embarque: orden y asiento. |

### 1.1 Esquema original

```sql
aircrafts_data  (aircraft_code PK, model jsonb, range integer)
airports_data   (airport_code PK, airport_name jsonb, city jsonb,
                 coordinates point, timezone text)
flights         (flight_id PK, flight_no, scheduled_departure, scheduled_arrival,
                 departure_airport, arrival_airport, status, aircraft_code,
                 actual_departure, actual_arrival)
seats           (aircraft_code, seat_no, fare_conditions)
bookings        (book_ref PK, book_date, total_amount)
tickets         (ticket_no PK, book_ref, passenger_id)
ticket_flights  (ticket_no, flight_id, fare_conditions, amount)
boarding_passes (ticket_no, flight_id, boarding_no, seat_no)
```

## 2. Diagnóstico de la fuente

Antes de realizar las modificaciones, se identificaron ocho problemas:

| # | Problema | Tabla |
|---|---|---|
| P1 | Valores no atómicos: nombres y ciudades en formato JSON, coordenadas como cadena `(lon,lat)`. | `airports_data`, `aircrafts_data` |
| P2 | La ciudad, su traducción y su zona horaria se repiten en cada aeropuerto. | `airports_data` |
| P3 | Origen, destino, aeronave y duración se repiten en cada vuelo del mismo `flight_no`. | `flights` |
| P4 | Textos repetidos muchas veces (`status`, `fare_conditions`) sin catálogo ni dominio. | `flights`, `seats`, `ticket_flights` |
| P5 | Dato derivable almacenado: `bookings.total_amount`. | `bookings` |
| P6 | Nulos escritos como el texto `\N`. | `flights` |
| P7 | Marcas de tiempo con desplazamiento abreviado (`+03`) y sin formato uniforme. | `flights`, `bookings` |
| P8 | Ninguna restricción de dominio (rangos, montos positivos, origen distinto de destino). | Varias |

---

## 3. Proceso de normalización paso a paso


| Pasos | Tabla destino | Tabla origen | Filas | Motivo principal |
|---:|---|---|---:|---|
| 1 | `ciudades` | `airports_data` | 101 | Extrae la ciudad (2FN/3FN) |
| 2 | `aeropuertos` | `airports_data` | 104 | Atomiza JSON y coordenadas (1FN) |
| 3 | `aeronaves` | `aircrafts_data` | 9 | Atomiza JSON (1FN) |
| 4 | `clases_tarifarias` | `seats`, `ticket_flights` | 3 | Catálogo (3FN) |
| 5 | `estados_vuelo` | `flights.status` | 6 | Catálogo (3FN) |
| 6 | `asientos` | `seats` | 1.339 | Referencia catálogo y aeronave |
| 7 | `rutas` | `flights` | 710 | Elimina dependencia parcial (2FN) |
| 8 | `vuelos` | `flights` | 33.121 | Depura y referencia ruta y estado |
| 9 | `reservas` | `bookings` | 262.788 | Elimina dato derivable (3FN) |
| 10 | `pasajes` | `tickets` | 366.733 | Renombra y valida |
| 11 | `cupones` | `ticket_flights` | 1.045.726 | Entidad asociativa N:M |
| 12 | `tarjetas_embarque` | `boarding_passes` | 579.686 | FK compuesta y unicidades |
| 13 | `v_vuelo` | `vuelos`, `rutas`, `estados_vuelo` | 33.121 | Vista de consulta |

### Paso 1. `ciudades`

En `airports_data`, la ciudad es un JSON repetido por aeropuerto,
con su traducción y su zona horaria (P1, P2).

Por ende, se agrupa por el nombre en inglés extraído del JSON. La traducción
y la zona horaria se toman con `MIN()`, lo que no altera ningún valor porque en
cada grupo coinciden. La clave sustituta se asigna en orden alfabético.

```sql
INSERT INTO ciudades (nombre, nombre_ru, zona_horaria)
SELECT json_extract(city, '$.en'), MIN(json_extract(city, '$.ru')), MIN(timezone)
FROM airports_data
GROUP BY json_extract(city, '$.en')
ORDER BY 1;
```

| Antes (`airports_data.city`, `timezone`) | Después (`ciudades`) |
|---|---|
| `{"en": "Moscow", "ru": "Москва"}`, `Europe/Moscow`| `(45, 'Moscow', 'Москва', 'Europe/Moscow')` |
| `{"en": "Ulyanovsk", "ru": "Ульяновск"}`, `Europe/Samara`| `(87, 'Ulyanovsk', 'Ульяновск', 'Europe/Samara')` |

**Resultado:** 104 aeropuertos → 101 ciudades

### Paso 2. `aeropuertos`
Se tiene el nombre en JSON y coordenadas como cadena (P1).

Para ello, se separan los idiomas en dos columnas, se resuelve `ciudad_id`
contra `ciudades` y las coordenadas se cortan por la coma con `substr` e
`instr`, convirtiendo cada mitad a `REAL`.

| Antes | Después |
|---|---|
| `airport_name = {"en": "Domodedovo International Airport", "ru": "Домодедово"}` | `nombre = 'Domodedovo International Airport'`, `nombre_ru = 'Домодедово'` |
| `city = {"en": "Moscow", ...}` | `ciudad_id = 45` |
| `coordinates = (37.9062995910644531,55.4087982177734375)` | `longitud = 37.90629959106445`, `latitud = 55.40879821777344` |

Adicionalmente, se añaden `CHECK` de rango para longitud (−180 a 180) y latitud (−90 a 90), y
`length(codigo) = 3` para el código IATA.

### Paso 3. `aeronaves`

El modelo es un JSON bilingüe (P1).

Se separan `modelo` y `modelo_ru`, `range` pasa a `autonomia_km`
con `CHECK (autonomia_km > 0)`.

| Antes | Después |
|---|---|
| `('773', {"en": "Boeing 777-300", "ru": "Боинг 777-300"}, 11100)` | `('773', 'Boeing 777-300', 'Боинг 777-300', 11100)` |

### Paso 4. `clases_tarifarias`

`fare_conditions` es un texto repetido en 1.339 filas de `seats`
y en 1.045.726 de `ticket_flights`, sin un dominio declarado (P4).

Por ende, se extraen los tres valores existentes (`Economy`, `Comfort`,
`Business`) a un catálogo con clave sustituta, nombre en español y un campo
`orden` que expresa la jerarquía de la cabina. El valor original se conserva
como `codigo UNIQUE`.

| `clase_id` | `codigo` | `nombre` | `orden` |
|---:|---|---|---:|
| 1 | `Economy` | Económica | 1 |
| 2 | `Comfort` | Confort | 2 |
| 3 | `Business` | Ejecutiva | 3 |

### Paso 5. `estados_vuelo`

`flights.status` es un texto repetido en las 33.121 filas de los vuelos (P4).

Para esto, se crea un catálogo con los seis valores presentes en la fuente,
numerados según el ciclo de vida del vuelo, con una breve descripción (en español) de
lo que significa cada uno.

| `estado_id` | `codigo` | `descripcion` | Vuelos |
|---:|---|---|---:|
| 1 | `Scheduled` | Programado, aún no operado al cierre del volcado | 15.383 |
| 2 | `On Time` | En horario, aún no operado | 518 |
| 3 | `Delayed` | Con demora anunciada, aún no operado | 41 |
| 4 | `Departed` | En vuelo al cierre del volcado | 58 |
| 5 | `Arrived` | Completado | 16.707 |
| 6 | `Cancelled` | Cancelado | 414 |

### Paso 6. `asientos`

`seats` repite la clase en formato de texto.

Para ello, se carga cada asiento con su `clase_id` en lugar del texto,
mediante un `JOIN` al catálogo del paso 4. La llave primaria es compuesta
`(aeronave_codigo, numero)`: un mismo número de asiento existe en varios
modelos.

| Antes (`seats`) | Después (`asientos`) |
|---|---|
| `('773', '11A', 'Comfort')` | `('773', '11A', 2)` |

Distribución final: Economy (1.139), Comfort (48), Business (152).

### Paso 7. `rutas`

Origen, destino, aeronave y duración dependen de `flight_no` y no
del vuelo (`flight_id`). Existe una dependencia parcial (P3).

En consecuencia, se extrae una entidad con una fila por designador. La duración no
existe en la fuente formalmente, sino que se calcula como la diferencia entre la llegada y la
salida programadas en minutos.

```sql
CAST(ROUND(MIN((julianday(scheduled_arrival || ':00')
              - julianday(scheduled_departure || ':00')) * 1440)) AS INTEGER)
```

| Antes (`flights`) | Después (`rutas`) |
|---|---|
| `(1, 'PG0405', 09:35 → 10:30, 'DME', 'LED', '321')` | `('PG0405', 'DME', 'LED', '321', 55)` |
| `(3, 'PG0405', 09:35 → 10:30, 'DME', 'LED', '321')` | |
| `(5, 'PG0405', 09:35 → 10:30, 'DME', 'LED', '321')` | |

**Resultado:** 33.121 vuelos → 710 rutas, con duraciones de 25 a 530
minutos. Se añaden `CHECK (duracion_min > 0)` y `CHECK (origen <> destino)`.

### Paso 8. `vuelos`

Existen nulos escritos como `\N` y marcas de tiempo irregulares (P6, P7).

Para solventar esto:

1. `status` se sustituye por `estado_id` (JOIN con `estados_vuelo`).
2. `\N` y `NULL` se unifican en **`NULL`** para las horas.
3. A `salida_programada`, `salida_real` y `llegada_real` se les incluye `':00'` al
   final. La fuente trae el desplazamiento abreviado `+03`; el sufijo lo
   completa a `+03:00`, que es el formato ISO 8601 de la zona.
4. `llegada_programada` se recorta a 19 caracteres, sin desplazamiento.

| Campo | Antes (`flights`) | Después (`vuelos`) |
|---|---|---|
| `flight_no` / `numero_vuelo` | `PG0405` | `PG0405` (con FK a `rutas`) |
| `status` / `estado_id` | `Arrived` | `5` |
| `scheduled_departure` / `salida_programada` | `2017-07-16 09:35:00+03` | `2017-07-16 09:35:00+03:00` |
| `scheduled_arrival` / `llegada_programada` | `2017-07-16 10:30:00+03` | `2017-07-16 10:30:00` |
| `actual_departure` / `salida_real` | `2017-07-16 09:44:00+03` | `2017-07-16 09:44:00+03:00` |
| `actual_arrival` / `llegada_real` | `2017-07-16 10:39:00+03` | `2017-07-16 10:39:00+03:00` |
| `actual_departure` (vuelo 1185, `Scheduled`) | `\N` | `NULL` |

Se añade `CHECK (llegada_real IS NULL OR salida_real IS NULL OR llegada_real > salida_real)`.


### Paso 9. `reservas`
`total_amount` es un dato derivable almacenado (P5), y la fecha incluye el desplazamiento abreviado (P7).

Por ende, se elimina `total_amount` y se normaliza la fecha igual que en el
paso 8. El total de una reserva pasa a obtenerse como `SUM(cupones.monto)`.

| Antes (`bookings`) | Después (`reservas`) |
|---|---|
| `('00000F', '2017-07-05 03:12:00+03', 265700)` | `('00000F', '2017-07-05 03:12:00+03:00')` |

>La suma de
>`bookings.total_amount` en toda la base (20.766.980.900) es idéntica a la
>suma de `ticket_flights.amount` (20.766.980.900). Es decir, no existe pérdida de información.


### Paso 10. `pasajes`

Se renombran las columnas y llaves foráneas; sin cambios de valor.
`passenger_id` se conserva como atributo y no se crea una tabla de
pasajeros por falta de información para la misma. Tampoco se declara `UNIQUE`, pues
un mismo pasajero puede comprar varios pasajes. En este caso, cada
identificador aparece una vez (366.733 distintos en 366.733 filas).

### Paso 11. `cupones`

`ticket_flights` repite la clase como texto y no declara llaves.

Por ende, se declara la llave compuesta `(numero_pasaje, vuelo_id)`, que
convierte la tabla en la entidad asociativa de la relación N:M entre pasajes y
vuelos (un pasaje cubre varios vuelos; y un vuelo se usa en muchos pasajes). La
clase pasa a `clase_id` y se exige que `monto > 0`.

| Antes (`ticket_flights`) | Después (`cupones`) |
|---|---|
| `('0005432159776', 30625, 'Business', 42100)` | `('0005432159776', 30625, 3, 42100.0)` |

Distribución por clase: Economy (920.793), Comfort (17.291), Business (107.642).

### Paso 12. `tarjetas_embarque`

Se establece que cada tarjeta debe corresponder a un cupón ya existente,
mediante una llave foránea compuesta hacia `cupones`; y se impide que en un
mismo vuelo se repitan el número de embarque o el asiento.

```sql
UNIQUE (vuelo_id, numero_embarque),
UNIQUE (vuelo_id, asiento)
```

### Paso 13. Vista `v_vuelo`

Reúne el vuelo con los datos de su ruta y su estado, de modo que las consultas
habituales no repitan las uniones.

### 3.1 Correspondencia de nombres

| Fuente | Modelo normalizado |
|---|---|
| `airports_data` / `airport_code` | `aeropuertos` / `codigo` |
| `aircrafts_data` / `aircraft_code`, `range` | `aeronaves` / `codigo`, `autonomia_km` |
| `flights` / `flight_id`, `flight_no` | `vuelos` / `vuelo_id`, `numero_vuelo` |
| `scheduled_departure`, `scheduled_arrival` | `salida_programada`, `llegada_programada` |
| `actual_departure`, `actual_arrival` | `salida_real`, `llegada_real` |
| `seats` / `seat_no` | `asientos` / `numero` |
| `bookings` / `book_ref`, `book_date` | `reservas` / `localizador`, `fecha_reserva` |
| `tickets` / `ticket_no`, `passenger_id` | `pasajes` / `numero_pasaje`, `pasajero_id` |
| `ticket_flights` / `amount` | `cupones` / `monto` |
| `boarding_passes` / `boarding_no`, `seat_no` | `tarjetas_embarque` / `numero_embarque`, `asiento` |

---


## 5. Diccionario de datos

Descripción campo por campo de las doce tablas y de la vista. Los porcentajes
de nulos se midieron sobre el esquema normalizado una vez poblado.

### 5.1 `ciudades` — 101 filas

Grano: **una fila por ciudad con al menos un aeropuerto**.

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `ciudad_id` | INTEGER PK | **CONSTRUIDO** | Clave sustituta, en orden alfabético del nombre en inglés. | 0,00 % |
| `nombre` | TEXT UNIQUE | **DERIVADO** | Nombre en inglés, clave `"en"` del JSON `city`. | 0,00 % |
| `nombre_ru` | TEXT | **DERIVADO** | Nombre en ruso, clave `"ru"` del mismo JSON. | 0,00 % |
| `zona_horaria` | TEXT | **FUENTE** (`timezone`) | Horario IANA. | 0,00 % |

### 5.2 `aeropuertos` — 104 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `codigo` | TEXT PK | **FUENTE** (`airport_code`) | Código IATA de tres letras.| 0,00 % |
| `nombre` | TEXT | **DERIVADO** | Nombre en inglés, clave `"en"` de `airport_name`. | 0,00 % |
| `nombre_ru` | TEXT | **DERIVADO** | Nombre en ruso, clave `"ru"`. | 0,00 % |
| `ciudad_id` | INTEGER FK | **DERIVADO** | Ciudad donde se ubica, resuelta por el nombre en inglés. | 0,00 % |
| `longitud` | REAL | **DERIVADO** | Primer componente de `coordinates`. Rango de −180 a 180. | 0,00 % |
| `latitud` | REAL | **DERIVADO** | Segundo componente de `coordinates`. Rango de −90 a 90. | 0,00 % |

### 5.3 `aeronaves` — 9 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `codigo` | TEXT PK | **FUENTE** (`aircraft_code`) | Código del modelo. | 0,00 % |
| `modelo` | TEXT | **DERIVADO** | Nombre comercial. | 0,00 % |
| `modelo_ru` | TEXT | **DERIVADO** | Nombre comercial en ruso, clave `"ru"`. | 0,00 % |
| `autonomia_km` | INTEGER | **FUENTE** (`range`) | Alcance máximo declarado, en km (`CHECK > 0`). | 0,00 % |


### 5.4 `clases_tarifarias`— 3 filas

| Campo | Tipo | Procedencia | Descripción |
|---|---|---|---|
| `clase_id` | INTEGER PK | **CONSTRUIDO** | Identificador de la clase. |
| `codigo` | TEXT UNIQUE | **FUENTE** (`fare_conditions`) | Valor literal original. |
| `nombre` | TEXT | **CONSTRUIDO** | Nombre en español. |
| `orden` | INTEGER UNIQUE | **CONSTRUIDO** | Jerarquía de la cabina, de menor a mayor. |



### 5.5 `estados_vuelo` — 6 filas

| Campo | Tipo | Procedencia | Descripción |
|---|---|---|---|
| `estado_id` | INTEGER PK | **CONSTRUIDO** | Identificador del catálogo. |
| `codigo` | TEXT UNIQUE | **FUENTE** (`status`) | Valor original. |
| `descripcion` | TEXT | **CONSTRUIDO** | Explicación en español del estado. |


### 5.6 `asientos` — 1.339 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `aeronave_codigo` | TEXT PK/FK | **FUENTE** (`aircraft_code`) | Modelo al que pertenece (→ `aeronaves`). | 0,00 % |
| `numero` | TEXT PK | **FUENTE** (`seat_no`) | Identificador del asiento. | 0,00 % |
| `clase_id` | INTEGER FK | **DERIVADO** | Clase del asiento (→ `clases_tarifarias`), resuelta desde `fare_conditions`. | 0,00 % |

### 5.7 `rutas` — 710 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `numero_vuelo` | TEXT PK | **FUENTE** (`flight_no`) | Designador comercial. | 0,00 % |
| `origen` | TEXT FK | **FUENTE** (`departure_airport`) | Aeropuerto de salida (→ `aeropuertos`). | 0,00 % |
| `destino` | TEXT FK | **FUENTE** (`arrival_airport`) | Aeropuerto de llegada, necesariamente distinto del de origen. | 0,00 % |
| `aeronave_codigo` | TEXT FK | **FUENTE** (`aircraft_code`) | Modelo que opera la ruta (→ `aeronaves`). | 0,00 % |
| `duracion_min` | INTEGER | **DERIVADO** | Duración programada en minutos, a partir de las marcas programadas. Rango calculado entre 25 y 530. | 0,00 % |

### 5.8 `vuelos` — 33.121 filas


| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `vuelo_id` | INTEGER PK | **FUENTE** (`flight_id`) | Identificador único del vuelo. | 0,00 % |
| `numero_vuelo` | TEXT FK | **FUENTE** (`flight_no`) | Ruta a la que pertenece (→ `rutas`). | 0,00 % |
| `estado_id` | INTEGER FK | **DERIVADO** | Estado del vuelo (→ `estados_vuelo`), resuelto desde `status`. | 0,00 % |
| `salida_programada` | TEXT | **DERIVADO** | `AAAA-MM-DD HH:MM:SS+03:00`. | 0,00 % |
| `llegada_programada` | TEXT | **DERIVADO** | `AAAA-MM-DD HH:MM:SS`, sin desplazamiento. | 0,00 % |
| `salida_real` | TEXT | **DERIVADO** | Hora efectiva de despegue, se designa nula si el vuelo no se operó. | **49,36 %** |
| `llegada_real` | TEXT | **DERIVADO** | Hora real de aterrizaje. | **49,53 %** |



### 5.9 `reservas` — 262.788 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `localizador` | TEXT PK | **FUENTE** (`book_ref`) | Código de reserva (seis caracteres). | 0,00 % |
| `fecha_reserva` | TEXT | **DERIVADO** | Fecha y hora de la reserva en `AAAA-MM-DD HH:MM:SS+03:00`. | 0,00 % |

### 5.10 `pasajes` — 366.733 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `numero_pasaje` | TEXT PK | **FUENTE** (`ticket_no`) | Número de pasaje (13 caracteres). | 0,00 % |
| `localizador` | TEXT FK | **FUENTE** (`book_ref`) | Reserva a la que pertenece (→ `reservas`). | 0,00 % |
| `pasajero_id` | TEXT | **FUENTE** (`passenger_id`) | Identificador del pasajero. | 0,00 % |

### 5.11 `cupones` — 1.045.726 filas


| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `numero_pasaje` | TEXT PK/FK | **FUENTE** (`ticket_no`) | Pasaje (→ `pasajes`). | 0,00 % |
| `vuelo_id` | INTEGER PK/FK | **FUENTE** (`flight_id`) | Vuelo cubierto (→ `vuelos`). | 0,00 % |
| `clase_id` | INTEGER FK | **DERIVADO** | Clase pagada (→ `clases_tarifarias`), resuelta desde `fare_conditions`. | 0,00 % |
| `monto` | REAL | **FUENTE** (`amount`) | Importe del segmento (`CHECK > 0`). | 0,00 % |

### 5.12 `tarjetas_embarque` — 579.686 filas

| Campo | Tipo | Procedencia | Descripción | Nulos |
|---|---|---|---|---:|
| `numero_pasaje` | TEXT PK/FK | **FUENTE** (`ticket_no`) | Pasaje. Con `vuelo_id` construye la FK compuesta a `cupones`. | 0,00 % |
| `vuelo_id` | INTEGER PK/FK | **FUENTE** (`flight_id`) | Vuelo. | 0,00 % |
| `numero_embarque` | INTEGER | **FUENTE** (`boarding_no`) | Orden de embarque dentro del vuelo (`CHECK > 0`, `UNIQUE` con `vuelo_id`). | 0,00 % |
| `asiento` | TEXT | **FUENTE** (`seat_no`) | Asiento asignado (`UNIQUE` con `vuelo_id`). | 0,00 % 

Se tiene que hay menos tarjetas
(579.686) que cupones (1.045.726). Por ende, no todo cupón tiene tarjeta.

### 5.13 Vista `v_vuelo`

| Campo | Procedencia | Descripción |
|---|---|---|
| `vuelo_id`, `numero_vuelo` | `vuelos` | Identificación del vuelo. |
| `origen`, `destino`, `aeronave_codigo` | `rutas` | Datos de la ruta. |
| `estado` | `estados_vuelo.codigo` | Estado en texto. |
| `salida_programada` | `vuelos` | Tal como está almacenada. |
| `llegada_programada` | **DERIVADO** | `salida_programada + rutas.duracion_min`, con desplazamiento `+03:00`. |
| `salida_real`, `llegada_real` | `vuelos` | Horas efectivas, pueden ser `NULL`. |

---

---