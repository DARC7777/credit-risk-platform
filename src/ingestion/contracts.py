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