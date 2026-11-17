# Progreso — credit-risk-platform

## Estado actual
- **Fase:** F0, sin iniciar
- **Siguiente paso:** primer paso de "Entender" en F0
- **Bloqueos:** ninguno
- **Plan:** F0–F15 · núcleo Data Engineer: F0–F2d, F4, F4c, F11–F13 · núcleo MLOps: F4, F7, F11, F12, F13 · opcionales: F5, F8
- **Certificaciones objetivo:**
  1. Databricks Certified Data Engineer **Associate** (temario vigente desde 2026-05-04)
  2. Databricks Certified Data Engineer **Professional** (temario nuevo, vigente desde 2026-10-09)
- **Última actualización:** 2026-11-16

> Leyenda: [x] hecho con evidencia · [~] hecho sin verificar · [ ] pendiente
> `A§n` = sección del examen Associate · `P§n` = sección del examen Professional (temario nuevo)

**Cómo leer cada fase**
- **Pregunta:** el problema de ingeniería que la fase resuelve.
- **Entender:** explorar, listar alternativas y dejar por escrito la decisión con su porqué. Va antes de construir.
- **Construir:** pasos de 20 a 60 minutos. Dicen qué lograr o decidir, no cómo.
- **Compuerta:** lo que se tiene que poder verificar para dar la fase por cerrada.

---

## F0 · Fundación y reproducibilidad
**Pregunta:** ¿Qué necesito tener en pie, y cómo lo organizo, para que cualquier resultado del proyecto se pueda reproducir y explicar?

Entender
- [ ] Lee la descripción del dataset Home Credit: qué representa cada tabla y cómo se relacionan. Dibuja el diagrama de relaciones
- [ ] Escribe en una página el problema de negocio: quién decide, qué decide y cuánto cuesta equivocarse en cada dirección
- [ ] Lista formas de organizar los datos por capas y objetos en la plataforma, y escribe tu decisión con el porqué `A§1`

Construir
- [ ] Decide dónde aterrizan los archivos crudos y quién puede verlos; sube los CSV ahí `A§1`
- [ ] Crea en el workspace la estructura de datos que decidiste `A§1`
- [ ] Decide cómo separar en el repo la lógica reutilizable de la orquestación, y anota el porqué
- [ ] Decide cómo fijar las dependencias para que el entorno se reconstruya igual en otra máquina
- [ ] Define qué significa "reproducible" en este proyecto: qué tiene que quedar registrado de cada corrida
- [ ] Construye la lógica que registra esa huella, con una prueba que demuestre que funciona
- [ ] Prepara un chequeo inicial que confirme, dentro de Databricks, que el entorno y los datos están donde deben

**Compuerta:** en un clon limpio el entorno se reconstruye y las pruebas pasan · el chequeo inicial corre en Databricks y lista las 8 tablas fuente con su conteo · dos corridas con la misma entrada dejan la misma huella

## F1 · Ingesta Bronze
**Pregunta:** ¿Cómo garantizo que los datos aterricen completos, con el tipo correcto y sin duplicarse aunque la carga se repita?

Entender
- [ ] Explora cada archivo fuente: columnas, tipos aparentes, nulos y tamaño. Anota lo que te sorprenda
- [ ] Decide qué identifica de forma única una fila en cada tabla y anota la evidencia
- [ ] Lista las formas de obtener el esquema de un archivo, con los riesgos de cada una, y escribe tu decisión `A§2`

