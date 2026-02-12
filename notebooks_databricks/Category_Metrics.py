# Databricks notebook source
# MAGIC %md
# MAGIC ### Category Metrics

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT OVERWRITE product_master.gold.category_metrics
# MAGIC SELECT
# MAGIC   main_category,
# MAGIC   store,
# MAGIC   COUNT(*) AS total_products,
# MAGIC   AVG(price) AS avg_price,
# MAGIC   AVG(average_rating) AS avg_rating
# MAGIC FROM silver.products
# MAGIC GROUP BY 1,2;
# MAGIC

# COMMAND ----------

