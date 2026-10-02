# Databricks notebook source
# MAGIC %md
# MAGIC # Lakebase por JDBC
# MAGIC Postgres simula el sistema transaccional del banco; Spark extrae por JDBC.

# COMMAND ----------

%load_ext autoreload
%autoreload 2

# COMMAND ----------

dbutils.widgets.text("pg_token", "", "Token OAuth de Lakebase")

# COMMAND ----------

from src.ingestion.contracts import cargar_contrato, esquema_de
from src.ingestion.readers import leer_csv

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"
contrato = cargar_contrato("../conf/data_contracts.yaml")

PG_HOST = "ep-steep-paper-d8xhu2of.database.us-east-2.cloud.databricks.com"
PG_DB = "databricks_postgres"
JDBC_URL = f"jdbc:postgresql://{PG_HOST}:5432/{PG_DB}?sslmode=require"

props = {
    "user": "daki.dev27@gmail.com",
    "password": dbutils.widgets.get("pg_token"),
    "driver": "org.postgresql.Driver",
}

# COMMAND ----------

df = leer_csv(spark, f"{RUTA}/application_test.csv", esquema_de(contrato, "application_test"))

(df.drop("_rescued_data")
   .write.jdbc(JDBC_URL, "public.solicitudes", mode="overwrite", properties=props))

n = spark.read.jdbc(JDBC_URL, "(SELECT COUNT(*) AS n FROM public.solicitudes) t",
                    properties=props).first()["n"]
print(f"Filas en Postgres: {n:,}")

# COMMAND ----------

limites = spark.read.jdbc(
    JDBC_URL,
    '(SELECT MIN("SK_ID_CURR") AS minimo, MAX("SK_ID_CURR") AS maximo FROM public.solicitudes) t',
    properties=props,
).first()

print(f"SK_ID_CURR va de {limites['minimo']:,} a {limites['maximo']:,}")


# COMMAND ----------

df_pg = spark.read.jdbc(
    url=JDBC_URL,
    table="public.solicitudes",
    column='"SK_ID_CURR"',
    lowerBound=limites["minimo"],
    upperBound=limites["maximo"],
    numPartitions=4,
    properties=props,
)

from pyspark.sql import functions as F
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