Construir
- [ ] Escribe el contrato de cada tabla: columnas, tipos, nulabilidad y llave
- [ ] Lee una tabla fuente aplicando su contrato y verifica que los tipos resultantes coinciden `A§2`
- [ ] Decide qué pasa cuando un archivo no respeta el contrato (columna faltante, sobrante u orden distinto) y logra que la carga se detenga antes de escribir
- [ ] Decide qué metadatos de ingesta acompañan cada fila y para qué sirve cada uno
- [ ] Decide qué pasa si llega una fila con la misma llave y contenido distinto: ¿reemplaza, se ignora o se guarda como versión? Escribe el porqué
- [ ] Logra que cargar el mismo lote dos veces deje la tabla igual. Demuéstralo con conteos y con el historial de la tabla `A§2`
- [ ] Prueba negativa: muestra qué le pasa a la tabla con una escritura ingenua repetida
- [ ] Lista formas de procesar solo los archivos nuevos cuando llegan cargas periódicas, y escribe tu decisión `A§2`
- [ ] Simula cargas mensuales y procesa solo lo nuevo `A§2`
- [ ] Decide cómo extraer datos de una base operacional (Lakebase) y cómo manejar sus credenciales sin dejarlas en el código `A§2`
- [ ] Extrae una tabla desde Lakebase hacia Bronze con la misma garantía de no duplicar `A§2`
- [ ] Escribe pruebas de la lógica de ingesta que corran fuera de Databricks

**Compuerta:** las 8 tablas en Bronze con el mismo conteo que su archivo · un archivo con el esquema alterado aborta sin escribir nada · la segunda carga del mismo lote no cambia conteos ni agrega filas (salida pegada) · no hay credenciales en el repo

## F1b · Ingesta ampliada
**Pregunta:** ¿Cómo elijo el mecanismo de ingesta correcto cuando cambian el formato, el volumen, la frecuencia o el esquema de la fuente?

Entender
- [ ] Lista los mecanismos de ingesta que ofrece Databricks y compáralos: si son incrementales, quién guarda el estado, qué fuentes aceptan y cuánto cuestan `A§2` `P§2`
- [ ] Explora qué cambia cuando el dato llega anidado o semiestructurado en vez de tabular `A§2` `P§3`

Construir
- [ ] Haz una carga incremental desde el volume con un mecanismo distinto al de F1, y demuestra que repetirla no duplica `A§2`
- [ ] Decide qué hacer cuando la fuente agrega una columna nueva. Pruébalo con un archivo que la traiga, sin perder filas ni valores inesperados `A§2`
- [ ] Construye una versión anidada de `bureau` con su historial mensual, haz que aterrice y llévala después a forma tabular `A§2` `A§3`
- [ ] Guarda el mismo dato anidado sin un esquema fijo y consúltalo. Compara ventajas y costos frente al esquema fijo `P§3`
- [ ] Carga una tabla en otros formatos abiertos y también archivos binarios. Anota qué gana y qué pierde cada uno `P§2`
- [ ] Consulta Lakebase sin copiar los datos y con permisos gobernados. Compáralo con la extracción de F1 `P§2`
- [ ] Investiga cómo capturar continuamente los cambios de una base Postgres. Impleméntalo si Free Edition lo permite; si no, documenta el diseño `A§2` `P§2`
- [ ] Escribe tu guía de decisión: qué mecanismo usar según volumen, frecuencia, tipo de dato y gobierno `A§2`

**Compuerta:** la columna nueva aparece sin perder filas · la carga incremental repetida no duplica · el dato anidado da los mismos totales en forma tabular y sin esquema fijo · la guía cubre todos los mecanismos probados

## F2 · Silver y calidad como compuerta
**Pregunta:** ¿Cómo decido qué dato es confiable para consumir, qué hago con el que no lo es y cuándo detengo todo?

Entender
- [ ] Perfila Bronze buscando problemas de calidad (nulos, valores imposibles, valores centinela, rangos) y anota la evidencia `A§3`
- [ ] Lista alternativas para tratar filas inválidas (descartar, apartar, corregir o detener) y escribe tu decisión con el porqué

Construir
- [ ] Decide si las reglas de calidad viven dentro o fuera del código que las aplica, y escríbelas `A§3`
- [ ] Logra que cada fila rechazada quede guardada con el motivo de su rechazo
- [ ] Decide qué proporción de rechazos detiene la carga y por qué ese número. Logra que se detenga sin escribir
- [ ] Decide la política de nulos por columna y documenta los valores centinela, como el de `DAYS_EMPLOYED` `A§3`
- [ ] Si Bronze guarda varias versiones de un registro, logra que Silver muestre solo la vigente. Compara dos formas de lograrlo y explica en qué difieren `A§3`
- [ ] Implementa las mismas reglas con el mecanismo declarativo de calidad de la plataforma y compáralo con el tuyo `A§3` `P§3`
- [ ] Conserva la historia de correcciones de cada registro además de su versión vigente `P§1` `P§2`
- [ ] Haz que el mismo flujo procese datos que llegan de forma continua, y escribe cuándo conviene cada enfoque `P§1`
- [ ] Prueba la lógica de calidad comparando datos y esquemas contra lo esperado, con transformaciones que se puedan encadenar `P§1`
- [ ] Haz que la tabla rechace datos inválidos aunque alguien escriba por fuera del flujo
- [ ] Escribe el diccionario de datos de Silver y publícalo donde lo vean los usuarios del catálogo `P§7`

