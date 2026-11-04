# Documentación de Denormalización y Diccionario de Datos

Documentación del proceso de denormalización para el análisis de puntualidad de vuelos y descripción campo por campo del modelo resultante. Se presenta primero la información de entrada, después las transformaciones y finalmente el diccionario de dimensiones, hechos, tabla consolidada y vistas.

La estructura se documenta a partir de `Denormalizacion_final.sql`, versión reformateada del 30 de octubre de 2026. Los tipos, restricciones, conteos y porcentajes de nulos se contrastaron con `Base_de_datos/vuelos_final.duckdb` del repositorio. La verificación corresponde al 2 de noviembre de 2026.

## Archivos y alcance

| Archivo | Contenido |
|---|---|
| `Denormalizacion_final.sql` | Crea y carga 7 dimensiones, 2 tablas de hechos, 1 tabla consolidada y 5 vistas analíticas; usa tablas normalizadas y lim_vuelos ya existentes. |
| `Base_de_datos/vuelos_final.duckdb` | Base final consultada: contiene el modelo normalizado, la selección limpia y los objetos de denormalización. |
| `denormalizacion_vuelos.duckdb` | Archivo separado del repositorio con las 7 dimensiones y las 2 tablas de hechos; no contiene la tabla consolidada ni las vistas de la base final. |

Este documento describe exclusivamente la denormalización y las entradas necesarias para entenderla. Los diez objetos físicos creados son siete dimensiones, dos hechos y una tabla ancha. Las cinco vistas no se cuentan como tablas físicas. `_demora_final` es auxiliar temporal y se elimina antes de terminar la transacción.

## Convención de procedencia

| Etiqueta | Significado en esta etapa |
|---|---|
| **FUENTE** | Campo copiado de una tabla o vista de entrada de la transformación descrita. Puede haber sido calculado en una etapa anterior; se indica su origen inmediato. |
| **DERIVADO** | Campo calculado, convertido de tipo o resuelto mediante una unión durante la transformación descrita. |
| **CONSTRUIDO** | Clave sustituta, calendario, etiqueta o catálogo definido por el script. |

`PK` = clave primaria; `FK` = clave foránea declarada; `UNIQUE` = unicidad; `NN` = NOT NULL. Una relación lógica identificada en la descripción no implica que exista una FK física. La columna «Admite NULL» describe el esquema; «Nulos medidos» describe los datos cargados.

## 1. Datos de entrada

| Objeto de entrada | Uso |
|---|---|
| `vuelos` | Identificador, número de vuelo, programación, estado y marcas reales de los 33.121 vuelos. |
| `rutas` | Origen, destino, modelo de aeronave y duración programada; 710 designadores comerciales. |
| `aeropuertos`, `ciudades` | Código, nombre, ciudad, zona horaria y coordenadas de 104 aeropuertos. |
| `aeronaves`, `asientos` | Características y capacidad de 9 modelos de aeronave. |
| `estados_vuelo` | Código original del estado para resolver su equivalente dimensional. |
| `v_vuelo` | Vista normalizada que reúne vuelos, rutas y estados. Reconstruye llegada_programada a partir de salida_programada + duración de la ruta, con referencia +03:00. |
| `lim_vuelos` | Selección previa de 16.707 vuelos Arrived; incluye retrasos, salida local, franjas e indicadores de puntualidad. |

El calendario de programación completa va del **16 de julio al 14 de septiembre de 2017**: 61 días. La selección limpia utilizada para los resultados abarca del **16 de julio al 15 de agosto de 2017**, según `fecha_salida_local`. Son ámbitos distintos y no deben presentarse como un mismo período.

## 2. Necesidades que resuelve la denormalización

| Necesidad | Solución implementada |
|---|---|
| Repetir uniones para obtener ciudad, coordenadas, ruta o modelo. | Agrupar atributos descriptivos en dimensiones y reunirlos en vuelos_denormalizados. |
| Analizar por día, hora y bloque horario. | Crear dim_tiempo y dim_franja; usar fecha y hora locales en las vistas limpias. |
| Disponer de medidas numéricas de puntualidad. | Calcular demora de salida, demora de llegada, minutos recuperados y duración real en hechos_demoras. |
| Separar programación total y selección apta para resultados. | Conservar hechos_vuelos completo y obtener la capa limpia mediante unión con lim_vuelos. |
| Facilitar el consumo por Power BI y Streamlit. | Materializar una tabla por vuelo con descripciones, medidas e indicadores, y exponerla mediante v_powerbi. |

Se introduce redundancia deliberada: por ejemplo, `dim_aeropuerto` incorpora el nombre de la ciudad y la tabla consolidada repite descripciones por vuelo. El modelo dimensional conserva claves y relaciones; la tabla ancha permite consultar resultados sin repetir esas uniones.

## 3. Proceso de denormalización paso a paso

### Paso 1. Preparación transaccional

Se inicia BEGIN TRANSACTION y se eliminan los objetos analíticos enumerados, primero las vistas y después las tablas dependientes. No se recrean aquí las tablas normalizadas ni lim_vuelos.

### Paso 2. Cálculo auxiliar de minutos

Se crea _demora_final desde v_vuelo, filtrando solo salida_real IS NOT NULL. date_diff calcula salida real − programada, llegada real − programada y llegada real − salida real, con conversión a TIMESTAMPTZ y BIGINT.

### Paso 3. Calendario: dim_tiempo

generate_series construye todos los días entre la mínima y la máxima fecha de salida programada de vuelos. Se obtienen año, mes, día, semana ISO, fin de semana y existencia de salidas reales. Las etiquetas españolas se asignan en el script.

### Paso 4. Horas: dim_franja

range(24) genera las 24 horas. CASE asigna bloque y orden. La dimensión conserva el literal Manana, mientras lim_vuelos usa Dia para las horas 06–11.

