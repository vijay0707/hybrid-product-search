# Databricks notebook source
# MAGIC %md
# MAGIC ### Product Summary

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT OVERWRITE product_master.gold.product_summary
# MAGIC SELECT
# MAGIC   p.product_id,
# MAGIC   p.parent_asin,
# MAGIC   p.title,
# MAGIC   p.main_category,
# MAGIC   p.store,
# MAGIC   p.price,
# MAGIC   p.average_rating,
# MAGIC   p.rating_count,
# MAGIC   COUNT(DISTINCT f.feature_id) AS feature_count,
# MAGIC   COUNT(DISTINCT i.image_id) AS image_count
# MAGIC FROM silver.products p
# MAGIC LEFT JOIN silver.product_features f ON p.product_id = f.product_id
# MAGIC LEFT JOIN silver.product_images i ON p.product_id = i.product_id
# MAGIC GROUP BY 1,2,3,4,5,6,7,8;
# MAGIC

# COMMAND ----------

