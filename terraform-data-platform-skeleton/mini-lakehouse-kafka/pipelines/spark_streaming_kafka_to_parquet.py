from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType


TOPIC = "events-orders"
BOOTSTRAP = "localhost:9092"

OUT_PATH = "data/bronze/events_orders"
CKPT_PATH = "checkpoints/events_orders"

# minimal schema matching our producer (extra fields tolerated if not listed)
schema = StructType(
    [
        StructField("event_id", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("order_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("currency", StringType(), True),
        StructField("status", StringType(), True),
        StructField("source", StringType(), True),
        StructField("seq", LongType(), True),
    ]
)

spark = (
    SparkSession.builder.appName("kafka-to-parquet-bronze")
    # keep it explicit for local:
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", BOOTSTRAP)
    .option("subscribe", TOPIC)
    .option("startingOffsets", "earliest")
    .load()
)

# Kafka value is bytes -> string -> JSON -> columns
parsed = (
    raw.select(
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp").alias("ingest_time"),
        col("key").cast("string").alias("key"),
        from_json(col("value").cast("string"), schema).alias("event"),
    )
    .select(
        col("topic"),
        col("partition"),
        col("offset"),
        col("ingest_time"),
        col("key"),
        col("event.*"),
    )
)

query = (
    parsed.writeStream.format("parquet")
    .option("path", OUT_PATH)
    .option("checkpointLocation", CKPT_PATH)
    .outputMode("append")
    .start()
)

print("Streaming started. Writing to:", OUT_PATH)
query.awaitTermination()

