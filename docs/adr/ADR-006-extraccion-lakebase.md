# ADR-006: Extracción desde una base transaccional (Lakebase)

**Estado:** Aceptado
**Fecha:** octubre de 2026
**Fase:** F1 · Ingesta y contratos de datos

## Contexto

En una entidad financiera, las solicitudes de crédito no llegan como archivos
CSV: viven en la base de datos transaccional del core bancario. Una plataforma
de datos realista debe saber extraer de ese tipo de sistema.

Para simularlo, se creó una base Postgres en Lakebase (proyecto
`credit-score`), se cargó la tabla `application_test` como
`public.solicitudes` (48.744 solicitudes sin respuesta conocida, equivalentes
a solicitudes nuevas) y se extrajo hacia `riesgo.bronze.solicitudes_core`.

## Decisión

**La extracción usa el conector nativo `postgresql` de Databricks, con lectura
en paralelo particionada por `SK_ID_CURR`, credenciales en un secret scope y
la misma escritura idempotente del resto de Bronze.**

### Conector nativo en lugar de JDBC genérico

En cómputo serverless, la escritura con el formato `jdbc` genérico está
bloqueada (`UNSUPPORTED_DATA_SOURCE_WRITE`). El conector `postgresql` está
permitido y por dentro sigue usando JDBC. Además, en serverless solo se
aceptan ciertas opciones de escritura: agregar `sslmode` explícitamente
produjo `SERVERLESS_WRITE_OPTIONS_NOT_ALLOWED`. El driver ya negocia una
conexión cifrada por defecto, así que no hace falta.

### Lectura en paralelo

Se consulta primero el mínimo y el máximo de `SK_ID_CURR` en la fuente
(100.001 y 456.250) y se divide la lectura en 4 particiones, cada una con su
propia conexión. Los límites solo deciden dónde cortar: no filtran filas.
Resultado: 4 particiones, 48.744 filas leídas, sin pérdidas ni duplicados.

### Credenciales en un secret scope

Lakebase autentica con tokens OAuth que vencen en una hora. El token se guarda
en el secret scope `lakebase`, con la clave `pg_token`, y el notebook lo lee
con `dbutils.secrets.get`. Nunca aparece en el código ni en el repositorio.

Se descartó usar un widget de texto: **los widgets cortan el valor a 2.048
caracteres**, y el token mide 2.058. El token cortado conservaba el formato
de un JWT, pero su firma quedaba incompleta, y Postgres respondía "User is not
authorized". El diagnóstico se confirmó comparando el largo del valor leído
desde el widget (2.048) y desde el secreto (2.058).

### Metadatos de origen

Las filas extraídas llevan `_source_system = core_bancario_lakebase` y
`_source_file = public.solicitudes`, para distinguir en Bronze qué datos
vinieron de un archivo y cuáles de la base transaccional.

## Consecuencias

**Positivas:** la misma función de escritura (`escribir_bronze`) sirve para
datos que llegan de archivos y de bases de datos, porque la lógica vive en
`src/` y no en los notebooks.

**Negativas y pendientes:**

- El token se renueva a mano cada hora. En producción se generaría
  automáticamente con una cuenta de servicio (service principal).
- La dirección del servidor está escrita en el notebook. Debe moverse a
  `conf/config.yaml`, porque puede cambiar: durante este trabajo el host
  cambió al recrear el proyecto.
- La carga a Postgres usa `overwrite`, porque es solo preparación del
  escenario y no forma parte del pipeline.