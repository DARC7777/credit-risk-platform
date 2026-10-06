# Progreso — credit-risk-platform

## Estado actual
- **Fase:** cierre de F1
- **Siguiente paso:** verificar la recarga de Bronze con la llave nueva
- **Bloqueos:** ninguno
- **Plan:** F0–F15 · núcleo Data Engineer: F0–F2d, F4, F4c, F11–F13 · opcionales: F5, F8
- **Certificaciones objetivo:**
  1. Databricks Certified Data Engineer **Associate** (temario vigente desde 2026-05-04)
  2. Databricks Certified Data Engineer **Professional** (temario nuevo, vigente desde 2026-10-09)
- **Última actualización:** 2026-10-05

> Leyenda: [x] hecho con evidencia · [~] hecho sin verificar · [ ] pendiente
> `A§n` = sección del examen Associate · `P§n` = sección del examen Professional (temario nuevo)

---

## F0 · Fundación y reproducibilidad — CERRADA
- [x] Catálogo `riesgo` con esquemas bronze, silver, gold, ml, ai
- [x] Volume `riesgo.bronze.home_credit_raw` con los CSV de Home Credit
- [x] Entorno con uv y `pyproject.toml` con lockfile
- [x] `load_config` y `set_seeds`, con 3 tests de pytest pasando
- [x] `notebooks/00_setup_check.py`
- [x] ADR-001 (dataset y Spark), ADR-002 (capas), ADR-003 (reproducibilidad)
- [x] `docs/business_problem.md`

## F1 · Ingesta y contratos — EN CIERRE
- [x] `conf/data_contracts.yaml` con las 8 tablas: tipos, nulabilidad y llave verificada
- [x] Lector CSV con esquema declarado (`src/ingestion/readers.py`) y ADR-004
- [x] Metadatos de ingesta y `_row_hash` (`src/ingestion/metadata.py`)
- [x] Validación de estructura: detecta columna faltante, sobrante y orden cambiado
- [x] Escritura idempotente con MERGE: doble carga sin duplicar y prueba negativa con `append`
- [~] Cambio de llave Bronze a llave natural + `_row_hash` (código listo, recarga sin verificar)
- [x] Autoloader con cargas mensuales simuladas (`notebooks/03_autoloader.py`) `A§2`
- [x] Extracción desde Lakebase por JDBC (`notebooks/04_lakebase_jdbc.py`) `A§2`

**Compuerta:** las tablas en Bronze · esquema alterado aborta sin escribir · el mismo lote dos veces no duplica

**Pendientes de cierre:**
- [ ] Pegar la salida del bucle de recarga y de la verificación
- [ ] Actualizar ADR-005 con la llave natural + `_row_hash`
- [ ] Terminar ADR-006: conector nativo, secret scope, token truncado a 2048 caracteres
- [ ] Borrar el proyecto de Lakebase que no se usa
- [ ] Commit final de F1

## F1b · Ingesta ampliada — PLANEADA
- [ ] `COPY INTO` incremental desde el volume hacia una tabla de Unity Catalog `A§2`
- [ ] Autoloader con evolución de esquema: archivo con una columna nueva, `schemaEvolutionMode` y columna de datos rescatados `A§2`
- [ ] JSON anidado: `bureau` con su `bureau_balance` como arreglo, ingerido con Autoloader y aplanado con `explode` `A§2` `A§3`
- [ ] El mismo JSON guardado como `VARIANT` con `parse_json` y consultado con `variant_get`; comparar contra el esquema fijo `P§3`
- [ ] Otros formatos: una tabla en Parquet, una tabla Iceberg gestionada y archivos binarios con `binaryFile` `P§2`
- [ ] Lakebase como catálogo federado (Lakehouse Federation) con permisos de UC y credenciales de conexión; ADR frente al JDBC de F1 `P§2`
- [ ] Lakeflow Connect: CDC desde Postgres (Lakebase) si Free Edition lo permite; si no, estudio teórico `A§2` `P§2`
- [ ] ADR-007: cuándo Autoloader, `COPY INTO`, Lakeflow Connect, federación o JDBC, según volumen, frecuencia, tipo de dato y gobierno `A§2`

