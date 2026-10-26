# Análisis de Puntualidad de Vuelos ✈️

Análisis estadístico de los patrones de puntualidad y retraso en vuelos comerciales.

## Metodología

La puntualidad es la capacidad, el hábito y el valor de cumplir con las obligaciones, citas, tareas o horarios en el momento exacto que se ha acordado. Por su parte la Real Academia Española, lo define como “El cuidado y la diligencia en llegar a una hora convenida o en realizar una acción a su debido tiempo”. En las aerolíneas, la puntualidad impacta directamente en la eficiencia logística, la reducción de costos para las aerolíneas y la fluidez general del tránsito aéreo. La misma también define la credibilidad de la aerolínea ante el pasajero, siendo este un punto clave para obtener su confianza y convertirlo en un viajero frecuente.

La puntualidad, además, es un indicador de algo más profundo: confiabilidad. Cuando un pasajero reserva un vuelo, deposita su confianza en llegar a tiempo a su destino. Un retraso puede ser entendible; pero la reiteración de retrasos no lo es. Por ello, las compañías aéreas intentan mantener altos niveles de puntualidad para lograr construir una reputación sólida y generar lealtad entre sus pasajeros.

Bajo estos precedentes, el presente trabajo se propone evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017, mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales. El objetivo central es investigar, mediante técnicas de estadística descriptiva, cómo variables específicas, tales como la franja horaria de salida (scheduled_departure), el día de la semana, el aeropuerto de origen/destino y el tipo de aeronave (aircraft_code, model), influyen en la frecuencia y magnitud de los retrasos, medidos a partir de la desviación entre los horarios reales y programados.

---

## Planteamiento del Problema

​​A nivel mundial, la aviación comercial es la columna vertebral del transporte, donde la puntualidad es uno de los indicadores de desempeño más importantes para la logística, los costos de las aerolíneas y la fluidez del tránsito aéreo. A su vez, la red de aeropuertos de la Federación Rusa demanda una sincronización precisa para conectar múltiples zonas y, durante el período comprendido entre el 16 de julio y el 17 de agosto de 2017, este sistema aeroportuario gestionó un volumen alto de operaciones.

A pesar de la planificación de los itinerarios, se observan desviaciones constantes entre los horarios de salida y llegada programados frente a los horarios reales, lo que se traduce en una acumulación de retrasos que no se distribuye de manera correcta.

---

## Justificación

El estudio de la puntualidad en el transporte aéreo es relevante debido a que es indicador clave que afecta al tránsito aéreo, la rentabilidad de las aerolíneas y la eficiencia en todo el sistema de aviación. En la actualidad, los pasajeros están dispuestos a pagar más por volar con aerolíneas que tienen un mejor historial de puntualidad. Dichas aerolíneas suelen tener márgenes de ganancias operativas superiores. Cada punto de mejora se traduce en millones de dólares de ahorro, ya que se reducen los costos asociados a los retrasos (como compensaciones a pasajeros, combustible extra y horas de tripulación) y se optimiza el uso de los aviones.

Desde una perspectiva académica, resulta significativo analizar cómo diversos factores influyen en las salidas y llegadas de los vuelos, mediante el uso de herramientas de análisis estadístico y modelado de datos que permitan identificar patrones, tendencias y correlaciones entre variables asociadas. Al cruzar variables temporales (día, hora) y operacionales (tipo de aeronave, aeropuertos de origen/destino), la investigación no solo describe el fenómeno, sino que generará información accionable. Este tipo de análisis puede contribuir a identificar áreas de alta incidencia geográfica y franjas horarias críticas, así como a generar conclusiones sobre futuras estrategias de optimización de la puntualidad, reducción de costos y mejora de la experiencia del pasajero en el sector aeronáutico.

---

## Objetivo general

Evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017, mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales.

## Objetivos específicos

- Cuantificar la frecuencia y magnitud de los retrasos registrados en las salidas y llegadas de los vuelos, mediante la comparación entre los horarios programados y los horarios reales.

- Analizar la incidencia de los retrasos según el horario programado de salida, con el propósito de identificar las franjas horarias que presentan mayor frecuencia y magnitud de retrasos.

- Comparar el comportamiento de los retrasos entre los diferentes aeropuertos de origen y destino, a fin de identificar diferencias en el cumplimiento de los horarios programados.

- Comparar la frecuencia y magnitud de los retrasos según el tipo de aeronave asignada a los vuelos, con el propósito de identificar diferencias en el cumplimiento de los horarios programados.

- Examinar la variación de los retrasos según el día de la semana, con el propósito de identificar patrones temporales en el cumplimiento de los horarios programados.

