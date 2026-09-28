# Databricks notebook source
# MAGIC %md
# MAGIC # Ingesta a Bronze
# MAGIC Lectura de los CSV con el esquema declarado en el contrato.

# COMMAND ----------

from src.ingestion.contracts import cargar_contrato, esquema_de

contrato = cargar_contrato("../conf/data_contracts.yaml")
esquema = esquema_de(contrato, "bureau")

for campo in esquema.fields:
    print(f"{campo.name:25s} {campo.dataType.simpleString():8s} nulable={campo.nullable}")
# COMMAND ----------
# COMMAND ----------

from src.ingestion.readers import leer_csv

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"
archivo = contrato["tablas"]["bureau"]["archivo"]

df = leer_csv(spark, f"{RUTA}/{archivo}", esquema)

print("Filas:", df.count())
print("Filas con datos rescatados:", df.filter("_rescued_data IS NOT NULL").count())
display(df.limit(5))

# COMMAND ----------

import uuid
from src.ingestion.metadata import agregar_metadatos, agregar_row_hash

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

from src.ingestion.contracts import validar_estructura

for tabla, info in contrato["tablas"].items():
    validar_estructura(spark, f"{RUTA}/{info['archivo']}", contrato, tabla)
    print(f"✓ {tabla}")

# COMMAND ----------

from src.ingestion.contracts import ContratoRoto

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

from src.ingestion.writers import escribir_bronze

for intento in [1, 2]:
    print(f"--- Carga {intento} ---")
    for tabla, info in contrato["tablas"].items():
        ruta = f"{RUTA}/{info['archivo']}"
        destino = f"riesgo.bronze.{tabla}"

        validar_estructura(spark, ruta, contrato, tabla)
        df = leer_csv(spark, ruta, esquema_de(contrato, tabla))

        if info["llave"] == ["_row_hash"]:
            columnas = [c["nombre"] for c in info["columnas"]]
            df = agregar_row_hash(df, columnas)

        df = agregar_metadatos(df, info["archivo"], batch_id=str(uuid.uuid4()))
        modo = escribir_bronze(spark, df, destino, info["llave"])
        print(f"{tabla:25s} {modo:8s} {spark.table(destino).count():>12,} filas")