**Compuerta:** 10% de corruptos aborta sin escribir · 2% continúa y deja rastro con motivo · una corrección en Bronze aparece como versión nueva en la historia y actualiza la vigente

## F2b · Orquestación
**Pregunta:** ¿Cómo hago que el flujo corra solo, en orden, se recupere de las fallas y me avise, sin que yo intervenga?

Entender
- [ ] Dibuja el grafo de dependencias de tu flujo: qué depende de qué y qué puede correr en paralelo `A§4`
- [ ] Lista formas de disparar un flujo (horario, llegada de datos, cambio en una tabla) y decide cuál corresponde a cada parte `A§4`

Construir
- [ ] Crea un job con el grafo Bronze → Silver y sus dependencias `A§4`
- [ ] Logra que una misma tarea se repita para las 8 tablas sin copiarla 8 veces `A§4` `P§1`
- [ ] Decide qué tareas merecen reintentos y cuántos, y configúralos `A§4`
- [ ] Logra que el job tome otro camino cuando se abre la compuerta de calidad `A§4` `P§1`
- [ ] Usa al menos tres tipos de tarea distintos y anota cuándo conviene cada uno `A§4`
- [ ] Configura los disparadores que decidiste `A§4`
- [ ] Crea el mismo job por tres vías (interfaz, línea de comandos y API) y compáralas `P§1`
- [ ] Provoca una falla y recupera el job cambiando parámetros, sin repetir lo que ya pasó `P§8`
- [ ] Decide quién se entera de cada estado del job y configúralo `P§4`
- [ ] Lee el historial de corridas: duración frente a la línea base y tasa de fallo `A§6` `P§4`

**Compuerta:** si borras Silver, el job la reconstruye · una falla inducida reintenta, toma la rama de fallo y se repara sin re-correr lo que ya pasó

## F2c · CI/CD
**Pregunta:** ¿Cómo llevo el mismo código de desarrollo a producción de forma repetible, revisada y sin pasos manuales?

Entender
- [ ] Lista qué cambia entre dev y prod en este proyecto (catálogo, esquema, permisos, horarios) y qué no debe cambiar `A§5` `P§8`
- [ ] Compara formas de empaquetar y desplegar código y jobs en Databricks, y escribe tu decisión `A§5`

Construir
- [ ] Empaqueta la lógica para que se instale como dependencia y no como archivos sueltos `P§1`
- [ ] Define los entornos dev y prod, con sus diferencias como configuración `A§5` `P§8`
- [ ] Describe como código versionado el job y el pipeline de F2 y F2b `A§5`
- [ ] Valida, despliega y ejecuta en cada entorno desde la línea de comandos `A§5` `P§8`
- [ ] Gestiona las dependencias en cada tipo de cómputo. Provoca un conflicto de librerías, documéntalo y resuélvelo `P§1`
- [ ] Haz el ciclo rama → commit → push → pull request desde el workspace `A§5` `P§8`
- [ ] Logra que cada pull request corra las pruebas y la validación de forma automática `A§5` `P§8`

**Compuerta:** el mismo código se despliega a dev y a prod con un comando y configuración distinta · un pull request muestra CI verde

## F2d · Streaming con estado
**Pregunta:** ¿Cómo proceso eventos que llegan sin parar, con un estado acotado, y obtengo el mismo resultado que un batch aunque el proceso se caiga?

Entender
- [ ] Explica con tus palabras la diferencia entre tiempo de evento y tiempo de proceso, y qué pasa con los eventos que llegan tarde `P§1`
- [ ] Lista las formas de emitir resultados de una agregación continua y cuándo sirve cada una `P§1`

