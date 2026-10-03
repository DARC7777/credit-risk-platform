# Databricks notebook source
# MAGIC %md
# MAGIC # Ingesta a Bronze
# MAGIC Lectura de los CSV con el esquema declarado en el contrato.

# COMMAND ----------

%load_ext autoreload
%autoreload 2

# COMMAND ----------

import uuid
from src.ingestion.contracts import cargar_contrato, esquema_de, validar_estructura, ContratoRoto
from src.ingestion.readers import leer_csv
from src.ingestion.metadata import agregar_metadatos, agregar_row_hash
from src.ingestion.writers import escribir_bronze

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"
contrato = cargar_contrato("../conf/data_contracts.yaml")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exploración: esquema y lectura de bureau

# COMMAND ----------

esquema = esquema_de(contrato, "bureau")

for campo in esquema.fields:
    print(f"{campo.name:25s} {campo.dataType.simpleString():8s} nulable={campo.nullable}")

# COMMAND ----------

archivo = contrato["tablas"]["bureau"]["archivo"]
df = leer_csv(spark, f"{RUTA}/{archivo}", esquema)

print("Filas:", df.count())
print("Filas con datos rescatados:", df.filter("_rescued_data IS NOT NULL").count())
display(df.limit(5))

# COMMAND ----------

tabla = "installments_payments"
archivo = contrato["tablas"][tabla]["archivo"]
columnas = [c["nombre"] for c in contrato["tablas"][tabla]["columnas"]]

df = leer_csv(spark, f"{RUTA}/{archivo}", esquema_de(contrato, tabla))
df = agregar_row_hash(df, columnas)
df = agregar_metadatos(df, archivo, batch_id=str(uuid.uuid4()))

total = df.count()
hashes = df.select("_row_hash").distinct().count()
print(f"Filas: {total:,}  Hashes distintos: {hashes:,}  {'✓ llave' if total == hashes else '✗ repite'}")
display(df.limit(3))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validación de estructura

# COMMAND ----------

for tabla, info in contrato["tablas"].items():
    validar_estructura(spark, f"{RUTA}/{info['archivo']}", contrato, tabla)
    print(f"✓ {tabla}")

# COMMAND ----------

PRUEBAS = f"{RUTA}/_pruebas"
dbutils.fs.mkdirs(PRUEBAS)

base = spark.read.option("header", "true").csv(f"{RUTA}/bureau.csv").limit(100).toPandas()
cols = list(base.columns)

casos = {
    "falta_columna":  base.drop(columns=["AMT_CREDIT_SUM"]),
    "sobra_columna":  base.assign(COLUMNA_NUEVA="x"),
    "orden_cambiado": base[[cols[1], cols[0]] + cols[2:]],
}

for nombre, pdf in casos.items():
    ruta = f"{PRUEBAS}/bureau_{nombre}.csv"
    pdf.to_csv(ruta, index=False)
    try:
        validar_estructura(spark, ruta, contrato, "bureau")
        print(f"✗ {nombre}: NO se detectó")
    except ContratoRoto as e:
        print(f"✓ {nombre}: detectado → {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Carga a Bronze (llave natural + _row_hash)

# COMMAND ----------

# Ejecutar UNA sola vez: borra las tablas para reconstruirlas con _row_hash
for tabla in contrato["tablas"]:
    spark.sql(f"DROP TABLE IF EXISTS riesgo.bronze.{tabla}")

# COMMAND ----------

for tabla, info in contrato["tablas"].items():
    ruta = f"{RUTA}/{info['archivo']}"
    destino = f"riesgo.bronze.{tabla}"

    validar_estructura(spark, ruta, contrato, tabla)
    df = leer_csv(spark, ruta, esquema_de(contrato, tabla))

    columnas = [c["nombre"] for c in info["columnas"]]
    df = agregar_row_hash(df, columnas)

    if "_row_hash" in info["llave"]:
        llave_bronze = info["llave"]
    else:
        llave_bronze = info["llave"] + ["_row_hash"]

    df = agregar_metadatos(df, info["archivo"], batch_id=str(uuid.uuid4()))
    modo = escribir_bronze(spark, df, destino, llave_bronze)
    print(f"{tabla:25s} {modo:8s} {str(llave_bronze):45s} {spark.table(destino).count():>12,} filas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verificación

# COMMAND ----------

for tabla, info in contrato["tablas"].items():
    bronze = spark.table(f"riesgo.bronze.{tabla}")
    csv = spark.read.option("header", "true").csv(f"{RUTA}/{info['archivo']}")

    filas_csv = csv.count()
    filas_bronze = bronze.count()
    llaves = bronze.select(*info["llave"]).distinct().count()
    lotes = bronze.select("_batch_id").distinct().count()

    ok = filas_csv == filas_bronze == llaves and lotes == 1
    print(f"{tabla:25s} csv={filas_csv:>11,} bronze={filas_bronze:>11,} "
          f"llaves={llaves:>11,} lotes={lotes}  {'✓' if ok else '✗'}")

# COMMAND ----------

tabla = "bureau"
info = contrato["tablas"][tabla]
prueba = "riesgo.bronze._prueba_append"

spark.sql(f"DROP TABLE IF EXISTS {prueba}")
for intento in [1, 2]:
    df = leer_csv(spark, f"{RUTA}/{info['archivo']}", esquema_de(contrato, tabla))
    df = agregar_metadatos(df, info["archivo"], batch_id=str(uuid.uuid4()))
    df.write.format("delta").mode("append").saveAsTable(prueba)

t = spark.table(prueba)
print(f"filas={t.count():,}  llaves={t.select(*info['llave']).distinct().count():,}  "
      f"lotes={t.select('_batch_id').distinct().count()}")

spark.sql(f"DROP TABLE {prueba}")