**Compuerta:** la columna nueva evoluciona el esquema sin perder filas · `COPY INTO` dos veces no duplica · el JSON aterriza como struct y como `VARIANT`

## F2 · Silver y calidad como compuerta — NO INICIADA
- [ ] Motor de reglas declarativas en YAML (`conf/quality_rules.yaml`, `src/quality/`) `A§3`
- [ ] Tabla `riesgo.silver.cuarentena` con motivo de rechazo por registro
- [ ] Interruptor de circuito al 5%
- [ ] Centinelas documentados (`DAYS_EMPLOYED = 365243`) y política de nulos por columna `A§3`
- [ ] Versión vigente: Silver toma la versión más reciente por llave natural (ventana con `row_number` frente a `dropDuplicates`) `A§3`
- [ ] Las mismas reglas como expectations en un Lakeflow Declarative Pipeline (`expect`, `expect_or_drop`, `expect_or_fail`), con ADR que compara contra el motor propio `A§3` `P§3`
- [ ] AUTO CDC desde las versiones de Bronze: SCD tipo 1 (versión vigente) y tipo 2 (historia de correcciones) con `stored_as_scd_type` `P§1` `P§2`
- [ ] Pipeline en modo streaming desde Autoloader; ADR de Structured Streaming frente a Declarative Pipelines `P§1`
- [ ] Tests del motor con `assertDataFrameEqual`, `assertSchemaEqual` y funciones encadenadas con `DataFrame.transform` `P§1`
- [ ] `CHECK` constraints en Delta y `docs/data_dictionary.md`
- [ ] Descripciones del diccionario publicadas como comentarios y tags en Unity Catalog `P§7`

**Compuerta:** 10% de corruptos aborta sin escribir · 2% continúa y deja rastro en cuarentena · una corrección en Bronze aparece como nueva versión en el SCD2

## F2b · Orquestación con Lakeflow Jobs — PLANEADA
- [ ] Job con DAG: ingesta Bronze → Silver, con dependencias entre tareas `A§4`
- [ ] Tarea for-each sobre las 8 tablas del contrato `A§4` `P§1`
- [ ] Reintentos configurados y rama condicional (if/else) cuando abre el interruptor `A§4` `P§1`
- [ ] Tipos de tarea: notebook, consulta SQL y pipeline declarativo `A§4`
- [ ] Triggers: programado, llegada de archivo al volume y actualización de tabla, con ADR de cuándo usar cada uno `A§4`
- [ ] El mismo job creado por UI, por CLI y por REST API `P§1`
- [ ] Fallo inducido reparado con job repair y parámetros sobrescritos `P§8`
- [ ] Notificaciones por estado del job `P§4`
- [ ] Lectura del historial de runs: tiempos frente a la línea base y tasa de fallo `A§6` `P§4`

**Compuerta:** borrar Silver y el job la reconstruye · un fallo inducido reintenta, toma la rama de fallo y se repara sin re-correr lo que ya pasó

## F2c · CI/CD con Declarative Automation Bundles — PLANEADA
- [ ] `src/` empaquetado como wheel y estructura del proyecto pensada para el bundle `P§1`
- [ ] `databricks.yml` con targets dev y prod, variables y overrides por target (catálogo o esquema) `A§5` `P§8`
- [ ] Job y pipeline de F2/F2b definidos en el bundle `A§5`
- [ ] `databricks bundle validate`, `deploy -t <target>` y `run` desde la CLI `A§5` `P§8`
- [ ] Dependencias en entornos serverless, pipeline y bundle; documentar un conflicto de librería y su solución `P§1`
- [ ] Flujo en Git folder del workspace: rama, commit, push y pull request desde la UI `A§5` `P§8`
- [ ] GitHub Actions que corre pytest y `bundle validate` en cada pull request `A§5` `P§8`

**Compuerta:** el mismo código se despliega a dev y prod con un comando y configuración distinta · un PR muestra CI verde

## F2d · Structured Streaming con estado — PLANEADA
- [ ] Simular `installments_payments` como flujo de eventos con un timestamp de evento derivado
- [ ] Agregación por ventana de tiempo con watermark para acotar el estado `P§1`
- [ ] Modos de salida (append, update, complete) probados y documentados `P§1`
- [ ] `foreachBatch` con MERGE idempotente hacia Delta `P§1`
- [ ] Caída provocada a mitad del flujo y recuperación desde el checkpoint sin contar doble `P§1`
- [ ] Pipeline append-only que recibe batch y streaming sobre la misma tabla Delta `P§2`

