# Databricks notebook source
# MAGIC %md
# MAGIC # Verificación de entorno (F0)
# MAGIC Comprueba que catálogo, esquemas y volume existen antes de que corra
# MAGIC cualquier pipeline. Falla si algo no está.

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos")  # ajustar según dónde quede el Git folder

from src.utils.reproducibility import load_config, set_seeds

cfg = load_config()
fallas = []

# COMMAND ----------

# MAGIC %md ## 1. Catálogo

catalogo = cfg["catalog"]["name"]
existe = spark.sql(f"SHOW CATALOGS LIKE '{catalogo}'").count() > 0

print(f"{'OK  ' if existe else 'FAIL'} | catálogo {catalogo}")
if not existe:
    fallas.append(f"no existe el catálogo {catalogo}")

# COMMAND ----------

# MAGIC %md ## 2. Esquemas

esperados = set(cfg["catalog"]["schemas"])
encontrados = {
    fila.schema_name
    for fila in spark.sql(
        f"SELECT schema_name FROM {catalogo}.information_schema.schemata"
    ).collect()
}

for esquema in sorted(esperados):
    presente = esquema in encontrados
    print(f"{'OK  ' if presente else 'FAIL'} | esquema {esquema}")
    if not presente:
        fallas.append(f"falta el esquema {esquema}")

extras = encontrados - esperados - {"default", "information_schema"}
if extras:
    print(f"WARN | esquemas no declarados: {sorted(extras)}")

# COMMAND ----------

# MAGIC %md ## 3. Volume y archivos

ruta = cfg["paths"]["raw_volume"]
ARCHIVOS_ESPERADOS = 10

try:
    archivos = dbutils.fs.ls(ruta)
    csvs = [a for a in archivos if a.name.endswith(".csv")]
    ok = len(csvs) == ARCHIVOS_ESPERADOS
    print(f"{'OK  ' if ok else 'FAIL'} | {len(csvs)} de {ARCHIVOS_ESPERADOS} CSV en {ruta}")
    if not ok:
        fallas.append(f"se esperaban {ARCHIVOS_ESPERADOS} CSV, hay {len(csvs)}")

    vacios = [a.name for a in csvs if a.size == 0]
    if vacios:
        fallas.append(f"archivos vacíos: {vacios}")
except Exception as e:
    print(f"FAIL | no se pudo leer {ruta}: {e}")
    fallas.append(f"volume inaccesible: {ruta}")

# COMMAND ----------

# MAGIC %md ## 4. Semillas

set_seeds(cfg["project"]["seed"])
print(f"OK   | semilla fijada en {cfg['project']['seed']}")

# COMMAND ----------

# MAGIC %md ## Resultado

if fallas:
    raise RuntimeError("Verificación fallida:\n- " + "\n- ".join(fallas))

print("\nTodas las verificaciones pasaron.")