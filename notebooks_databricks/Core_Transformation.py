# Databricks notebook source
# MAGIC %md
# MAGIC ### Parse JSON

# COMMAND ----------

from pyspark.sql.functions import from_json
from pyspark.sql.types import *

schema = StructType([
    StructField("parent_asin", StringType()),
    StructField("title", StringType()),
    StructField("main_category", StringType()),
    StructField("store", StringType()),
    StructField("price", DoubleType()),
    StructField("average_rating", DoubleType()),
    StructField("rating_number", IntegerType()),
    StructField("features", ArrayType(StringType())),
    StructField("images", ArrayType(
        StructType([
            StructField("variant", StringType()),
            StructField("thumb", StringType()),
            StructField("large", StringType()),
            StructField("hi_res", StringType())
        ])
    )),
    StructField("details", StructType([
        StructField("UPC", StringType()),
        StructField("Manufacturer", StringType())
    ]))
])

parsed_df = spark.table("bronze.products_raw") \
    .withColumn("json", from_json("raw_payload", schema)) \
    .select("json.*")
display(parsed_df)


# COMMAND ----------

# MAGIC %md
# MAGIC ### Populate silver.products

# COMMAND ----------

from pyspark.sql.functions import expr, uuid, col, current_timestamp

products_df = parsed_df.select(
    expr("uuid()").alias("product_id"),
    "parent_asin",
    "title",
    "main_category",
    "store",
    "price",
    col("average_rating"),
    col("rating_number").alias("rating_count"),
    col("details.UPC").alias("upc"),
    col("details.Manufacturer").alias("manufacturer"),
    current_timestamp().alias("created_ts"),
    current_timestamp().alias("updated_ts")
)

display(products_df)
products_df.write.mode("append").saveAsTable("silver.products")


# COMMAND ----------

# MAGIC %md
# MAGIC ### Populate silver.product_features

# COMMAND ----------

from pyspark.sql.functions import explode, posexplode

features_df = parsed_df.select(
    "parent_asin",
    posexplode("features").alias("feature_order", "feature_text")
).join(
    spark.table("silver.products"),
    "parent_asin"
).select(
    expr("uuid()").alias("feature_id"),
    "product_id",
    "feature_text",
    "feature_order"
)

display(features_df)

features_df.write.mode("append").saveAsTable("silver.product_features")


# COMMAND ----------

# MAGIC %md
# MAGIC ### Populate silver.product_images

# COMMAND ----------

images_df = parsed_df.select(
    "parent_asin",
    explode("images").alias("img")
).join(
    spark.table("silver.products"),
    "parent_asin"
).select(
    expr("uuid()").alias("image_id"),
    "product_id",
    col("img.variant"),
    col("img.thumb").alias("thumb_url"),
    col("img.large").alias("large_url"),
    col("img.hi_res").alias("hi_res_url"),
    (col("img.variant") == "MAIN").alias("is_primary")
)

display(images_df)
images_df.write.mode("append").saveAsTable("silver.product_images")


# COMMAND ----------

