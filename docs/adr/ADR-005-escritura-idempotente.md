# ADR-005: Escritura idempotente a Bronze

**Estado:** Aceptado
**Fecha:** octubre de 2026
**Fase:** F1 · Ingesta y contratos de datos

## Contexto

Un proceso de carga se ejecuta de más con frecuencia: falla a la mitad y se
relanza, un reintento automático lo dispara dos veces, o alguien lo corre por
error. Si la escritura simplemente agrega las filas al final, cada ejecución
extra duplica los datos, y el error aparece semanas después como cifras
infladas en un modelo o un tablero.

Se requiere que la escritura a Bronze sea idempotente: ejecutar la misma carga
varias veces debe dejar el mismo resultado que ejecutarla una vez.

## Decisión

**La escritura a Bronze usa `MERGE` de Delta Lake por la llave declarada en el
contrato, y solo inserta las filas cuya llave no existe.** Si la llave ya
existe, la fila no se modifica.

La implementación vive en `src/ingestion/writers.py` (`escribir_bronze`). En la
primera carga la tabla no existe y se crea; en las siguientes se aplica el
`MERGE`.

### Por qué solo insertar

Bronze es el registro de lo que llegó y cuándo llegó por primera vez. Si una
fila ya existe, conserva su `_ingested_at` y su `_batch_id` originales. Las
correcciones de la fuente, si existieran, se resuelven en Silver, donde se
define qué versión de un registro es la vigente.

### Por qué la llave importa tanto

La idempotencia depende de dos condiciones:

1. **La llave identifica cada fila de forma única.** Se verificó tabla por
   tabla antes de escribir (ver ADR-004). Una llave no única hace fallar el
   `MERGE` o deja duplicados.
2. **La llave no depende de nada que cambie entre cargas.** Por eso los
   metadatos de ingesta nunca entran al cálculo de `_row_hash`: si
   `_ingested_at` formara parte del hash, cada carga produciría llaves nuevas
   para las mismas filas y todo se duplicaría.

## Evidencia

- Las 8 tablas se cargaron dos veces seguidas. En la segunda carga, cada tabla
  conservó exactamente el mismo número de filas, y el panel de rendimiento
  registró **0 bytes escritos** en los `MERGE`.
- Verificación posterior por tabla: las filas del CSV, las filas en Bronze y
  las llaves distintas coinciden, y todas las filas pertenecen a un solo
  `_batch_id`.
- Prueba negativa: la misma carga de `bureau` hecha dos veces con `append`
  produjo 3.432.856 filas, 1.716.428 llaves y 2 lotes. La verificación detecta
  la duplicación, lo que demuestra que la prueba puede fallar.

## Alternativas consideradas

- **`append`:** más rápido, pero duplica en cada reintento. Descartado.
- **`overwrite` de la tabla completa:** idempotente, pero borra el historial de
  ingesta y no sirve para cargas incrementales.
- **`MERGE` con actualización (`whenMatchedUpdateAll`):** aplicaría
  correcciones de la fuente, pero sobrescribiría los metadatos de la primera
  llegada. Se reserva para Silver.

## Autoloader: un segundo mecanismo

Para cargas incrementales se probó Autoloader (`src/ingestion/autoloader.py`).
Logra la idempotencia de otra forma: recuerda en un checkpoint qué **archivos**
ya procesó, en lugar de comparar **filas** por llave.

| | MERGE por llave | Autoloader |
|---|---|---|
| Qué recuerda | Filas, por su llave | Archivos, por su ruta |
| Costo | Lee la tabla destino completa | Solo lee archivos nuevos |
| Falla si… | La llave no es única | Llegan los mismos datos en un archivo con otro nombre, o un archivo corregido con el mismo nombre |

Ambos se combinarán en el job de producción (F11): Autoloader decide qué
archivos leer y `MERGE` decide qué filas escribir.

## Consecuencias

**Positivas:** reintentar una carga es seguro. La prueba de idempotencia es
automatizable y forma parte de la compuerta de F1.

**Negativas:** el `MERGE` lee la tabla destino completa en cada carga. Con
`bureau_balance` (27 millones de filas) la lectura fue cercana al doble del
tamaño de la tabla. Para cargas recurrentes, esto se mitiga con Autoloader.