Construir
- [ ] Simula `installments_payments` como un flujo de eventos con un tiempo de evento creíble
- [ ] Agrega por ventanas de tiempo. Decide cuánto retraso toleras y por qué, y logra que el estado no crezca sin límite `P§1`
- [ ] Prueba cada forma de emitir resultados y documenta lo que observes `P§1`
- [ ] Escribe el resultado del flujo en una tabla sin duplicar aunque un micro-lote se reprocese `P§1`
- [ ] Detén el flujo a la mitad, reinícialo y verifica que no cuenta doble `P§1`
- [ ] Logra que una misma tabla reciba datos en batch y en continuo sin romperse `P§2`
- [ ] Estudia en teoría un bus de mensajes y cómo cambiaría el diseño `P§2`

**Compuerta:** después de detener y reiniciar el flujo, los totales coinciden con un cálculo batch sobre los mismos datos

Nota: el bus de mensajes real (Kinesis) se practica en el proyecto 02 de AWS.

## F3 · EDA y protocolo de evaluación
**Pregunta:** ¿Qué dicen los datos sobre el incumplimiento y cómo fijo, antes de modelar, la forma de saber si un modelo es bueno?

Entender
- [ ] Calcula la tasa de incumplimiento global y por segmento, y anota lo que te sorprenda
- [ ] Compara métodos exactos y aproximados para perfilar columnas y mide la diferencia de costo `A§3`

Construir
- [ ] Mide el poder predictivo de cada variable con una métrica que puedas explicarle a negocio
- [ ] Identifica las variables que no estarían disponibles al momento de decidir y descártalas por escrito
- [ ] Decide cómo partir los datos en el tiempo para que la evaluación imite el uso real
- [ ] Congela y versiona un conjunto de 500 casos de referencia
- [ ] Escribe el protocolo de evaluación con umbrales numéricos, antes de entrenar cualquier modelo

**Compuerta:** el protocolo tiene un commit anterior al del primer modelo · los casos de referencia están versionados y se reproducen igual

## F4 · Gold, features y Feature Store
**Pregunta:** ¿Cómo convierto el historial de cada cliente en variables confiables, sin mirar al futuro y a un costo que pueda justificar?

Entender
- [ ] Explora las seis tablas satélite y decide qué comportamientos del cliente vale la pena resumir, y en qué horizontes de tiempo
- [ ] Lista los tipos de objeto que puedes publicar en Gold y decide cuál usar en cada caso según latencia, costo y refresco `A§3` `P§1`

Construir
- [ ] Construye agregaciones por horizonte de tiempo `A§3` `P§3`
- [ ] Mide rachas de mora y deterioro a lo largo del tiempo `P§3`
- [ ] Une las tablas a nivel de cliente. Decide el tipo de unión para cada una y verifica que no multiplicas filas `A§3`
- [ ] Implementa la misma transformación personalizada de tres formas distintas y compara su costo `P§1`
- [ ] Normaliza `ORGANIZATION_TYPE` en sectores con un modelo de lenguaje, si Free Edition lo permite `P§3`
- [ ] Logra que Gold se actualice leyendo solo lo que cambió en Silver `P§5`
- [ ] Optimiza una unión entre una tabla grande y una pequeña, y mide antes y después `A§3`
- [ ] Provoca una unión desbalanceada, léela en el perfil de la consulta y compara dos remedios `A§3` `A§6` `P§5`
- [ ] Mide el efecto de los parámetros de afinación y documenta cuáles permite serverless `A§3`
- [ ] Define la tasa de incumplimiento y la pérdida esperada como métricas reutilizables, con una sola definición `P§9`
- [ ] Publica las features con su descripción y logra que cada consulta respete el momento de cada observación
- [ ] Escribe pruebas por familia de features
- [ ] Agrega Gold como tarea del job de F2b

**Compuerta:** los casos de referencia reproducen los valores esperados · Gold se reconstruye en una corrida

## F4b · Test de fuga temporal
**Pregunta:** ¿Cómo impido de forma automática que una feature use información del futuro?

