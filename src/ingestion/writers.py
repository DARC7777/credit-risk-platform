from delta.tables import DeltaTable


def escribir_bronze(spark, df, tabla_destino, llave):
    if not spark.catalog.tableExists(tabla_destino):
        df.write.format("delta").saveAsTable(tabla_destino)
        return "creada"

    condicion = " AND ".join(f"t.{c} = s.{c}" for c in llave)
    (DeltaTable.forName(spark, tabla_destino).alias("t")
        .merge(df.alias("s"), condicion)
        .whenNotMatchedInsertAll()
        .execute())
    return "merge"