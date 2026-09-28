import yaml
from pyspark.sql.types import (
    StructType, StructField, IntegerType, DoubleType, StringType,
)

TIPOS = {
    "int": IntegerType(),
    "double": DoubleType(),
    "string": StringType(),
}


def cargar_contrato(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def esquema_de(contrato, tabla):
    columnas = contrato["tablas"][tabla]["columnas"]
    return StructType([
        StructField(c["nombre"], TIPOS[c["tipo"]], c["nulable"])
        for c in columnas
    ])

class ContratoRoto(Exception):
    pass


def validar_estructura(spark, ruta, contrato, tabla):
    esperadas = [c["nombre"] for c in contrato["tablas"][tabla]["columnas"]]
    recibidas = spark.read.option("header", "true").csv(ruta).columns

    faltan = [c for c in esperadas if c not in recibidas]
    sobran = [c for c in recibidas if c not in esperadas]
    orden_ok = recibidas == esperadas

    if faltan or sobran or not orden_ok:
        raise ContratoRoto(
            f"{tabla}: faltan={faltan} sobran={sobran} orden_correcto={orden_ok}"
        )