Entender
- [ ] Escribe tres ejemplos concretos de fuga que podrían ocurrir en este dataset

Construir
- [ ] Escribe una prueba que falle ante una fuga temporal
- [ ] Logra que esa prueba bloquee el merge en CI

**Compuerta:** una feature con fuga sembrada a propósito bloquea el pull request

Nota: la plataforma de features completa vive en el proyecto de GCP.

## F4c · Gobierno, seguridad y compartir datos
**Pregunta:** ¿Cómo garantizo que cada persona vea solo los datos que le corresponden, y que pueda borrar a un cliente por completo cuando lo exija?

Entender
- [ ] Clasifica cada columna sensible (identificadores, ingreso, edad, etc.) y decide qué trato merece `P§6`
- [ ] Compara el control de acceso por roles con el control por atributos, y escribe tu decisión `A§7` `P§6`

Construir
- [ ] Crea, modifica, borra y convierte tablas gestionadas y externas. Verifica qué permite Free Edition `A§7`
- [ ] Crea un grupo de analistas con permisos en cada nivel del catálogo y demuestra cómo se heredan `A§7` `P§7`
- [ ] Aplica mínimo privilegio también a los objetos del workspace (notebooks, jobs, carpetas) `P§6`
- [ ] Oculta el ingreso a quien no pertenezca al grupo autorizado `A§7` `P§6`
- [ ] Limita las filas visibles según el tipo de contrato `A§7` `P§6`
- [ ] Aplica el ocultamiento y el filtro de forma centralizada, a partir de etiquetas `A§7` `P§6`
- [ ] Desidentifica los datos: identificador irreversible, edad en rangos y fuera las columnas innecesarias `P§6`
- [ ] Detecta y enmascara PII en batch y en continuo `P§6`
- [ ] Borra a un cliente de todas las capas, incluidas sus versiones anteriores `P§6`
- [ ] Comparte una tabla con un destinatario externo. Si los entornos colaborativos no están disponibles, estúdialos en teoría `P§2`
- [ ] Escribe cómo conviven guardar versiones en Bronze y el derecho al olvido `A§7` `P§6`

**Compuerta:** un usuario fuera del grupo ve la columna enmascarada y solo sus filas · el cliente purgado no aparece en ninguna capa ni en versiones anteriores

## F5 · Segmentación (opcional)
**Pregunta:** ¿Hay grupos de clientes con comportamiento distinto que el negocio pueda usar, y se mantienen estables en el tiempo?

Entender
- [ ] Decide qué variables describen a un cliente para segmentarlo, y por qué

Construir
- [ ] Reduce la dimensionalidad y agrupa a los clientes, justificando el número de grupos
- [ ] Describe cada segmento en lenguaje de negocio
- [ ] Mide la estabilidad de los segmentos entre periodos

**Compuerta:** los segmentos se mantienen entre dos particiones temporales y cada uno tiene descripción de negocio

## F6 · Modelos y backtesting
**Pregunta:** ¿Supera un modelo complejo a uno simple e interpretable, medido como se usaría en producción?

Entender
- [ ] Repasa el protocolo de F3 y lista qué métricas responden por discriminación, calibración y valor de negocio
- [ ] Compara familias de modelos interpretables y complejos para este problema

Construir
- [ ] Entrena un baseline interpretable
- [ ] Entrena un modelo retador
- [ ] Evalúa ambos con la partición temporal del protocolo, nunca al azar
- [ ] Reporta las métricas y la calibración de los dos
- [ ] Envía predicciones a la competencia de Kaggle y registra el puntaje privado

**Compuerta:** todo se evalúa contra el protocolo de F3, sin mover los umbrales después de ver resultados

## F7 · Tracking, tuning y compuertas de promoción
**Pregunta:** ¿Cómo sé con qué datos, código y parámetros se entrenó cada modelo, y quién decide que pasa a producción?

Entender
- [ ] Lista qué debe registrar cada entrenamiento para poder reproducirlo
- [ ] Escribe las condiciones que un modelo tiene que cumplir para promoverse

