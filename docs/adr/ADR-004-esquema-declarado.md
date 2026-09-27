# ADR-004: Esquema declarado en la ingesta a Bronze

**Estado:** Aceptado
**Fecha:** septiembre de 2026
**Fase:** F1 · Ingesta y contratos de datos

## Contexto 

Las fuentes son 8 archivos CSV. Un CSV es texto plano: no declara el tipo de
ninguna columna. Para leerlo, Spark ofrece dos opciones: inferir los tipos
mirando los datos, o recibir un esquema declarado explícitamente.

Durante la exploración de F1 se observaron dos riesgos de la inferencia:

1. **La inferencia puede esconder errores.** Con `samplingRatio = 0.1`, Spark
   decide el tipo mirando el 10% de las filas. Un valor inválido en el 90% no
   mirado no genera un error: se convierte en nulo sin aviso.
2. **Spark ignora en silencio las opciones mal escritas.** Durante la
   exploración se escribió `sampleRatio` en lugar de `samplingRatio`. El código
   corrió sin error, pero la opción nunca se aplicó. Es el mismo patrón: una
   falla que no avisa.

Además, la inferencia es inestable en el tiempo: si un archivo futuro trae un
texto en una columna numérica, Spark puede cambiar el tipo de la columna y
seguir escribiendo, trasladando el problema a las capas siguientes.

## Decisión

**El esquema de cada tabla se declara en `conf/data_contracts.yaml` y la
ingesta nunca infiere tipos.** La inferencia se usó una única vez, para
generar el borrador del contrato, que luego se revisó a mano.

La ingesta distingue dos tipos de falla, con tratamientos distintos:

| Falla | Ejemplo | Tratamiento |
|---|---|---|
| Valor inválido en una fila | `AMT_CREDIT_SUM = "N/A"` | La fila se escribe en Bronze, marcada, y se alerta si la proporción supera un umbral |
| Estructura rota del archivo | Falta una columna o aparece una nueva | Se aborta el lote completo sin escribir nada |

Las filas con valores inválidos **no se eliminan en Bronze**. Bronze conserva
lo que llegó tal como llegó, para poder rastrear el origen del problema. La
separación en cuarentena ocurre en F2, al pasar a Silver.

### Criterios aplicados al contrato

- **Los tipos de Bronze reflejan cómo llega el dato, no lo que significa.**
  Las columnas `DAYS_*` se declaran como `double` porque algunas llegan
  escritas con punto decimal (`-3648.0`); declararlas `int` haría fallar la
  lectura. La conversión a entero ocurre en Silver.
- **Ante la duda, el tipo más permisivo que no pierda información.**
  `AMT_CREDIT_LIMIT_ACTUAL` se infirió como `int`, probablemente porque la
  muestra solo tenía cupos redondos. Se declara `double`, como todas las
  columnas `AMT_*`: acepta enteros y decimales, sin costo en Bronze.
- **Las columnas llave no admiten nulos.** Una llave nula no identifica
  ninguna fila.

### Llaves verificadas

Las llaves se verificaron comparando el total de filas con el número de
combinaciones distintas de las columnas propuestas.

| Tabla | Llave | Filas |
|---|---|---|
| application_train | SK_ID_CURR | 307.511 |
| application_test | SK_ID_CURR | 48.744 |
| bureau | SK_ID_BUREAU | 1.716.428 |
| bureau_balance | SK_ID_BUREAU, MONTHS_BALANCE | 27.299.925 |
| previous_application | SK_ID_PREV | 1.670.214 |
| pos_cash_balance | SK_ID_PREV, MONTHS_BALANCE | 10.001.358 |
| credit_card_balance | SK_ID_PREV, MONTHS_BALANCE | 3.840.312 |
| installments_payments | _row_hash (técnica) | 13.605.401 |

**Caso `installments_payments`:** la llave natural propuesta (crédito, versión
y número de cuota) repitió 653.483 filas. La investigación mostró pagos
parciales: la misma cuota pagada en varios abonos. Agregar la fecha de pago
redujo las repeticiones a 770, correspondientes a abonos de la misma cuota el
mismo día. Agregar el monto solo trasladaría el problema. Como la fuente no
tiene filas idénticas en todas sus columnas, se usa un hash de la fila
completa como llave técnica.

## Alternativas consideradas

- **Inferir el esquema en cada ingesta.** Descartada por los dos riesgos del
  contexto.
- **Leer todo como texto y tipar en Silver.** Evita fallas de lectura, pero
  retrasa la detección de problemas estructurales y deja Bronze sin contrato.
- **Eliminar las filas inválidas en Bronze.** Descartada: destruye la
  evidencia necesaria para rastrear el problema con la fuente.

## Consecuencias

**Positivas:** un cambio de estructura en la fuente se detecta en el momento
de la ingesta, no semanas después en un tablero. El contrato es un documento
legible por personas que también ejecuta la validación.

**Negativas:** mantener el contrato es trabajo manual; si la fuente agrega una
columna legítima, el contrato debe actualizarse antes de que la ingesta la
acepte.

**Limitación conocida:** la llave técnica de `installments_payments` no puede
distinguir una fila duplicada por error de dos pagos legítimos idénticos
(misma cuota, mismo día, mismo monto). Hoy no existen casos, pero si
aparecieran, el hash los trataría como la misma fila. La mitigación
recomendada es solicitar a la fuente un identificador de transacción.