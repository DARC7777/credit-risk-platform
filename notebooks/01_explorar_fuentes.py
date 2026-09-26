# Databricks notebook source
# MAGIC %md
# MAGIC # Exploración de fuentes de datos
# MAGIC Inventario de los CSV antes de escribir los contratos de datos


# COMMAND ----------
RUTA = "/Volumes/riesgo/bronze/home_credit_raw"

archivos = [f for f in dbutils.fs.ls(RUTA) if f.name.endswith(".csv")]
for f in archivos:
    print(f"{f.name} {f.size / 1e6:8.1f} MB")


# COMMAND ----------

resumen = []
for f in archivos:
    df = (spark.read
          .option("header", "true")
          .option("inferSchema", "true")
          .option("sampleRatio", 0.1)
          .csv(f.path))
    resumen.append((f.name, df.count(), len(df.columns)))

display(spark.createDataFrame(resumen, ["archivo", "filas", "columnas"]).sort("archivo"))