### Paso 5. Aeropuertos: dim_aeropuerto

Se unen aeropuertos y ciudades. row_number asigna la clave; se cuentan todas las salidas programadas y se calcula su suma acumulada con funciones de ventana para clasificar el tráfico.

### Paso 6. Rutas: dim_ruta

Se toma una fila por numero_vuelo de rutas, se construye la etiqueta origen - destino y se conserva la duración programada. No se agrupa exclusivamente por el par de aeropuertos.

### Paso 7. Aeronaves: dim_aeronave

Se unen aeronaves y asientos, se cuenta la capacidad por modelo y se asigna una clave sustituta por código. El INNER JOIN requiere que el modelo tenga asientos asociados.

### Paso 8. Estados: dim_estado

INSERT VALUES define seis estados. Su clave se resuelve por codigo al cargar los hechos, porque el orden de IDs difiere del catálogo normalizado.

### Paso 9. Rangos: dim_regimen

Se construyen tres rangos empíricos para la demora de salida: 0; 1–11; 124–277 minutos. Son los rangos definidos por este script para el conjunto observado.

### Paso 10. Programación: hechos_vuelos

Se cargan todos los vuelos con sus claves dimensionales, duración programada y es_operado calculado como salida_real IS NOT NULL. Fecha y hora se extraen del texto original +03:00.

### Paso 11. Validación y carga: hechos_demoras

Antes del INSERT se comprueba que toda demora de salida auxiliar encuentre un rango. Si no lo encuentra, error() interrumpe el proceso. Se cargan las medidas y se calculan minutos recuperados como demora_salida − demora_llegada.

### Paso 12. Selección limpia de hechos

v_hechos_vuelos_limpios y v_hechos_demoras_limpias conservan solo IDs presentes en lim_vuelos. En la primera vista se reemplazan fecha_id y franja_id por fecha y hora locales del aeropuerto de origen.

### Paso 13. Integración descriptiva

v_analisis_vuelos_limpios une lim_vuelos, las vistas de hechos y las dimensiones para incorporar nombres, ciudades, zonas horarias, modelo, ruta, régimen y medidas. Usa INNER JOIN.

### Paso 14. Conversión para consumo

v_powerbi_vuelos_limpios convierte las cinco marcas de fecha y hora a TIMESTAMP_US. Las otras columnas se conservan.

### Paso 15. Materialización y cierre

Se crea vuelos_denormalizados con 44 columnas y PK(vuelo_id), y se carga desde la vista anterior. v_powerbi expone la tabla. Se elimina _demora_final y se ejecuta COMMIT.

### Paso 16. Controles posteriores

Se consultan conteos, unicidad de vuelo_id, fechas extremas y coherencia entre las medidas y las marcas de tiempo.

### 3.1 Fórmulas de las medidas

```sql
-- Entradas de v_vuelo, con desplazamiento explícito.
date_diff('minute', CAST(salida_programada AS TIMESTAMPTZ),
                    CAST(salida_real AS TIMESTAMPTZ)) AS demora_salida_min

date_diff('minute', CAST(llegada_programada AS TIMESTAMPTZ),
                    CAST(llegada_real AS TIMESTAMPTZ)) AS demora_llegada_min

date_diff('minute', CAST(salida_real AS TIMESTAMPTZ),
                    CAST(llegada_real AS TIMESTAMPTZ)) AS duracion_real_min

-- Tras calcular ambas demoras:
demora_salida_min - demora_llegada_min AS minutos_recuperados
```

Las diferencias se expresan en minutos enteros. Si falta llegada_real, las medidas que la necesitan permanecen NULL; no se sustituyen por cero. Un valor negativo en demora de llegada significa anticipación.

### 3.2 Clasificación de aeropuertos

Se ordenan las salidas por cantidad descendente y código ascendente para resolver empates. Se usa la suma acumulada **incluyendo el aeropuerto actual**: hasta 50 % del total corresponde a Principal; sobre 50 % y hasta 80 %, a Intermedio; sobre 80 %, a Secundario. Si un aeropuerto hace superar el umbral, queda en la siguiente banda. No se trata de porcentajes de aeropuertos ni se recalcula con la selección limpia.

### 3.3 Catálogos definidos

| estado_id | codigo | descripcion | es_operado |
|---|---|---|---|
| 1 | Arrived | Llegado | 1 |
| 2 | Cancelled | Cancelado | 0 |
| 3 | Delayed | Retrasado | 0 |
| 4 | Departed | En vuelo | 1 |
| 5 | On Time | A tiempo | 0 |
| 6 | Scheduled | Programado | 0 |

| regimen_id | etiqueta | desde_min | hasta_min | orden |
|---|---|---|---|---|
| 1 | Puntual | 0 | 0 | 1 |
| 2 | Demora breve | 1 | 11 | 2 |
| 3 | Demora prolongada | 124 | 277 | 3 |

`dim_regimen` clasifica **demoras de salida**. No incluye valores negativos, 12–123 ni mayores de 277. La ausencia de esos intervalos es una propiedad del catálogo implementado; si otra base los incorpora, debe ampliarse antes de cargarla. La validación del script detecta valores sin cobertura. Estos rangos no son una norma externa y no equivalen al indicador `> 15` minutos.

### 3.4 Correspondencia entre entradas y resultados

