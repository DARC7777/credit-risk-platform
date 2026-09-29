from pyspark.sql import functions as F
from src.ingestion.metadata import agregar_metadatos


def cargar_con_autoloader(spark, origen, esquema, destino, checkpoint, batch_id):
    df = (spark.readStream
          .format("cloudFiles")
          .option("cloudFiles.format", "csv")
          .option("pathGlobFilter", "*.csv")
          .option("header", "true")
          .option("rescuedDataColumn", "_rescued_data")
          .schema(esquema)
          .load(origen))

    df = agregar_metadatos(df, archivo="autoloader", batch_id=batch_id)
    df = df.withColumn("_source_file", F.col("_metadata.file_path"))

    consulta = (df.writeStream
                .option("checkpointLocation", checkpoint)
                .trigger(availableNow=True)
                .toTable(destino))
    consulta.awaitTermination()