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