| Entrada | Objeto o campo resultante |
|---|---|
| `vuelos.salida_programada` | dim_tiempo y claves de fecha/hora de hechos_vuelos, con referencia +03:00. |
| `aeropuertos` + `ciudades` | dim_aeropuerto: incorpora ciudad, zona y coordenadas. |
| `rutas` | dim_ruta; claves de origen, destino y modelo en hechos_vuelos. |
| `aeronaves` + `asientos` | dim_aeronave con capacidad calculada. |
| `estados_vuelo.codigo` | dim_estado y hechos_vuelos.estado_id, resueltos por código. |
| `v_vuelo` y sus marcas temporales | _demora_final → hechos_demoras. |
| `lim_vuelos.salida_prog_local` | Fecha/hora local en v_hechos_vuelos_limpios y vuelos_denormalizados. |
| `lim_vuelos.retraso_salida_min`, `retraso_llegada_min` | Se conservan con esos nombres en vuelos_denormalizados; hechos_demoras usa demora_salida_min y demora_llegada_min. |
| `v_powerbi_vuelos_limpios` | Carga física de vuelos_denormalizados; v_powerbi expone la tabla. |

## 4. Inventario y alcance de los objetos

| Objeto | Tipo | Filas verificadas | Grano / función |
|---|---|---|---|
| `dim_tiempo` | Dimensión | 61 | un día del calendario de programación completo |
| `dim_franja` | Dimensión | 24 | una hora del día |
| `dim_aeropuerto` | Dimensión | 104 | un aeropuerto |
| `dim_ruta` | Dimensión | 710 | un designador comercial de vuelo (numero_vuelo) |
| `dim_aeronave` | Dimensión | 9 | un modelo de aeronave |
| `dim_estado` | Dimensión | 6 | un estado de vuelo |
| `dim_regimen` | Dimensión | 3 | un rango empírico de demora de salida |
| `hechos_vuelos` | Hechos | 33.121 | un vuelo programado identificado por vuelo_id |
| `hechos_demoras` | Hechos | 16.773 | un vuelo con salida_real no nula y demora de salida cubierta por dim_regimen |
| `vuelos_denormalizados` | Tabla consolidada | 16.707 | un vuelo de lim_vuelos con coincidencia en todas las uniones requeridas |

| Vista | Filas verificadas | Condición |
|---|---|---|
| `v_hechos_vuelos_limpios` | 16.707 | Creada por el script de denormalización. |
| `v_hechos_demoras_limpias` | 16.707 | Creada por el script de denormalización. |
| `v_analisis_vuelos_limpios` | 16.707 | Creada por el script de denormalización. |
| `v_powerbi_vuelos_limpios` | 16.707 | Creada por el script de denormalización. |
| `v_powerbi` | 16.707 | Creada por el script de denormalización. |
| `v_vuelo` | 33.121 | Entrada normalizada preexistente; no creada por este script. |

El script crea **5 vistas**: `v_hechos_vuelos_limpios`, `v_hechos_demoras_limpias`, `v_analisis_vuelos_limpios`, `v_powerbi_vuelos_limpios`, `v_powerbi`. `v_vuelo` es una entrada preexistente.

### 4.1 Por qué cambian los conteos

`hechos_vuelos` conserva los **33.121 vuelos programados**. `hechos_demoras` contiene **16.773 registros** porque su condición de entrada es tener salida_real, sin exigir estado Arrived. En la base inspeccionada son 16.707 Arrived, 58 Departed y 8 Cancelled que conservan marcas reales. Por ello, el indicador es_operado calculado en hechos_vuelos puede diferir del definido en dim_estado.

La selección limpia contiene **16.707 vuelos Arrived**. Sus uniones producen los mismos 16.707 IDs en la tabla final. Los 58 Departed carecen de llegada real y explican los NULL de llegada, recuperación y duración en hechos_demoras. Los 8 Cancelled con marcas reales tampoco se incorporan a la selección limpia. No debe interpretarse todo registro con salida real como un vuelo completado.

## 5. Diccionario de datos

Los porcentajes se midieron sobre cada objeto de `vuelos_final.duckdb`, después de la carga. El origen se refiere a la etapa documentada, no necesariamente al dato bruto de travel.sqlite.

### 5.1 `dim_tiempo` — 61 filas

Grano: **un día del calendario de programación completo**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `fecha_id` | BIGINT · PK, CHECK | No | **DERIVADO** | Fecha codificada como AAAAMMDD mediante strftime; identifica cada día. | 0,00 % |
| `fecha` | DATE · UNIQUE, CHECK | No | **CONSTRUIDO** | Día del calendario generado entre la mínima y la máxima salida programada de vuelos. | 0,00 % |
| `anio` | BIGINT | No | **DERIVADO** | Año de fecha, mediante year(fecha). | 0,00 % |
| `mes` | BIGINT | No | **DERIVADO** | Mes de fecha, de 1 a 12. | 0,00 % |
| `nombre_mes` | VARCHAR | No | **CONSTRUIDO** | Nombre español asignado al mes: Enero a Diciembre. | 0,00 % |
| `dia` | BIGINT | No | **DERIVADO** | Día del mes de fecha. | 0,00 % |
| `dia_semana` | BIGINT · CHECK | No | **DERIVADO** | Día ISO: 1 = lunes y 7 = domingo; isodow(fecha). | 0,00 % |
| `nombre_dia` | VARCHAR | No | **CONSTRUIDO** | Nombre español del día; el código conserva Miercoles y Sabado sin tilde. | 0,00 % |
| `semana_iso` | BIGINT | No | **DERIVADO** | Número de semana ISO mediante week(fecha); no es un identificador único entre años. | 0,00 % |
| `es_fin_de_semana` | BIGINT · CHECK | No | **DERIVADO** | 1 si isodow(fecha) es 6 o 7; 0 en otro caso. | 0,00 % |
| `hay_operados` | BIGINT · CHECK | No | **DERIVADO** | 1 si existe al menos un registro en vuelos con esa fecha programada y salida_real no nula; 0 en otro caso. No se filtra por estado Arrived. | 0,00 % |

