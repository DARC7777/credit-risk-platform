def leer_csv(spark, ruta, esquema):
    return (spark.read
            .option("header", "true")
            .option("rescuedDataColumn", "_rescued_data")
            .schema(esquema)
            .csv(ruta))