Construir
- [ ] Registra cada corrida con la versión de los datos y del código
- [ ] Busca hiperparámetros dejando las corridas agrupadas
- [ ] Implementa las condiciones de promoción como código probado
- [ ] Distingue el modelo vigente del retador sin cambiar el código que los consume
- [ ] Entrena y registra un modelo de respaldo
- [ ] Registra los modelos en el catálogo, con linaje hasta las tablas de entrenamiento
- [ ] Registra la firma del modelo y un ejemplo de entrada

**Compuerta:** un modelo que no cumple una condición no se promueve (probado) · desde el modelo registrado se llega a sus datos y su commit

## F8 · Cosechas y SQL analítico (opcional)
**Pregunta:** ¿Cómo madura la mora de cada cohorte de créditos y qué puedo proyectar a partir de eso?

Entender
- [ ] Define qué es una cosecha en este dataset y cómo vas a medir su maduración

Construir
- [ ] Construye las curvas de mora por cosecha y maduración
- [ ] En SQL: compara periodos contra el anterior, calcula medias móviles y ordena dentro de grupos
- [ ] Arma un reporte trimestral con agregación condicional y redondeo a dos decimales
- [ ] Ajusta por cosecha con lógica aplicada grupo por grupo

**Compuerta:** tres cosechas proyectadas, con su limitación escrita · consultas reutilizables y versionadas

## F9 · Explicabilidad y estabilidad
**Pregunta:** ¿Puedo explicar cada decisión del modelo y detectar cuándo deja de comportarse como al entrenarlo?

Entender
- [ ] Compara formas de explicar un modelo a nivel global y a nivel de cada cliente
- [ ] Define qué significa estabilidad de la población y de cada variable

Construir
- [ ] Explica el modelo a nivel global y da razones por cliente en lenguaje de negocio
- [ ] Implementa las métricas de estabilidad como funciones probadas
- [ ] Mide el desempeño por segmento
- [ ] Escribe la ficha del modelo

**Compuerta:** razones legibles para 10 casos de referencia · métricas de estabilidad con sus pruebas pasando

## F10 · Decisión de negocio y tableros
**Pregunta:** ¿Dónde pongo el umbral de aprobación para maximizar el valor, y cómo lo ve el negocio?

Entender
- [ ] Estima el costo de aprobar a quien no paga y el de rechazar a quien sí paga, y escribe tus supuestos

Construir
- [ ] Construye una matriz de costos parametrizada
- [ ] Traza la curva de ganancia y encuentra el umbral óptimo
- [ ] Simula la política y analiza qué tan sensible es a los supuestos
- [ ] Publica un tablero sobre las métricas de F4 que se actualice como parte del job `A§4` `P§9`

**Compuerta:** el umbral cambia cuando cambian los costos · el tablero se actualiza solo

## F11 · Producción, degradación y rollback
**Pregunta:** ¿Qué pasa cuando el scoring en producción falla, y cómo vuelvo a un estado bueno en minutos?

Entender
- [ ] Lista las formas en que puede fallar el scoring y arma una taxonomía de ocho fallas
- [ ] Compara el scoring batch con el de tiempo real para este caso

Construir
- [ ] Crea un job de scoring desplegado con el mecanismo de F2c `A§4` `A§5` `P§8`
- [ ] Logra que el scoring lea las features igual que en el entrenamiento y escriba sin duplicar
- [ ] Provoca cada una de las ocho fallas y documenta qué pasa
- [ ] Logra que el scoring pase al modelo de respaldo cuando falla el vigente
- [ ] Haz un simulacro de rollback del modelo y de la tabla, con evidencia
- [ ] Expón el modelo para inferencia en tiempo real si Free Edition lo permite; si no, documenta el diseño
- [ ] Logra que el retador puntúe en paralelo sin decidir, y compara sus resultados con los del vigente
- [ ] Guarda cada predicción con su entrada, salida, versión del modelo y momento

**Compuerta:** el rollback queda documentado con evidencia y tiempo medido · cada falla de la taxonomía tiene una respuesta probada

## F12 · Monitoreo, drift y alertas
**Pregunta:** ¿Cómo me entero de que algo se degradó (datos, modelo, costo o jobs) antes de que lo note el negocio?