**Compuerta:** tras matar el stream y reiniciarlo, los totales coinciden con un cálculo batch sobre los mismos datos

Nota: el bus de mensajes real (Kinesis) se practica en el proyecto 02 de AWS; aquí se estudia Kafka en teoría `P§2`.

## F3 · EDA y protocolo de evaluación — PLANEADA
- [ ] Tasa de incumplimiento global y por segmento; IV y WoE por variable
- [ ] Perfilado con `summary()` y `approx_count_distinct` frente a `countDistinct`, con su diferencia de costo `A§3`
- [ ] Lista escrita de variables descartadas por fuga
- [ ] Definición de la partición out-of-time
- [ ] Golden set de 500 casos congelado y versionado
- [ ] `docs/evaluation_protocol.md` con umbrales numéricos fijados antes de modelar

## F4 · Gold, features y Feature Store — PLANEADA
- [ ] Agregaciones con ventanas de 3, 6, 12 y 24 meses sobre las seis tablas satélite `A§3` `P§3`
- [ ] Funciones de ventana para rachas de mora y deterioro `P§3`
- [ ] Joins: left, inner, por llaves múltiples y `union` frente a `unionByName` `A§3`
- [ ] UDFs: una pandas UDF, una Python UDF y una función SQL registrada en Unity Catalog, con su costo comparado `P§1`
- [ ] `ai_query` para normalizar `ORGANIZATION_TYPE` en sectores, si Free Edition lo permite `P§3`
- [ ] Change Data Feed en Silver; Gold se actualiza leyendo solo los cambios `P§5`
- [ ] `broadcast` justificado por asimetría de tamaños, medido antes y después `A§3`
- [ ] Experimento de skew: AQE con skew join frente a salting, leído en el query profile `A§3` `A§6` `P§5`
- [ ] Parámetros de tuning (`spark.sql.shuffle.partitions`, `autoBroadcastJoinThreshold`) medidos; documentar cuáles permite serverless `A§3`
- [ ] Objetos Gold: vista, vista materializada, streaming table y tabla, con ADR de cuándo usar cada uno según latencia, costo y refresco `A§3` `P§1`
- [ ] Modelo dimensional con una metric view de Unity Catalog para la tasa de incumplimiento y la pérdida esperada `P§9`
- [ ] Registro en Feature Store con descripción por feature
- [ ] Tests unitarios por familia de features
- [ ] Agregar la capa Gold como tarea del job de F2b

**Compuerta:** el golden set reproduce los valores esperados · Gold se reconstruye en una corrida

## F4b · Test de fuga temporal — PLANEADA (acotada)
- [ ] Test automatizado de fuga temporal en CI que bloquea el merge

Nota: la plataforma de features completa vive en el proyecto de GCP.

## F4c · Gobierno, seguridad y compartir datos — PLANEADA
- [ ] Tablas gestionadas frente a externas: crear, modificar, borrar y convertir; verificar qué permite Free Edition `A§7`
- [ ] Grupo `analistas_riesgo` con `GRANT` y `REVOKE` a nivel de catálogo, esquema y tabla; demostrar la herencia de permisos `A§7` `P§7`
- [ ] Mínimo privilegio también en objetos del workspace (notebooks, jobs, carpetas) `P§6`
- [ ] Máscara de columna sobre `AMT_INCOME_TOTAL` según pertenencia a grupo `A§7` `P§6`
- [ ] Filtro de filas por tipo de contrato `A§7` `P§6`
- [ ] Política ABAC con tags gobernados para aplicar máscara y filtro de forma centralizada `A§7` `P§6`
- [ ] Pseudonimización de `SK_ID_CURR` con hash y sal; generalización de la edad en rangos; supresión de columnas no necesarias `P§6`
- [ ] Detección y enmascaramiento de PII en batch y en streaming `P§6`
- [ ] Purga por derecho al olvido: borrar un cliente en Bronze, Silver y Gold, con `VACUUM` y su efecto en time travel `P§6`
- [ ] Delta Sharing hacia un destinatario abierto (D2O); Clean Rooms en teoría si no están disponibles `P§2`
- [ ] ADR-008: RBAC frente a ABAC, y cómo convive la purga con guardar versiones en Bronze `A§7` `P§6`

