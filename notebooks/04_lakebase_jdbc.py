# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Lakebase por JDBC
# MAGIC Postgres simula el sistema transaccional del banco; Spark extrae con el conector nativo de Postgres.

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

dbutils.widgets.text("pg_token", "", "Token OAuth de Lakebase")

# COMMAND ----------

from src.ingestion.contracts import cargar_contrato, esquema_de
from src.ingestion.readers import leer_csv

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"
contrato = cargar_contrato("../conf/data_contracts.yaml")

opciones_pg = {
    "host": "ep-broad-river-d80j4ljq.database.us-east-2.cloud.databricks.com",
    "port": "5432",
    "database": "databricks_postgres",
    "user": "daki.dev27@gmail.com",
    "password": dbutils.secrets.get("lakebase", "pg_token"),
}

print("Largo del token:", len(opciones_pg["password"]))

# COMMAND ----------


df = leer_csv(spark, f"{RUTA}/application_test.csv", esquema_de(contrato, "application_test"))

(df.drop("_rescued_data")
   .write.format("postgresql")
   .options(**opciones_pg)
   .option("dbtable", "public.solicitudes")
   .mode("overwrite")
   .save())

n = (spark.read.format("postgresql")
     .options(**opciones_pg)
     .option("query", "SELECT COUNT(*) AS n FROM public.solicitudes")
     .load()
     .first()["n"])
print(f"Filas en Postgres: {n:,}")

# COMMAND ----------

limites = (spark.read.format("postgresql")
           .options(**opciones_pg)
           .option("query", 'SELECT MIN("SK_ID_CURR") AS minimo, MAX("SK_ID_CURR") AS maximo FROM public.solicitudes')
           .load()
           .first())

print(f"SK_ID_CURR va de {limites['minimo']:,} a {limites['maximo']:,}")

# COMMAND ----------

from pyspark.sql import functions as F

df_pg = (spark.read.format("postgresql")
         .options(**opciones_pg)
         .option("dbtable", "public.solicitudes")
         .option("partitionColumn", '"SK_ID_CURR"')
         .option("lowerBound", limites["minimo"])
         .option("upperBound", limites["maximo"])
         .option("numPartitions", 4)
         .load())

print(f"Pedazos: {df_pg.select(F.spark_partition_id()).distinct().count()}")
print(f"Filas leídas: {df_pg.count():,}")

# COMMAND ----------

import uuid
from src.ingestion.metadata import agregar_metadatos
from src.ingestion.writers import escribir_bronze

df_pg = agregar_metadatos(df_pg, archivo="public.solicitudes",
                          batch_id=str(uuid.uuid4()),
                          source_system="core_bancario_lakebase")

destino = "riesgo.bronze.solicitudes_core"
modo = escribir_bronze(spark, df_pg, destino, ["SK_ID_CURR"])
print(f"{destino}: {modo} → {spark.table(destino).count():,} filas")

# COMMAND ----------