Restricciones de dominio declaradas: `CHECK((fecha_id = CAST(strftime(fecha, '%Y%m%d') AS INTEGER)))`; `CHECK((dia_semana BETWEEN 1 AND 7))`; `CHECK((es_fin_de_semana IN (0, 1)))`; `CHECK((hay_operados IN (0, 1)))`.

### 5.2 `dim_franja` — 24 filas

Grano: **una hora del día**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `franja_id` | BIGINT · PK, CHECK | No | **CONSTRUIDO** | Hora entera de 0 a 23, generada con range(24). | 0,00 % |
| `hora` | VARCHAR · UNIQUE | No | **DERIVADO** | Etiqueta HH:00, mediante printf; por ejemplo 09:00. | 0,00 % |
| `bloque` | VARCHAR | No | **CONSTRUIDO** | Madrugada (00–05), Manana (06–11), Tarde (12–17) o Noche (18–23), según el literal del SQL. | 0,00 % |
| `orden` | BIGINT | No | **CONSTRUIDO** | Orden del bloque: Madrugada = 1, Manana = 2, Tarde = 3, Noche = 4. | 0,00 % |

Restricciones de dominio declaradas: `CHECK((franja_id BETWEEN 0 AND 23))`.

### 5.3 `dim_aeropuerto` — 104 filas

Grano: **un aeropuerto**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `aeropuerto_id` | BIGINT · PK | No | **CONSTRUIDO** | Clave sustituta con row_number() por código de aeropuerto en orden ascendente. | 0,00 % |
| `codigo` | VARCHAR · UNIQUE | No | **FUENTE** | aeropuertos.codigo: código IATA del aeropuerto. | 0,00 % |
| `nombre` | VARCHAR | No | **FUENTE** | aeropuertos.nombre. | 0,00 % |
| `ciudad` | VARCHAR | No | **FUENTE** | ciudades.nombre, incorporado mediante ciudad_id. | 0,00 % |
| `zona_horaria` | VARCHAR | No | **FUENTE** | ciudades.zona_horaria: identificador IANA. | 0,00 % |
| `longitud` | DOUBLE | No | **FUENTE** | aeropuertos.longitud, en grados. | 0,00 % |
| `latitud` | DOUBLE | No | **FUENTE** | aeropuertos.latitud, en grados. | 0,00 % |
| `vuelos_salida` | BIGINT | No | **DERIVADO** | COUNT(*) de todos los vuelos programados cuyo origen es ese aeropuerto; 0 si no tiene salidas. No usa solo lim_vuelos. | 0,00 % |
| `banda_trafico` | VARCHAR | No | **DERIVADO** | Clasificación por participación acumulada de las salidas: Principal hasta 50 %, Intermedio hasta 80 %, Secundario para el resto; Sin salidas si no hay registros. | 0,00 % |
| `orden_banda` | BIGINT | No | **DERIVADO** | 1 = Principal; 2 = Intermedio; 3 = Secundario; 4 = Sin salidas. | 0,00 % |

### 5.4 `dim_ruta` — 710 filas

Grano: **un designador comercial de vuelo (numero_vuelo)**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `ruta_id` | BIGINT · PK | No | **CONSTRUIDO** | Clave sustituta con row_number() ordenado por numero_vuelo. | 0,00 % |
| `numero_vuelo` | VARCHAR · UNIQUE | No | **FUENTE** | rutas.numero_vuelo: designador comercial; el grano se define por este valor. | 0,00 % |
| `etiqueta` | VARCHAR | No | **DERIVADO** | rutas.origen \|\| ' - ' \|\| rutas.destino; por ejemplo DME - LED. Varias filas pueden compartir el par origen–destino. | 0,00 % |
| `duracion_programada_min` | BIGINT | No | **FUENTE** | rutas.duracion_min: duración programada en minutos, ya calculada en la etapa anterior. | 0,00 % |

### 5.5 `dim_aeronave` — 9 filas

Grano: **un modelo de aeronave**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `aeronave_id` | BIGINT · PK | No | **CONSTRUIDO** | Clave sustituta con row_number() por aeronaves.codigo. | 0,00 % |
| `codigo` | VARCHAR · UNIQUE | No | **FUENTE** | aeronaves.codigo: código del modelo; no identifica una matrícula individual. | 0,00 % |
| `modelo` | VARCHAR | No | **FUENTE** | aeronaves.modelo. | 0,00 % |
| `autonomia_km` | BIGINT | No | **FUENTE** | aeronaves.autonomia_km: alcance declarado en kilómetros. | 0,00 % |
| `asientos_total` | BIGINT | No | **DERIVADO** | COUNT(asientos.numero) agrupado por el modelo. Capacidad del modelo, no cantidad de pasajeros transportados. | 0,00 % |

### 5.6 `dim_estado` — 6 filas

Grano: **un estado de vuelo**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `estado_id` | BIGINT · PK | No | **CONSTRUIDO** | Identificador definido en el catálogo dimensional; puede diferir del identificador normalizado. | 0,00 % |
| `codigo` | VARCHAR · UNIQUE | No | **FUENTE** | Literal del estado de vuelo, incorporado al catálogo con INSERT VALUES. | 0,00 % |
| `descripcion` | VARCHAR | No | **CONSTRUIDO** | Descripción española definida en el script. | 0,00 % |
| `es_operado` | BIGINT · CHECK | No | **CONSTRUIDO** | 1 para Arrived y Departed; 0 para los demás estados, según el catálogo. | 0,00 % |

Restricciones de dominio declaradas: `CHECK((es_operado IN (0, 1)))`.

### 5.7 `dim_regimen` — 3 filas