Entender
- [ ] Decide qué señales vigilar y qué umbral dispara cada alerta
- [ ] Explora qué telemetría ofrece la plataforma sobre costo, auditoría, cómputo y cargas de trabajo `P§4`

Construir
- [ ] Crea las tablas donde viven el monitoreo y las alertas
- [ ] Mide la estabilidad de las variables y la distribución de los scores
- [ ] Define una señal temprana de mora que no espere al resultado final (por ejemplo, la primera cuota)
- [ ] Inyecta drift artificial
- [ ] Usa la telemetría de la plataforma para costo, auditoría y cargas de trabajo `P§4`
- [ ] Lee la salud y la calidad del pipeline declarativo desde sus propios registros `P§4` `P§8`
- [ ] Crea alertas sobre la tasa de cuarentena y sobre una métrica de negocio `P§4`
- [ ] Monitorea jobs y pipelines sin la interfaz: API, línea de comandos y SDK `P§4`
- [ ] Revisa la salud de los jobs: estados, bloqueos aguas arriba, tiempos y tasa de fallo `A§6` `P§4`
- [ ] Compara el monitoreo nativo de la plataforma con tus métricas propias y escribe tu decisión
- [ ] Logra que un drift por encima del umbral dispare un reentrenamiento que respete las condiciones de F7
- [ ] Documenta el monitoreo y escribe el runbook

**Compuerta:** el drift inyectado dispara la alerta y el reentrenamiento · el modelo nuevo solo se promueve si cumple las condiciones de F7

## F13 · FinOps, cómputo y optimización
**Pregunta:** ¿Cuánto cuesta cada parte de la plataforma y qué cambio la abarata sin romperla?

Entender
- [ ] Compara los tipos de cómputo disponibles (límites, dependencias, rendimiento y costo) y decide cuál usa cada carga `A§1` `P§1`
- [ ] Mide el costo actual de cada job a partir de la telemetría `A§1` `P§4`

Construir
- [ ] Construye un modelo de costo mensual proyectado por job y frecuencia `A§1` `P§4`
- [ ] Compara, con mediciones, estrategias de organización física de las tablas según tamaño y patrón de consulta `A§6` `P§5` `P§9`
- [ ] Mide cómo afecta la forma de registrar borrados a las tablas con muchas actualizaciones `P§5`
- [ ] Averigua qué mantenimiento hace la plataforma por ti y qué te ahorra `A§6` `P§5`
- [ ] Mide el efecto de la caché en lecturas repetidas `P§5`
- [ ] Logra archivos de tamaño balanceado y mide la diferencia `P§9`
- [ ] Escribe un runbook para fallas de cómputo: arranque, conflicto de librerías y memoria insuficiente `A§6` `P§8`
- [ ] Decide cómo dimensionarías el cómputo en un entorno pago, y escribe el porqué
- [ ] Calcula el costo por predicción en batch y en tiempo real

**Compuerta:** cada optimización tiene una medición de antes y después · el costo proyectado se compara con el observado

## F14 · Copiloto del analista
**Pregunta:** ¿Cómo construyo un asistente para analistas que responda bien, se abstenga cuando debe y no empeore cuando cambia el prompt?

Entender
- [ ] Decide qué preguntas debe responder el asistente y cuáles no, y qué riesgos tiene darle acceso a datos

Construir
- [ ] Construye tres herramientas: consulta de solo lectura restringida, explicación de una decisión y consulta del runbook
- [ ] Arma un conjunto de 30 preguntas de referencia, 5 de ellas de abstención obligatoria
- [ ] Evalúa con pruebas deterministas y con un modelo como juez
- [ ] Logra que no se pueda promover un prompt que empeore la exactitud
- [ ] Registra de cada respuesta: versión del prompt, herramienta, tokens, latencia y costo

**Compuerta:** un prompt deliberadamente malo es rechazado · un usuario sin permisos recibe una abstención

## F15 · Documentación y narrativa
**Pregunta:** ¿Puedo contar en cinco minutos qué construí, qué decidí y por qué, de forma que lo entienda alguien que no estuvo?

