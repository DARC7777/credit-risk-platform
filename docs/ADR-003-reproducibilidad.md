# ADR-003: Estrategia de reproducibilidad

**Estado:** Aceptado
**Fecha:** 2026-09-17

## Contexto

Un resultado que no se puede reproducir no se puede auditar ni corregir. En
riesgo crediticio esto es especialmente relevante: si un modelo rechaza una
solicitud, debe ser posible reconstruir exactamente con qué datos, qué código
y qué entorno se tomó esa decisión, incluso meses después.

Las fuentes de irreproducibilidad son cinco: la aleatoriedad de las
bibliotecas, la versión de los datos, la versión del código, el entorno de
ejecución y el no determinismo de Spark.

## Decisión

**Aleatoriedad.** Una única semilla declarada en `conf/config.yaml`. La
función `set_seeds()` en `src/utils/reproducibility.py` fija los generadores
globales de `random` y `numpy`. sklearn, LightGBM y Spark no tienen semilla
global: reciben el valor explícitamente en cada llamada, leyéndolo de la misma
configuración. Un test unitario verifica que la misma semilla produce el mismo
resultado y que semillas distintas producen resultados distintos.

**Entorno.** Gestión de dependencias con `uv`, declaradas en `pyproject.toml`
y congeladas en `uv.lock`, que fija el árbol completo de dependencias. Se
prefiere sobre `requirements.txt`, que solo fija lo declarado explícitamente.
La versión de Python se restringe a 3.12 para coincidir con el cómputo
serverless: Databricks Connect serializa el código que envía al cluster, y una
diferencia de versión del intérprete rompe la deserialización.

**Versión de los datos.** Cada ejecución registra la versión Delta de cada
tabla de entrada, obtenida de `DESCRIBE HISTORY`. Delta time travel permite
leer después esa versión exacta, aunque la tabla haya cambiado.

**Versión del código.** Cada ejecución registra el commit de Git.

**No determinismo de Spark.** Se prohíbe `monotonically_increasing_id` como
llave; `sample` siempre con semilla explícita; los ordenamientos siempre con
un criterio de desempate.

## Alternativas consideradas

**`requirements.txt` con versiones fijas.** Más simple y conocido, pero no
congela las dependencias transitivas, así que dos instalaciones separadas en
el tiempo pueden diferir.

**No fijar semillas y aceptar variación.** Haría imposible distinguir si un
cambio de resultado viene de un cambio de código o del azar.

## Consecuencias

**A favor:**
- Un resultado se puede reconstruir a partir de tres datos: commit, versiones
  Delta y semilla.
- Los refactors se pueden verificar contra un resultado esperado, lo que
  habilita el golden set de la fase F3.

**En contra:**
- Registrar versiones y commits en cada ejecución agrega código de
  instrumentación que no aporta valor funcional directo.
- Fijar la semilla puede dar una falsa sensación de estabilidad: un modelo
  cuyo desempeño varía mucho entre semillas es frágil, y la semilla fija lo
  oculta. Se mitiga evaluando con varias semillas en la fase F6.
- Mantener la paridad de versiones con el entorno serverless obliga a
  actualizar el proyecto cuando Databricks actualice su runtime.