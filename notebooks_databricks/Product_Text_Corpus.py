# Databricks notebook source
# MAGIC %md
# MAGIC ### Product Text Corpus

# COMMAND ----------

from pyspark.sql.functions import expr, col

text_corpus_df = spark.table("silver.products").join(spark.table("silver.product_features"), "product_id") \
                       .select("product_id",
                               "parent_asin",
                               "title",
                               "main_category",
                               "feature_text",
                               "feature_order"
                               )

result_df = (
    text_corpus_df
    .groupBy(
        "product_id",
        "parent_asin",
        "title",
        "main_category"
    )
    .agg(
        expr("""
            concat_ws(
              ',',
              transform(
                sort_array(collect_list(struct(feature_order, feature_text))),
                x -> x.feature_text
              )
            )
        """).alias("combined_values")
    )
)

result_df.write.mode("overwrite").saveAsTable("product_master.gold.product_text_corpus")
display(result_df)


# COMMAND ----------