Grano: **un rango empírico de demora de salida**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `regimen_id` | BIGINT · PK | No | **CONSTRUIDO** | Identificador del rango de demora de salida. | 0,00 % |
| `etiqueta` | VARCHAR · UNIQUE | No | **CONSTRUIDO** | Puntual, Demora breve o Demora prolongada. | 0,00 % |
| `desde_min` | BIGINT · CHECK | No | **CONSTRUIDO** | Límite inferior inclusivo del rango, en minutos. | 0,00 % |
| `hasta_min` | BIGINT · CHECK | No | **CONSTRUIDO** | Límite superior inclusivo del rango, en minutos. | 0,00 % |
| `descripcion` | VARCHAR | No | **CONSTRUIDO** | Explicación del rango empírico definida por el script. | 0,00 % |
| `orden` | BIGINT | No | **CONSTRUIDO** | Orden de presentación: 1, 2 o 3. | 0,00 % |

Restricciones de dominio declaradas: `CHECK((desde_min <= hasta_min))`.

### 5.8 `hechos_vuelos` — 33.121 filas

Grano: **un vuelo programado identificado por vuelo_id**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `vuelo_id` | BIGINT · PK | No | **FUENTE** | vuelos.vuelo_id; identifica la ocurrencia individual del vuelo. | 0,00 % |
| `fecha_id` | BIGINT | No | **DERIVADO** | AAAAMMDD extraído de vuelos.salida_programada en su referencia +03:00; referencia dim_tiempo. | 0,00 % |
| `franja_id` | BIGINT | No | **DERIVADO** | Hora de 0 a 23 extraída de vuelos.salida_programada en +03:00; referencia dim_franja. | 0,00 % |
| `origen_id` | BIGINT | No | **DERIVADO** | Clave de dim_aeropuerto resuelta con rutas.origen. | 0,00 % |
| `destino_id` | BIGINT | No | **DERIVADO** | Clave de dim_aeropuerto resuelta con rutas.destino. | 0,00 % |
| `ruta_id` | BIGINT | No | **DERIVADO** | Clave de dim_ruta resuelta con numero_vuelo. | 0,00 % |
| `aeronave_id` | BIGINT | No | **DERIVADO** | Clave de dim_aeronave resuelta con rutas.aeronave_codigo. | 0,00 % |
| `estado_id` | BIGINT | No | **DERIVADO** | Clave de dim_estado resuelta por el código de estados_vuelo; no se copia directamente el ID normalizado. | 0,00 % |
| `numero_vuelo` | VARCHAR | No | **FUENTE** | vuelos.numero_vuelo; se conserva para facilitar consultas. | 0,00 % |
| `salida_programada` | VARCHAR | No | **FUENTE** | vuelos.salida_programada como texto con desplazamiento +03:00. | 0,00 % |
| `duracion_programada_min` | BIGINT | No | **FUENTE** | rutas.duracion_min; medida numérica en minutos. | 0,00 % |
| `es_operado` | BIGINT · CHECK | No | **DERIVADO** | CAST(vuelos.salida_real IS NOT NULL AS BIGINT). Permite sumar registros con salida real; no equivale necesariamente al indicador de dim_estado. | 0,00 % |

Restricciones de dominio declaradas: `CHECK((es_operado IN (0, 1)))`.

### 5.9 `hechos_demoras` — 16.773 filas

Grano: **un vuelo con salida_real no nula y demora de salida cubierta por dim_regimen**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `vuelo_id` | BIGINT · PK | No | **FUENTE** | Identificador de v_vuelo; referencia hechos_vuelos. | 0,00 % |
| `regimen_id` | BIGINT | No | **DERIVADO** | Clave resuelta por demora_salida_min BETWEEN desde_min AND hasta_min, ambos inclusivos. | 0,00 % |
| `demora_salida_min` | BIGINT | No | **DERIVADO** | date_diff en minutos entre salida_programada y salida_real, convertidas a TIMESTAMPTZ. | 0,00 % |
| `demora_llegada_min` | BIGINT | Sí | **DERIVADO** | date_diff en minutos entre llegada_programada y llegada_real, convertidas a TIMESTAMPTZ; puede ser negativo si hay llegada anticipada. | 0,35 % |
| `minutos_recuperados` | BIGINT | Sí | **DERIVADO** | demora_salida_min − demora_llegada_min. Positivo: reducción de demora; negativo: aumento. | 0,35 % |
| `duracion_real_min` | BIGINT | Sí | **DERIVADO** | date_diff en minutos entre salida_real y llegada_real, convertidas a TIMESTAMPTZ. | 0,35 % |

### 5.10 `vuelos_denormalizados` — 16.707 filas

Grano: **un vuelo de lim_vuelos con coincidencia en todas las uniones requeridas**.