Entender
- [ ] Relee tus decisiones escritas y elige las tres que mejor muestran tu criterio

Construir
- [ ] Escribe el README en inglés
- [ ] Cierra las decisiones escritas, el diccionario de datos y la ficha del modelo
- [ ] Escribe las lecciones aprendidas
- [ ] Ensaya un guion de cinco minutos

**Compuerta:** el guion cabe en cinco minutos y cada afirmación apunta a evidencia en el repo

---

## Cobertura — Data Engineer Associate
| Sección | Peso | Dónde se cubre | Estado |
|---|---|---|---|
| A§1 Plataforma: Delta, Unity Catalog, cómputo y costos | 6% | F0, F13 | Pendiente |
| A§2 Ingesta y carga | 21% | F1, F1b | Pendiente |
| A§3 Transformación y modelado | 22% | F2, F3, F4 | Pendiente |
| A§4 Lakeflow Jobs | 16% | F2b, F10, F11 | Pendiente |
| A§5 CI/CD | 10% | F2c, F11 | Pendiente |
| A§6 Troubleshooting, monitoreo y optimización | 10% | F2b, F4, F12, F13 | Pendiente |
| A§7 Gobierno y seguridad | 15% | F4c | Pendiente |

Con F1b, F2, F2b, F2c, F4 y F4c cerradas queda cubierto cerca del 90%.

## Cobertura — Data Engineer Professional (temario desde 2026-10-09)
| Sección | Peso | Dónde se cubre | Estado |
|---|---|---|---|
| P§1 Desarrollo con Python y SQL | 23% | F2, F2b, F2c, F2d, F4, F13 | Pendiente |
| P§2 Ingesta y adquisición | 12% | F1b, F2, F2d, F4c | Pendiente |
| P§3 Manipulación de datos | 12% | F1b, F2, F4 | Pendiente |
| P§4 Monitoreo y alertas | 10% | F2b, F12, F13 | Pendiente |
| P§5 Costo y rendimiento | 15% | F4, F13 | Pendiente |
| P§6 Seguridad y cumplimiento | 8% | F4c | Pendiente |
| P§7 Gobierno | 5% | F2, F4c | Pendiente |
| P§8 Depuración y despliegue | 10% | F2b, F2c, F11, F12, F13 | Pendiente |
| P§9 Modelado de datos | 5% | F4, F10, F13 | Pendiente |

El Professional exige además F2d, F12 y F13: no se cubre sin la parte de operación.

## Cobertura — MLOps
| Competencia | Dónde se cubre | Estado |
|---|---|---|
| Calidad de datos | F1, F2 | Pendiente |
| Reproducibilidad | F0, F7 | Pendiente |
| Feature store | F4 | Pendiente |
| Tracking y registro | F7 | Pendiente |
| Compuertas de promoción | F7 | Pendiente |
| Orquestación | F2b, F11, F12 | Pendiente |
| CI/CD | F2c, F4b | Pendiente |
| Inferencia batch | F11 | Pendiente |
| Inferencia en tiempo real | F11 | Pendiente |
| Despliegue gradual | F7, F11 | Pendiente |
| Monitoreo y drift | F9, F12 | Pendiente |
| Reentrenamiento automático | F12 | Pendiente |
| Costos | F13 | Pendiente |
| LLMOps | F14 | Pendiente |

Contenedores (Docker, Kubernetes) e infraestructura como código (Terraform) quedan fuera de este proyecto: se practican en los proyectos de AWS y GCP.

**A verificar en Free Edition:** conectores de Lakeflow Connect (en especial CDC de Postgres) · tablas externas y external locations · Iceberg gestionado · federación hacia Lakebase · Delta Sharing y Clean Rooms · system tables disponibles · `ai_query` · metric views · parámetros de Spark en serverless · métricas visibles (Spark UI o query profile) · grupos y segundo usuario para probar permisos · Model Serving · monitoreo nativo de tablas e inferencias.

Lo que Free Edition no permita se estudia en teoría y queda documentado por escrito.

---

## Bitácora
- 2026-11-16 — Reinicio desde cero. Motivo: desarrollar criterio de ingeniería de datos, no solo seguir pasos.
