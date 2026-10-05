# Progreso — credit-risk-platform

## Estado actual
- **Fase:** cierre de F1
- **Siguiente paso:** verificar la recarga de Bronze con la llave nueva
- **Bloqueos:** ninguno
- **Última actualización:** 2026-10-04

> Leyenda: [x] hecho con evidencia · [~] hecho sin verificar · [ ] pendiente

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
- [x] Autoloader con cargas mensuales simuladas (`notebooks/03_autoloader.py`)
- [x] Extracción desde Lakebase por JDBC (`notebooks/04_lakebase_jdbc.py`)

**Compuerta:** las tablas en Bronze · esquema alterado aborta sin escribir · el mismo lote dos veces no duplica

**Pendientes de cierre:**
- [ ] Pegar la salida del bucle de recarga y de la verificación
- [ ] Actualizar ADR-005 con la llave natural + `_row_hash`
- [ ] Terminar ADR-006: conector nativo, secret scope, token truncado a 2048 caracteres
- [ ] Borrar el proyecto de Lakebase que no se usa
- [ ] Commit final de F1

## F2 · Silver y calidad como compuerta — NO INICIADA
- [ ] Motor de reglas declarativas en YAML (`conf/quality_rules.yaml`, `src/quality/`)
- [ ] Tabla `riesgo.silver.cuarentena` con motivo de rechazo por registro
- [ ] Interruptor de circuito al 5%
- [ ] Centinelas documentados (`DAYS_EMPLOYED = 365243`) y política de nulos por columna
- [ ] Versión vigente: Silver toma la versión más reciente por llave natural
- [ ] `CHECK` constraints en Delta y `docs/data_dictionary.md`

**Compuerta:** 10% de corruptos aborta sin escribir · 2% continúa y deja rastro en cuarentena

---

## Decisiones
| Fecha | Decisión | Dónde quedó |
|---|---|---|
| 2026-09 | Esquema declarado, nunca inferido | ADR-004 |
| 2026-10-03 | Llave de Bronze = llave natural + `_row_hash`, para guardar correcciones como versiones | ADR-005 (por actualizar) |
| 2026-10-03 | `installments_payments` usa `_row_hash` como llave: tiene pagos parciales, no duplicados | Contrato de datos |
| 2026-10-03 | Token de Lakebase en secret scope, no en widget | ADR-006 (por terminar) |

## Preguntas abiertas
- `DAYS_EMPLOYED = 365243`: ¿dato corrupto o centinela? ¿Qué pasa con el interruptor del 5% si va a cuarentena? (F2)

## Repaso pendiente
- Pregunta 2: qué recuerda Autoloader y qué recuerda MERGE
- Explicar con mis palabras: `info["llave"] + ["_row_hash"]`

---

## Bitácora
### 2026-10-04
- Se corrige el plan de F2: se había mezclado con el del proyecto 02 de AWS.
- Se crean `CLAUDE.md` y este archivo para llevar el estado.

### 2026-10-03
- F1 completada en código; se decide la llave natural + `_row_hash`.
- Desde F2, el método es esqueleto con huecos y pistas de sintaxis.

### 2026-09-29
- F0 cerrada.

## F3 · EDA y protocolo de evaluación — PLANEADA
- [ ] Tasa de incumplimiento global y por segmento; IV y WoE por variable
- [ ] Lista escrita de variables descartadas por fuga
- [ ] Definición de la partición out-of-time
- [ ] Golden set de 500 casos congelado y versionado
- [ ] `docs/evaluation_protocol.md` con umbrales numéricos fijados antes de modelar

## F4 · Gold, features y Feature Store — PLANEADA
- [ ] Agregaciones con ventanas de 3, 6, 12 y 24 meses sobre las seis tablas satélite
- [ ] Funciones de ventana para rachas de mora y deterioro
- [ ] Registro en Feature Store con descripción por feature
- [ ] Tests unitarios por familia de features
- [ ] `broadcast` justificado por asimetría de tamaños, medido antes y después

**Compuerta:** el golden set reproduce los valores esperados · Gold se reconstruye en una corrida

## F4b · Test de fuga temporal — PLANEADA (acotada)
- [ ] Test automatizado de fuga temporal en CI que bloquea el merge

Nota: la plataforma de features completa vive en el proyecto de GCP.

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
- [ ] Tablero en Databricks SQL

## F11 · Producción, degradación y rollback — PLANEADA
- [ ] Job de scoring con dependencias y feature lookup
- [ ] Escritura idempotente del scoring
- [ ] Las ocho fallas de la taxonomía
- [ ] Degradación al modelo de respaldo
- [ ] Simulacro de rollback documentado con evidencia

## F12 · Monitoreo, drift y alertas — PLANEADA
- [ ] Tablas `ml.monitoring` y `ml.alertas`
- [ ] PSI, CSI y distribución de scores
- [ ] Proxy de primera cuota
- [ ] Inyección de drift artificial
- [ ] `docs/monitoring.md` y `docs/runbook.md`

## F13 · FinOps y dimensionamiento — PLANEADA
- [ ] `docs/cost_model.md` con DBU por job, frecuencia y costo mensual proyectado
- [ ] Comparativa medida antes y después de `OPTIMIZE` con Z-ORDER
- [ ] ADR de dimensionamiento del cluster

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