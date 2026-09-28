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