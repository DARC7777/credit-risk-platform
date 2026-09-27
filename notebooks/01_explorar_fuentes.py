# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # Exploración de fuentes de datos
# MAGIC
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

# COMMAND ----------

def es_llave(tabla, columnas):
    archivo = f"{RUTA}/{contrato['tablas'][tabla]['archivo']}"
    df = spark.read.option("header", "true").csv(archivo)
    total = df.count()
    distintos = df.select(*columnas).distinct().count()
    print(f"{tabla:25s} {str(columnas):55s} filas={total:>10,}  distintos={distintos:>10,}  {'✓ llave' if total == distintos else '✗ repite'}")

es_llave("application_train",     ["SK_ID_CURR"])
es_llave("application_test",      ["SK_ID_CURR"])
es_llave("bureau",                ["SK_ID_BUREAU"])
es_llave("bureau_balance",        ["SK_ID_BUREAU", "MONTHS_BALANCE"])
es_llave("previous_application",  ["SK_ID_PREV"])
es_llave("pos_cash_balance",      ["SK_ID_PREV", "MONTHS_BALANCE"])
es_llave("credit_card_balance",   ["SK_ID_PREV", "MONTHS_BALANCE"])
es_llave("installments_payments", ["SK_ID_PREV", "NUM_INSTALMENT_VERSION", "NUM_INSTALMENT_NUMBER"])