| Campo | Tipo / restricción | Admite NULL | Procedencia | Descripción y regla | Nulos medidos |
|---|---|---|---|---|---|
| `vuelo_id` | BIGINT · PK | No | **FUENTE** | lim_vuelos.vuelo_id; una fila por vuelo de la selección limpia. | 0,00 % |
| `numero_vuelo` | VARCHAR | Sí | **FUENTE** | lim_vuelos.numero_vuelo. | 0,00 % |
| `origen` | VARCHAR | Sí | **FUENTE** | lim_vuelos.origen: código IATA de salida. | 0,00 % |
| `destino` | VARCHAR | Sí | **FUENTE** | lim_vuelos.destino: código IATA de llegada. | 0,00 % |
| `aeronave_codigo` | VARCHAR | Sí | **FUENTE** | lim_vuelos.aeronave_codigo: código del modelo. | 0,00 % |
| `salida_programada` | TIMESTAMP | Sí | **DERIVADO** | lim_vuelos.salida_programada convertido de texto a TIMESTAMP; hora de referencia +03:00 sin desplazamiento almacenado. | 0,00 % |
| `salida_real` | TIMESTAMP | Sí | **DERIVADO** | lim_vuelos.salida_real convertido a TIMESTAMP; misma referencia horaria que salida_programada. | 0,00 % |
| `llegada_programada` | TIMESTAMP | Sí | **DERIVADO** | lim_vuelos.llegada_programada convertido a TIMESTAMP; referencia +03:00, no hora local de destino. | 0,00 % |
| `llegada_real` | TIMESTAMP | Sí | **DERIVADO** | lim_vuelos.llegada_real convertido a TIMESTAMP; referencia +03:00, no hora local de destino. | 0,00 % |
| `retraso_salida_min` | BIGINT | Sí | **FUENTE** | lim_vuelos.retraso_salida_min, calculado previamente como salida_real − salida_programada en minutos; se conserva sin filtrar por >0 o >15. | 0,00 % |
| `retraso_llegada_min` | BIGINT | Sí | **FUENTE** | lim_vuelos.retraso_llegada_min, calculado previamente como llegada_real − llegada_programada; admite valores negativos. | 0,00 % |
| `salida_prog_local` | TIMESTAMP | Sí | **DERIVADO** | lim_vuelos.salida_prog_local convertido a TIMESTAMP; hora local del aeropuerto de origen, calculada en la limpieza. | 0,00 % |
| `hora_salida_local` | BIGINT | Sí | **FUENTE** | lim_vuelos.hora_salida_local: hora entera de 0 a 23 del aeropuerto de origen. | 0,00 % |
| `franja_horaria` | VARCHAR | Sí | **FUENTE** | Literal de lim_vuelos: 1. Madrugada (00-05), 2. Dia (06-11), 3. Tarde (12-17) o 4. Noche (18-23). | 0,00 % |
| `dia_semana_num` | BIGINT | Sí | **FUENTE** | lim_vuelos.dia_semana_num: 1 = lunes a 7 = domingo, según salida programada local. | 0,00 % |
| `dia_semana` | VARCHAR | Sí | **FUENTE** | lim_vuelos.dia_semana: nombre del día de la salida local. | 0,00 % |
| `salio_a_tiempo` | BIGINT | Sí | **FUENTE** | Indicador de lim_vuelos: 1 si retraso_salida_min <= 0; 0 en otro caso. | 0,00 % |
| `llego_a_tiempo` | BIGINT | Sí | **FUENTE** | Indicador de lim_vuelos: 1 si retraso_llegada_min <= 0; 0 en otro caso. | 0,00 % |
| `salio_a_tiempo_llego_tarde` | BIGINT | Sí | **FUENTE** | 1 si retraso_salida_min <= 0 y retraso_llegada_min > 0; 0 en otro caso, calculado en lim_vuelos. | 0,00 % |
| `demora_salida_15` | BIGINT | Sí | **FUENTE** | 1 si retraso_salida_min > 15; 0 en otro caso. Con exactamente 15 minutos vale 0. | 0,00 % |
| `demora_llegada_15` | BIGINT | Sí | **FUENTE** | 1 si retraso_llegada_min > 15; 0 en otro caso. | 0,00 % |
| `fecha_salida_local` | DATE | Sí | **DERIVADO** | CAST(salida_prog_local AS DATE). | 0,00 % |
| `fecha_id` | INTEGER | Sí | **DERIVADO** | Fecha local de salida en formato AAAAMMDD, convertida a INTEGER en v_hechos_vuelos_limpios. | 0,00 % |
| `franja_id` | INTEGER | Sí | **DERIVADO** | hora_salida_local convertida a INTEGER; identifica la hora local, no la hora +03:00 de hechos_vuelos. | 0,00 % |
| `origen_id` | BIGINT | Sí | **FUENTE** | v_hechos_vuelos_limpios.origen_id; relación lógica con dim_aeropuerto. | 0,00 % |
| `destino_id` | BIGINT | Sí | **FUENTE** | v_hechos_vuelos_limpios.destino_id; relación lógica con dim_aeropuerto. | 0,00 % |
| `ruta_id` | BIGINT | Sí | **FUENTE** | v_hechos_vuelos_limpios.ruta_id; relación lógica con dim_ruta. | 0,00 % |
| `aeronave_id` | BIGINT | Sí | **FUENTE** | v_hechos_vuelos_limpios.aeronave_id; relación lógica con dim_aeronave. | 0,00 % |
| `estado_id` | BIGINT | Sí | **FUENTE** | v_hechos_vuelos_limpios.estado_id; relación lógica con dim_estado. | 0,00 % |
| `aeropuerto_origen` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.nombre, usando origen_id. | 0,00 % |
| `ciudad_origen` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.ciudad, usando origen_id. | 0,00 % |
| `zona_horaria_origen` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.zona_horaria, usando origen_id. | 0,00 % |
| `aeropuerto_destino` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.nombre, usando destino_id. | 0,00 % |
| `ciudad_destino` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.ciudad, usando destino_id. | 0,00 % |
| `zona_horaria_destino` | VARCHAR | Sí | **FUENTE** | dim_aeropuerto.zona_horaria, usando destino_id. | 0,00 % |
| `modelo_aeronave` | VARCHAR | Sí | **FUENTE** | dim_aeronave.modelo. | 0,00 % |
| `asientos_total` | BIGINT | Sí | **FUENTE** | dim_aeronave.asientos_total; capacidad por modelo, repetida en cada vuelo. | 0,00 % |
| `ruta` | VARCHAR | Sí | **FUENTE** | dim_ruta.etiqueta: origen - destino. | 0,00 % |
| `duracion_programada_min` | BIGINT | Sí | **FUENTE** | hechos_vuelos.duracion_programada_min. | 0,00 % |
| `estado` | VARCHAR | Sí | **FUENTE** | dim_estado.codigo; la selección limpia corresponde a Arrived. | 0,00 % |
| `regimen_id` | BIGINT | Sí | **FUENTE** | hechos_demoras.regimen_id; relación lógica con dim_regimen. | 0,00 % |
| `regimen_salida` | VARCHAR | Sí | **FUENTE** | dim_regimen.etiqueta. | 0,00 % |
| `minutos_recuperados` | BIGINT | Sí | **FUENTE** | hechos_demoras.minutos_recuperados; medida calculada antes de consolidar la tabla. | 0,00 % |
| `duracion_real_min` | BIGINT | Sí | **FUENTE** | hechos_demoras.duracion_real_min, en minutos. | 0,00 % |