---
## Universo y Unidad de Análisis
- Universo de programación: está conformado por todos los vuelos comerciales registrados en la base de datos Travel.sqlite, la cual está constituida por un total de 33.121 registros de vuelos.
  
- Universo de operación: el estudio se focaliza en la muestra de 16.707 vuelos que se iniciaron y finalizaron su ruta filtrados por el estado de Arrived. Y que cuentan con datos reales de despegue y aterrizaje (actual_departure y actual_arrival). Se excluyeron 8 registros cuyo estatus es "Cancelled", dado que no cuentan con horas reales de operación.  El periodo de referencia de este análisis se encuentra entre el 16 de julio y el 15 de agosto de 2017.
   
- Unidad de análisis: la unidad mínima de observación es cada vuelo en particular. Cada uno de estos registros es único e irrepetible, y puede ser rastreado de manera inequívoca a través de su identificador primario (flight_id) dentro de la base de datos.
  
- Técnicas: para el procesamiento de los datos, se emplearon diversas medidas descriptivas que permiten caracterizar el comportamiento de la muestra en estudio. Se utilizarán tablas de frecuencias absolutas y relativas para estudiar variables categóricas (como el día de la semana o los aeropuertos); medidas de resumen (media, mediana, desviación estándar) para cuantificar en minutos la magnitud de los retrasos; y segmentaciones agrupadas para contrastar el rendimiento operativo entre los distintos modelos de aeronaves y nodos de la red. 
---

## Limitaciones

- Limitación temporal: El análisis se restringe al período comprendido entre el xx de julio y el xx de agosto de 2017. Por lo tanto, los patrones y conclusiones obtenidos no son aplicables a otras épocas del año.

- ​Limitación espacial: El estudio se enfoca únicamente en los aeropuertos rusos contenidos en la base de datos, por lo que los resultados no pueden usarse para el comportamiento de la aviación en otras regiones.

- ​Limitación de datos: La muestra se reduce de manera exclusiva a los vuelos que completaron su itinerario con éxito (estado "Arrived", con un total de 16.707 registros). Esto implica que los vuelos que sufrieron cancelaciones definitivas o desvíos quedan excluidos del análisis comparativo.

- ​Variables no contempladas: El estudio se limita al procesamiento de las variables temporales y operacionales disponibles en la estructura de los datos (horarios programados y reales, aeropuertos, tipo de aeronave y días de la semana). Factores externos que explican a fondo la causa raíz de una demora, como condiciones meteorológicas severas, congestión temporal del espacio aéreo, huelgas o problemas de mantenimiento específicos, quedan fuera del alcance al no estar contemplados en los registros analizados.  

---

## Proceso de Normalizacion (3FN)

La normalización de la base de datos de aerolíneas se estructuró en torno a la Tercera Forma Normal (3FN) y la eliminación de dependencias transitivas, esto mediante la creación de catálogos independientes. Se aisló la tabla de ciudades, desplazando su nombre y zona horaria (que antes residían en la de aeropuerto), para evitar duplicaciones cuando una ciudad posee múltiples terminales; y se reemplazaron cadenas de texto repetitivas de tarifas y estados por IDs enteros en tablas de soporte.

Con respecto a los aspectos operativos y comerciales, el diseño aplicó una descomposición semántica, separando la plantilla fija del trayecto (rutas) de su ejecución física (vuelos). Asimismo, la integridad de compra y abordaje se estructuró vinculando reservas, pasajes, cupones y tarjetas de embarque a través de claves compuestas y relaciones de muchos a muchos, asegurando que cada pase de embarque corresponda a un cupón previamente adquirido y blindando el sistema con validaciones de restricciones (CHECK y UNIQUE) contra incoherencias y duplicidad de asientos.

---

## Estructura del repositorio

```
├── app.py                                     Tablero principal de investigacion
├── requirements.txt
├── .streamlit/config.toml                     Paleta de colores azul y blanco     
├──.config/settings.json                       Ruta de la base de datos 
│
├── Base de datos/
│   ├── base_datos.py                          Llamada a la base de datos 
│   ├── data_normal.sql                        Carga de Datos de la Normalizacion 
│   └── esquema_normal.sql                     Esquema de la Normalizacion 
│                         
├── src/
│   └── .gitkeep                               Para mantener la estructura de las carpetas      
│
└──  pages/
    ├── 01_Resumen.py                          Introduccion, Extructura del informe 
    ├── 02_Plantamiento del problema.py        Justificacion, Objetivos, Variables 
    ├── 03_Marco_Teorico.py                    Fundamentos 
    ├── 04_Marco Metodologico.py      
    ├── 05_Conclusion.py           
    ├── 06_Bibliografia.py          
    └── 07_Cuestionario SQL.py                          
```
