# analisis-puntualidad-vuelos
Análisis estadístico de los patrones de puntualidad y retraso en vuelos comerciales. 

# INTRODUCCIÓN 

La puntualidad es la capacidad, el hábito y el valor de cumplir con las obligaciones, citas, tareas o horarios en el momento exacto que se ha acordado. Según la Real Academia Española, es “El cuidado y la diligencia en llegar a una hora convenida o en realizar una acción a su debido tiempo”. En las aerolíneas, la puntualidad impacta directamente en la eficiencia logística, la reducción de costos para las aerolíneas y la fluidez general del tránsito aéreo. La misma también define la credibilidad de la aerolínea ante el pasajero, siendo este un punto clave para obtener su confianza y convertirlo en un viajero frecuente. 
La puntualidad, además, es un indicador de algo más profundo: confiabilidad. Cuando un pasajero reserva un vuelo, deposita su confianza en llegar a tiempo a su destino. Un retraso puede ser entendible; pero la reiteración de retrasos no lo es. Por ello, las compañías aéreas intentan mantener altos niveles de puntualidad para lograr construir una reputación sólida y generar lealtad entre sus pasajeros.
Bajo estos precedentes, el presente trabajo se propone evaluar el cumplimiento de los horarios programados de salida y llegada de los vuelos registrados en los aeropuertos rusos durante el período comprendido entre el 16 de julio y el 15 de agosto de 2017, mediante el análisis de los retrasos y su comportamiento según variables temporales y operacionales. El objetivo central es investigar, mediante técnicas de estadística descriptiva, cómo variables específicas, tales como la franja horaria de salida (scheduled_departure), el día de la semana, el aeropuerto de origen/destino y el tipo de aeronave (aircraft_code, model), influyen en la frecuencia y magnitud de los retrasos, medidos a partir de la desviación entre los horarios reales y programados.

---

# PLANTEAMIENTO DEL PROBLEMA

​A nivel mundial, la aviación comercial es la columna vertebral del transporte, donde la puntualidad es uno de los indicadores de desempeño más críticos para la logística, los costos de las aerolíneas y la fluidez del tránsito aéreo. A su vez, la red de aeropuertos de la Federación Rusa demanda una sincronización precisa para conectar múltiples zonas y, durante el período comprendido entre el 16 de julio y el 17 de agosto de 2017, este sistema aeroportuario gestionó un volumen alto de operaciones. 

A pesar de la planificación de los itinerarios, se observan desviaciones constantes entre los horarios de salida y llegada programados frente a los horarios reales, lo que se traduce en una acumulación de retrasos que no se distribuye de manera correcta. 
Si no se aíslan y miden estas variables temporales y operacionales, resulta imposible diseñar estrategias de optimización basadas en datos. Por lo tanto, el presente estudio busca dar respuesta a la siguiente interrogante principal:

¿Cuál es el nivel de cumplimiento de los horarios programados de los vuelos "Arrived" en aeropuertos rusos entre el 16 de julio y el 15 de agosto de 2017, y cómo inciden variables temporales (franja horaria y día de la semana) y operacionales (aeropuertos de origen/destino y tipo de aeronave) en la frecuencia y magnitud de sus retrasos?

---

## JUSTIFICACIÓN

El estudio de la puntualidad en el transporte aéreo es relevante porque es un indicador clave que afecta al tránsito aéreo, la rentabilidad de las aerolíneas y la eficiencia en todo el sistema de aviación. En la actualidad, los pasajeros están dispuestos a pagar más por volar con aerolíneas que tienen un mejor historial de puntualidad. Dichas aerolíneas suelen tener márgenes de ganancias operativas superiores. Cada punto de mejora se traduce en millones de dólares de ahorro, ya que se reducen los costos asociados a los retrasos (como compensaciones a pasajeros, combustible extra y horas de tripulación) y se optimiza el uso de los aviones.

Desde una perspectiva académica, resulta significativo analizar cómo diversos factores influyen en las salidas y llegadas de los vuelos, mediante el uso de herramientas de análisis estadístico y modelado de datos que permitan identificar patrones, tendencias y correlaciones entre variables asociadas. Al cruzar variables temporales (día, hora) y operacionales (tipo de aeronave, aeropuertos de origen/destino), la investigación no solo describe el fenómeno, sino que generará información accionable. Este tipo de análisis puede contribuir a identificar áreas de alta incidencia geográfica y franjas horarias críticas, así como a generar conclusiones sobre futuras estrategias de optimización de la puntualidad, reducción de costos y mejora de la experiencia del pasajero en el sector aeronáutico.

---

## Objetivo general

## Objetivos específicos
- **
- **
- **
- **
- **