En esta tabla solo `vuelo_id` tiene PK y no admite NULL. Las otras 43 columnas admiten NULL en el DDL, aunque la carga inspeccionada no contiene ninguno. No hay claves foráneas ni CHECK declarados aquí: los IDs e indicadores conservan relaciones y reglas de sus entradas, pero no restricciones físicas en esta tabla.

### 5.11 Vistas de la capa limpia y de consumo

Las vistas no almacenan una copia física y no declaran PK/FK propias. Su grano observado es un vuelo por vuelo_id. Todas las vistas de esta sección tienen 16.707 filas y 0,00 % de nulos en todas sus columnas en la base verificada.

#### `v_hechos_vuelos_limpios` — 13 columnas

Hereda todas las columnas de hechos_vuelos (sección 5.8), conserva solo IDs de lim_vuelos y aplica estos cambios:

| Campo | Tipo | Procedencia | Regla |
|---|---|---|---|
| `fecha_id` | INTEGER | DERIVADO | Reemplaza la clave de fecha +03:00 por AAAAMMDD de lim_vuelos.salida_prog_local. |
| `franja_id` | INTEGER | DERIVADO | Reemplaza la hora +03:00 por CAST(lim_vuelos.hora_salida_local AS INTEGER). |
| `salida_prog_local` | VARCHAR | FUENTE | Campo adicional copiado de lim_vuelos; fecha y hora local del aeropuerto de origen. |

#### `v_hechos_demoras_limpias` — 6 columnas

Hereda sin cambios de nombre ni tipo los seis campos de hechos_demoras (sección 5.9). Filtra mediante INNER JOIN con lim_vuelos por vuelo_id.

#### `v_analisis_vuelos_limpios` — 44 columnas

Incluye las 21 columnas de lim_vuelos y agrega 23 campos: fecha local, claves dimensionales, descripciones y medidas. Los nombres y la descripción de sus 44 campos corresponden a la sección 5.10. Antes de la conversión posterior, las cinco marcas temporales tienen tipo VARCHAR; fecha_salida_local es DATE; fecha_id y franja_id son INTEGER; el resto coincide con los tipos indicados en 5.10.

#### `v_powerbi_vuelos_limpios` — 44 columnas

Conserva las 44 columnas de v_analisis_vuelos_limpios y convierte salida_programada, salida_prog_local, salida_real, llegada_programada y llegada_real a TIMESTAMP_US (alias de TIMESTAMP en esta base). Sus nombres, tipos y significados finales corresponden a la sección 5.10.

#### `v_powerbi` — 44 columnas

SELECT * de vuelos_denormalizados. Expone las mismas 44 columnas, con los mismos tipos, valores y significados de la sección 5.10.

### 5.12 Tabla temporal `_demora_final`

| Campo | Tipo | Procedencia | Regla |
|---|---|---|---|
| `vuelo_id` | BIGINT | FUENTE | Identificador de v_vuelo. |
| `dem_salida` | BIGINT | DERIVADO | Diferencia en minutos de salida real respecto de salida programada. |
| `dem_llegada` | BIGINT | DERIVADO | Diferencia en minutos de llegada real respecto de llegada programada; admite NULL. |
| `dur_real` | BIGINT | DERIVADO | Diferencia en minutos de llegada real respecto de salida real; admite NULL. |

Se crea con CREATE TEMP TABLE AS y no declara PK/FK. Su filtro es salida_real IS NOT NULL. Se utiliza para validar el régimen y cargar hechos_demoras, y después se elimina; no forma parte de las tablas persistentes.

## 6. Relaciones del modelo

| Origen | Campo | Destino físico o lógico | Tipo |
|---|---|---|---|
| hechos_vuelos | vuelo_id | vuelos.vuelo_id | FK física; una fila de hechos por vuelo. |
| hechos_vuelos | fecha_id | dim_tiempo.fecha_id | FK física; muchos vuelos por día. |
| hechos_vuelos | franja_id | dim_franja.franja_id | FK física; muchos vuelos por hora. |
| hechos_vuelos | origen_id y destino_id | dim_aeropuerto.aeropuerto_id | Dos FK físicas a una dimensión con roles distintos. |
| hechos_vuelos | ruta_id | dim_ruta.ruta_id | FK física. |
| hechos_vuelos | aeronave_id | dim_aeronave.aeronave_id | FK física. |
| hechos_vuelos | estado_id | dim_estado.estado_id | FK física. |
| hechos_demoras | vuelo_id | hechos_vuelos.vuelo_id | PK y FK; cero o una fila de demoras por vuelo programado. |
| hechos_demoras | regimen_id | dim_regimen.regimen_id | FK física. |
| vuelos_denormalizados | IDs dimensionales | Dimensiones correspondientes | Relaciones lógicas; la tabla ancha no declara FK. |

Las claves sustitutas generadas con row_number dependen del conjunto de códigos y su orden. Se deben regenerar las dimensiones y resolver los hechos juntos; los códigos de negocio se conservan para rastrear las correspondencias.

## 7. Criterios de interpretación

