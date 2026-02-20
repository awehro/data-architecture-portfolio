from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

BRONZE_PATH = "data/bronze/events_orders"
SILVER_PATH = "data/silver/orders"
CKPT_PATH = "checkpoints/silver_orders"

spark = (
    SparkSession.builder.appName("bronze-to-silver-orders")
    .master("local[*]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# IMPORTANT: file streaming requires an explicit schema
static_bronze = spark.read.format("parquet").load(BRONZE_PATH)
bronze_schema = static_bronze.schema

# Read Bronze as streaming source with schema
bronze = (
    spark.readStream.format("parquet")
    .schema(bronze_schema)
    .load(BRONZE_PATH)
)

# Parse timestamps and enforce basic types
typed = (
    bronze.withColumn("event_time_ts", to_timestamp(col("event_time")))
    .withColumn("ingest_time_ts", col("ingest_time").cast("timestamp"))
    .select(
        "event_id",
        "event_time_ts",
        "ingest_time_ts",
        "order_id",
        "customer_id",
        col("amount").cast("double").alias("amount"),
        "currency",
        "status",
        "source",
        col("seq").cast("long").alias("seq"),
        col("key").alias("kafka_key"),
        col("topic"),
        col("partition"),
        col("offset"),
    )
)

# Dedupe in streaming requires watermark (state cleanup)
silver = (
    typed.withWatermark("event_time_ts", "10 minutes")
    .dropDuplicates(["event_id"])
)

query = (
    silver.writeStream.format("parquet")
    .option("path", SILVER_PATH)
    .option("checkpointLocation", CKPT_PATH)
    .outputMode("append")
    .start()
)

print("Silver streaming started. Writing to:", SILVER_PATH)
query.awaitTermination()