**Compuerta:** un usuario fuera del grupo ve la columna enmascarada y solo sus filas · el cliente purgado no aparece en ninguna capa ni en versiones anteriores tras el `VACUUM`

## F5 · Segmentación — PLANEADA (opcional)
- [ ] PCA y K-means con selección de k
- [ ] Perfilamiento de segmentos en lenguaje de negocio
- [ ] Estabilidad de los segmentos entre particiones temporales

## F6 · Modelos y backtesting — PLANEADA
- [ ] Baseline de regresión logística con WoE
- [ ] Challenger LightGBM
- [ ] Validación out-of-time, nunca aleatoria
- [ ] AUC, KS, Gini, precision@k y curva de calibración
- [ ] Late submission a Kaggle, con el puntaje privado registrado en MLflow

**Compuerta:** todo evaluado contra el protocolo de F3, sin mover umbrales después de ver resultados

## F7 · MLflow, tuning y compuertas de promoción — PLANEADA
- [ ] Tracking con versión Delta y commit por run
- [ ] Optuna con runs anidados
- [ ] Siete compuertas en `promotion_gates.py`
- [ ] Aliases champion y challenger
- [ ] Modelo de respaldo entrenado y registrado

## F8 · Cosechas y SQL analítico — PLANEADA (opcional)
- [ ] Curvas de mora por cosecha y maduración
- [ ] Análisis en SQL con window functions: `PARTITION BY`, `LAG`/`LEAD`, media móvil, `ROW_NUMBER`
- [ ] Reporte trimestral con agregación condicional y redondeo a dos decimales
- [ ] Ajuste por cosecha con `applyInPandas`

**Compuerta:** tres cosechas proyectadas con su limitación escrita · consultas reutilizables en `sql/`

## F9 · Explicabilidad y estabilidad — PLANEADA
- [ ] SHAP global y códigos de razón en lenguaje de negocio
- [ ] PSI y CSI como funciones testeadas
- [ ] Desempeño por segmento
- [ ] `docs/model_card.md`

## F10 · Decisión de negocio y tableros — PLANEADA
- [ ] Matriz de costos parametrizada
- [ ] Curva de ganancia y umbral óptimo
- [ ] Simulación de política y análisis de sensibilidad
- [ ] Tablero en Databricks SQL sobre la metric view, como tarea de dashboard dentro del job `A§4` `P§9`

## F11 · Producción, degradación y rollback — PLANEADA
- [ ] Job de scoring en Lakeflow Jobs, desplegado con el bundle `A§4` `A§5` `P§8`
- [ ] Feature lookup y escritura idempotente del scoring
- [ ] Las ocho fallas de la taxonomía
- [ ] Degradación al modelo de respaldo
- [ ] Simulacro de rollback documentado con evidencia (alias y `RESTORE TABLE`)

## F12 · Monitoreo, drift y alertas — PLANEADA
- [ ] Tablas `ml.monitoring` y `ml.alertas`
- [ ] PSI, CSI y distribución de scores
- [ ] Proxy de primera cuota
- [ ] Inyección de drift artificial
- [ ] System tables (billing, compute, access, lakeflow) para costo, auditoría y cargas de trabajo `P§4`
- [ ] Event log del pipeline declarativo para salud y calidad de datos `P§4` `P§8`
- [ ] Alerta de Databricks sobre la tasa de cuarentena y sobre una métrica de negocio `P§4`
- [ ] Monitoreo de jobs y pipelines con REST API, CLI y SDK `P§4`
- [ ] Salud de los jobs: estados, bloqueos aguas arriba en el DAG, tiempos y tasa de fallo `A§6` `P§4`
- [ ] `docs/monitoring.md` y `docs/runbook.md`