| Concepto | Regla documentada |
|---|---|
| Referencia temporal original | hechos_vuelos.fecha_id y franja_id se extraen del horario +03:00. Las vistas limpias sustituyen esas claves por la fecha y hora locales del origen. |
| TIMESTAMP y zona | Las columnas TIMESTAMP de la tabla final no almacenan zona. salida_prog_local es la salida local; las cuatro marcas programadas/reales restantes conservan la referencia horaria común de las entradas limpias. |
| Hora local del destino | No se calcula una llegada local de destino en este script. Disponer de zona_horaria_destino no convierte automáticamente llegada_real. |
| Cobertura temporal | Programación total: 16/07–14/09/2017. Tabla limpia: 16/07–15/08/2017 por fecha local de salida. |
| Vuelos con salida real | hechos_demoras se filtra por salida_real no nula; no por demora > 0, > 15 ni por estado Arrived. |
| Promedio entre vuelos con retraso | Para el criterio elegido de retraso positivo, filtrar retraso_salida_min > 0 antes de AVG. Incluye demoras de 1 a 15 minutos. |
| Promedio de todos los vuelos limpios | AVG(retraso_salida_min) incluye las salidas con cero minutos; mide el promedio sobre toda la selección limpia. |
| Retraso mayor de 15 minutos | demora_salida_15 y demora_llegada_15 usan > 15, estrictamente. Son indicadores diferentes del criterio > 0. |
| Régimen empírico | Puntual en dim_regimen significa exactamente 0 en salida; no significa <= 15. Su categoría de demora prolongada comienza en 124 en este conjunto. |
| Recuperación | minutos_recuperados > 0 significa menor demora al llegar que al salir; no implica necesariamente una llegada puntual. |
| Capacidad | asientos_total describe capacidad del modelo; sumarla por vuelos da asientos programados por operación, no pasajeros reales. |
| Catálogo de franjas | dim_franja.bloque usa Manana; vuelos_denormalizados.franja_horaria conserva la etiqueta Dia de lim_vuelos. Comparten intervalo 06–11, con nombres distintos. |

La carga conserva las medidas por vuelo y no fija un único denominador para todos los análisis. Cada KPI debe declarar población, campo y filtro para poder compararse entre Power BI y Streamlit.

## 8. Verificación de la carga

| Control | Resultado medido |
|---|---|
| Filas en hechos_vuelos | 33.121. |
| Filas en hechos_demoras | 16.773. |
| Filas en lim_vuelos y vuelos_denormalizados | 16.707 en cada una. |
| IDs distintos en vuelos_denormalizados | 16.707; sin duplicados de vuelo_id. |
| Período local de vuelos_denormalizados | 16/07/2017 a 15/08/2017. |
| Demoras sin cobertura en dim_regimen | 0. |
| Nulos en hechos_demoras.demora_llegada_min | 58; 0,35 %. |
| Nulos en hechos_demoras.minutos_recuperados | 58; 0,35 %. |
| Nulos en hechos_demoras.duracion_real_min | 58; 0,35 %. |
| Nulos en vuelos_denormalizados | 0 en sus 44 columnas. |
| Inconsistencias: retraso_salida_min frente a sus marcas | 0. |
| Inconsistencias: retraso_llegada_min frente a sus marcas | 0. |
| Inconsistencias: duracion_real_min frente a sus marcas | 0. |
| Inconsistencias: minutos_recuperados frente a salida − llegada | 0. |

### 8.1 Consultas reproducibles

```sql
-- Conteos de los ámbitos principales.
SELECT 'hechos_vuelos' AS objeto, COUNT(*) AS registros FROM hechos_vuelos
UNION ALL
SELECT 'hechos_demoras', COUNT(*) FROM hechos_demoras
UNION ALL
SELECT 'lim_vuelos', COUNT(*) FROM lim_vuelos
UNION ALL
SELECT 'vuelos_denormalizados', COUNT(*) FROM vuelos_denormalizados;

-- Unicidad y período de la tabla final.
SELECT
    COUNT(*) AS registros,
    COUNT(DISTINCT vuelo_id) AS vuelos_unicos,
    MIN(fecha_salida_local) AS primera_fecha_local,
    MAX(fecha_salida_local) AS ultima_fecha_local
FROM vuelos_denormalizados;

-- Nulos observados en medidas que dependen de llegada_real.
SELECT
    COUNT(*) AS total,
    COUNT(*) - COUNT(demora_llegada_min) AS nulos_demora_llegada,
    COUNT(*) - COUNT(minutos_recuperados) AS nulos_recuperados,
    COUNT(*) - COUNT(duracion_real_min) AS nulos_duracion
FROM hechos_demoras;

-- Cobertura del catálogo de regímenes.
SELECT COUNT(*) AS demoras_sin_regimen
FROM hechos_demoras d
LEFT JOIN dim_regimen g
    ON d.demora_salida_min BETWEEN g.desde_min AND g.hasta_min
WHERE g.regimen_id IS NULL;

-- Comparación que también detecta diferencias por NULL.
SELECT COUNT(*) AS inconsistencias
FROM vuelos_denormalizados
WHERE retraso_salida_min IS DISTINCT FROM
          date_diff('minute', salida_programada, salida_real)
   OR retraso_llegada_min IS DISTINCT FROM
          date_diff('minute', llegada_programada, llegada_real)
   OR duracion_real_min IS DISTINCT FROM
          date_diff('minute', salida_real, llegada_real)
   OR minutos_recuperados IS DISTINCT FROM
          retraso_salida_min - retraso_llegada_min;

-- Denominadores diferentes: no confundir estos promedios.
SELECT
    ROUND(AVG(retraso_salida_min), 2) AS promedio_todos_limpios,
    ROUND(AVG(retraso_salida_min)
          FILTER (WHERE retraso_salida_min > 0), 2) AS promedio_retraso_positivo
FROM vuelos_denormalizados;
```

La última consulta devuelve **12,20 minutos** sobre todos los vuelos limpios y **12,74 minutos** entre los de retraso de salida positivo. Es una diferencia de población, no un cambio en los minutos almacenados.

