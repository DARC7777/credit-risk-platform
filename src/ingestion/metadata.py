from pyspark.sql import functions as F


def agregar_metadatos(df, archivo, batch_id,
                      source_system="home_credit", source_version="kaggle-2018"):
    return (df
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.lit(archivo))
            .withColumn("_source_system", F.lit(source_system))
            .withColumn("_source_version", F.lit(source_version))
            .withColumn("_batch_id", F.lit(batch_id)))


def agregar_row_hash(df, columnas):
    valores = [F.coalesce(F.col(c).cast("string"), F.lit("<null>")) for c in columnas]
    return df.withColumn("_row_hash", F.sha2(F.concat_ws("|", *valores), 256))