## F13 · FinOps, cómputo y optimización — PLANEADA
- [ ] ADR de cómputo: serverless (entornos, dependencias, performance mode), all-purpose, job compute y SQL warehouse, con límites y modelo de costo `A§1` `P§1`
- [ ] `docs/cost_model.md` con DBU por job, frecuencia y costo mensual proyectado, a partir de system tables `A§1` `P§4`
- [ ] Comparativa medida: particionamiento, Z-ORDER, Liquid Clustering y `CLUSTER BY AUTO` según tamaño y patrón de consulta `A§6` `P§5` `P§9`
- [ ] Deletion vectors en las tablas con MERGE frecuente, medido antes y después `P§5`
- [ ] Predictive optimization y tablas gestionadas: qué mantenimiento eliminan `A§6` `P§5`
- [ ] Caché de disco en lecturas repetidas `P§5`
- [ ] Compactación y tamaño balanceado de archivos `P§9`
- [ ] Runbook de fallas de cómputo: arranque, conflicto de librerías y memoria insuficiente `A§6` `P§8`
- [ ] ADR de dimensionamiento del cluster para un entorno pago

## F14 · Copiloto del analista — PLANEADA
- [ ] Tres herramientas: SQL de solo lectura con lista blanca, explicación de una decisión, consulta del runbook
- [ ] Golden set de 30 preguntas, con 5 de abstención obligatoria
- [ ] Evals deterministas más juez LLM
- [ ] Compuerta que impide promover un prompt que empeore la exactitud
- [ ] Tracing: versión de prompt, herramienta, tokens, latencia y costo

**Compuerta:** un prompt deliberadamente malo es rechazado · un usuario sin permisos recibe abstención

## F15 · Documentación y narrativa — PLANEADA
- [ ] README en inglés
- [ ] ADRs cerrados, diccionario de datos y model card
- [ ] `lessons_learned.md`
- [ ] Guion de cinco minutos ensayado

---

## Cobertura — Data Engineer Associate
| Sección | Peso | Dónde se cubre | Estado |
|---|---|---|---|
| A§1 Plataforma: Delta, Unity Catalog, cómputo y costos | 6% | F0, F13 | Parcial |
| A§2 Ingesta y carga | 21% | F1, F1b | Parcial |
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

**A verificar en Free Edition:** conectores de Lakeflow Connect (en especial CDC de Postgres) · tablas externas y external locations · Iceberg gestionado · federación hacia Lakebase · Delta Sharing y Clean Rooms · system tables disponibles · `ai_query` · metric views · parámetros de Spark en serverless · métricas visibles (Spark UI o query profile) · grupos y segundo usuario para probar permisos.

Lo que Free Edition no permita se estudia en teoría y queda documentado en el ADR correspondiente.

---

## Decisiones
| Fecha | Decisión | Dónde quedó |
|---|---|---|
| 2026-09 | Esquema declarado, nunca inferido | ADR-004 |
| 2026-10-03 | Llave de Bronze = llave natural + `_row_hash`, para guardar correcciones como versiones | ADR-005 (por actualizar) |
| 2026-10-03 | `installments_payments` usa `_row_hash` como llave: tiene pagos parciales, no duplicados | Contrato de datos |
| 2026-10-03 | Token de Lakebase en secret scope, no en widget | ADR-006 (por terminar) |
| 2026-10-05 | El plan se alinea con los temarios Associate y Professional: se agregan F1b, F2b, F2c, F2d y F4c | Este archivo |

## Preguntas abiertas
- `DAYS_EMPLOYED = 365243`: ¿dato corrupto o centinela? ¿Qué pasa con el interruptor del 5% si va a cuarentena? (F2)
- Bronze guarda versiones de cada registro, pero la purga exige borrar a un cliente por completo: ¿cómo conviven? (F4c)

## Repaso pendiente
- Pregunta 2: qué recuerda Autoloader y qué recuerda MERGE
- Explicar con mis palabras: `info["llave"] + ["_row_hash"]`

---

## Bitácora
### 2026-10-05
- Se agregan fases y tareas para cubrir los temarios Associate y Professional de Databricks.
- Se reordena el archivo: todas las fases antes de Decisiones y Bitácora.

### 2026-10-04
- Se corrige el alcance de F2 a lo definido para este proyecto.
- Se crean `CLAUDE.md` y este archivo para llevar el estado.

### 2026-10-03
- F1 completada en código; se decide la llave natural + `_row_hash`.
- Desde F2, el método es esqueleto con huecos y pistas de sintaxis.

### 2026-09-29
- F0 cerrada.