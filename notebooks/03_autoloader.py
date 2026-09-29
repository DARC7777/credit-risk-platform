# Databricks notebook source
# MAGIC %md
# MAGIC # Autoloader
# MAGIC Carga incremental: solo procesa los archivos nuevos.

# COMMAND ----------

%load_ext autoreload
%autoreload 2

# COMMAND ----------

import uuid
from pyspark.sql import functions as F
from src.ingestion.contracts import cargar_contrato, esquema_de
from src.ingestion.autoloader import cargar_con_autoloader

RUTA = "/Volumes/riesgo/bronze/home_credit_raw"
contrato = cargar_contrato("../conf/data_contracts.yaml")

spark.sql("CREATE VOLUME IF NOT EXISTS riesgo.bronze.landing")
spark.sql("CREATE VOLUME IF NOT EXISTS riesgo.bronze.checkpoints")

LANDING = "/Volumes/riesgo/bronze/landing/bureau"
CHECKPOINT = "/Volumes/riesgo/bronze/checkpoints/bureau_autoloader"
DESTINO = "riesgo.bronze.bureau_autoloader"

base = spark.read.option("header", "true").csv(f"{RUTA}/bureau.csv")

def entregar(n):
    (base.filter(F.col("SK_ID_BUREAU").cast("int") % 3 == n)
         .coalesce(1)
         .write.mode("overwrite").option("header", "true")
         .csv(f"{LANDING}/entrega_{n}"))

def cargar():
    cargar_con_autoloader(spark, LANDING, esquema_de(contrato, "bureau"),
                          DESTINO, CHECKPOINT, batch_id=str(uuid.uuid4()))
    print(f"{DESTINO}: {spark.table(DESTINO).count():,} filas")

# COMMAND ----------

entregar(0)
cargar()


# COMMAND ----------

entregar(1)
cargar()

# COMMAND ----------

cargar()