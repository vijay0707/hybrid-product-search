# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS product_master COMMENT 'This is customer catalog';
# MAGIC CREATE DATABASE IF NOT EXISTS product_master.bronze;
# MAGIC CREATE DATABASE IF NOT EXISTS product_master.silver;
# MAGIC CREATE DATABASE IF NOT EXISTS product_master.gold;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW DATABASES IN product_master;

# COMMAND ----------

# MAGIC %md
# MAGIC ### BRONZE LAYER – DDLs

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Raw Products Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.bronze.products_raw (
# MAGIC   raw_payload STRING,
# MAGIC   source STRING,
# MAGIC   ingestion_ts TIMESTAMP,
# MAGIC   ingestion_date DATE,
# MAGIC   file_name STRING,
# MAGIC   record_hash STRING
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY (ingestion_date);
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### SILVER LAYER – DDLs

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Core Products Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.silver.products (
# MAGIC   product_id STRING,
# MAGIC   parent_asin STRING,
# MAGIC   title STRING,
# MAGIC   main_category STRING,
# MAGIC   store STRING,
# MAGIC   price DOUBLE,
# MAGIC   average_rating DOUBLE,
# MAGIC   rating_count INT,
# MAGIC   upc STRING,
# MAGIC   manufacturer STRING,
# MAGIC   created_ts TIMESTAMP,
# MAGIC   updated_ts TIMESTAMP
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY (main_category);
# MAGIC
# MAGIC -- Product Features Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.silver.product_features (
# MAGIC   feature_id STRING,
# MAGIC   product_id STRING,
# MAGIC   feature_text STRING,
# MAGIC   feature_order INT
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- Product Images Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.silver.product_images (
# MAGIC   image_id STRING,
# MAGIC   product_id STRING,
# MAGIC   variant STRING,
# MAGIC   thumb_url STRING,
# MAGIC   large_url STRING,
# MAGIC   hi_res_url STRING,
# MAGIC   is_primary BOOLEAN
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- Product Categories Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.silver.product_categories (
# MAGIC   category_id STRING,
# MAGIC   product_id STRING,
# MAGIC   category_level INT,
# MAGIC   category_name STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- Product Metadata Table
# MAGIC CREATE TABLE IF NOT EXISTS product_master.silver.product_metadata (
# MAGIC   metadata_id STRING,
# MAGIC   product_id STRING,
# MAGIC   metadata_key STRING,
# MAGIC   metadata_value STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### GOLD LAYER – DDLs

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Product Summary Mart
# MAGIC CREATE TABLE IF NOT EXISTS product_master.gold.product_summary (
# MAGIC   product_id STRING,
# MAGIC   parent_asin STRING,
# MAGIC   title STRING,
# MAGIC   main_category STRING,
# MAGIC   store STRING,
# MAGIC   price DOUBLE,
# MAGIC   average_rating DOUBLE,
# MAGIC   rating_count INT,
# MAGIC   feature_count INT,
# MAGIC   image_count INT
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY (main_category);
# MAGIC
# MAGIC -- Category Metrics Mart
# MAGIC CREATE TABLE IF NOT EXISTS product_master.gold.category_metrics (
# MAGIC   main_category STRING,
# MAGIC   store STRING,
# MAGIC   total_products INT,
# MAGIC   avg_price DOUBLE,
# MAGIC   avg_rating DOUBLE
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- ML Text Corpus Table
# MAGIC CREATE TABLE IF NOT EXISTS gold.product_text_corpus (
# MAGIC   product_id STRING,
# MAGIC   parent_asin STRING,
# MAGIC   combined_text STRING
# MAGIC )
# MAGIC USING DELTA;
# MAGIC

# COMMAND ----------

