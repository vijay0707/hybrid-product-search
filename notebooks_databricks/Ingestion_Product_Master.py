# Databricks notebook source


# COMMAND ----------

from pyspark.sql.functions import current_timestamp, current_date, sha2, col, lit, regexp_extract
from pyspark.sql.types import StructType, StructField, StringType


raw_path = "/Volumes/product_master/default/raw/products/*.json"
raw_df = spark.read.text(raw_path)

bronze_df = raw_df.withColumn(
    "raw_payload", col("value")
).withColumn(
    "source", lit("amazon")
).withColumn(
    "ingestion_ts", current_timestamp()
).withColumn(
    "ingestion_date", current_date()
).withColumn(
    "file_name", regexp_extract(col("_metadata.file_path"), r"([^/]+$)", 1)
).withColumn(
    "record_hash", sha2(col("value"), 256)
).drop("value")

# display(bronze_df)
bronze_df.write.mode("append").saveAsTable("product_master.bronze.products_raw")


# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM product_master.bronze.products_raw; 

# COMMAND ----------

