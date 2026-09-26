# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Exploración de fuentes de datos

# MAGIC Inventario de los CSV antes de escribir los contratos de datos.

# COMMAND ----------

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"

archivos = [f for f in dbutils.fs.ls(RUTA) if f.name.endswith(".csv")]
for f in archivos:
    print(f"{f.name:40s} {f.size / 1e6:8.1f} MB")

# COMMAND ----------

resumen = []
for f in archivos:
    df = (spark.read
          .option("header", "true")
          .option("inferSchema", "true")
          .option("samplingRatio", 0.1)
          .csv(f.path))
    resumen.append((f.name, df.count(), len(df.columns)))

display(spark.createDataFrame(resumen, ["archivo", "filas", "columnas"]).sort("archivo"))

# COMMAND ----------

import yaml

excluir = {"sample_submission.csv", "HomeCredit_columns_description.csv"}

contrato = {"version": 1, "tablas": {}}

for f in archivos:
    if f.name in excluir:
        continue
    df = (spark.read
          .option("header", "true")
          .option("inferSchema", "true")
          .option("samplingRatio", 0.1)
          .csv(f.path))
    nombre_tabla = f.name.replace(".csv", "").lower()
    contrato["tablas"][nombre_tabla] = {
        "archivo": f.name,
        "llave": [],  # se llena a mano
        "columnas": [
            {"nombre": c.name,
             "tipo": c.dataType.simpleString(),
             "nulable": True}
            for c in df.schema.fields
        ],
    }

with open("../conf/data_contracts_draft.yaml", "w") as fh:
    yaml.safe_dump(contrato, fh, sort_keys=False, allow_unicode=True)

print("Tablas en el borrador:", list(contrato["tablas"]))
