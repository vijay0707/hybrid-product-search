# Databricks notebook source
from pyspark.sql.functions import concat_ws, lower, regexp_replace, col, trim

gold_df = spark.table("product_master.gold.product_text_corpus")

lexical_df = (
    gold_df
    .withColumn(
        "lexical_text",
        concat_ws(
            " ",
            col("title"),
            col("main_category"),
            col("combined_values")
        )
    )
    .withColumn("lexical_text", lower(col("lexical_text")))
    .withColumn(
        "lexical_text",
        regexp_replace(col("lexical_text"), "[^a-z0-9 ]", " ")
    )
    .withColumn("lexical_text", regexp_replace(col("lexical_text"), "\\s+", " "))
    .withColumn("lexical_text", trim(col("lexical_text")))
)


display(lexical_df)

# COMMAND ----------

# Tokenization
from pyspark.sql.functions import split

tokenized_df = lexical_df.withColumn(
    "tokens",
    split(col("lexical_text"), " ")
)

display(tokenized_df)

# COMMAND ----------

# Remove Empty / Bad Rows
clean_df = tokenized_df.filter(
    (col("lexical_text").isNotNull()) &
    (col("lexical_text") != "") &
    (col("title")!= "") &
    (col("tokens").isNotNull()) &
    (col("product_id").isNotNull()) 
)


# COMMAND ----------

bm25_corpus_df = clean_df.select(
    "product_id",
    "parent_asin",
    "main_category",
    "title",
    "tokens"
)

display(bm25_corpus_df)

# COMMAND ----------

# (
#     bm25_corpus_df
#     .write
#     .format("parquet")
#     .mode("overwrite")
#     .option("overwriteSchema", "true")
#     .save("product_master.gold.product_bm25_corpus")
# )

(
    bm25_corpus_df.write.mode("overwrite").partitionBy("product_id").parquet("/Volumes/product_master/default/bm25/product_bm25_corpus.parquet")
)


# COMMAND ----------

# !pip install pandas rank-bm25

# COMMAND ----------

import os
import pickle
import pandas as pd
from rank_bm25 import BM25Okapi


# -------------------------
# CONFIG 
# -------------------------
BM25_CORPUS_PATH = "/Volumes/product_master/default/bm25/product_bm25_corpus.parquet"
BM25_INDEX_PATH = "/Volumes/product_master/default/bm25/bm25_index.pkl"
DOC_MAPPING_PATH = "/Volumes/product_master/default/bm25/bm25_doc_mapping.pkl"

os.makedirs("artifacts", exist_ok=True)


# -------------------------
# LOAD CORPUS
# -------------------------
def load_corpus(path: str) -> pd.DataFrame:
    """
    Loads BM25-ready corpus exported from Databricks
    """
    df = pd.read_parquet(path)

    required_cols = {"product_id", "tokens"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols}")

    return df


# -------------------------
# BUILD BM25
# -------------------------
def build_bm25_index(df: pd.DataFrame):
    """
    Builds BM25 index and document mappings
    """
    corpus_tokens = df["tokens"].tolist()

    bm25 = BM25Okapi(corpus_tokens)

    doc_mapping = {
        idx: {
            "product_id": row.product_id,
            "parent_asin": row.parent_asin,
            "main_category": row.main_category,
            "title": row.title
        }
        for idx, row in df.iterrows()
    }

    return bm25, doc_mapping


# -------------------------
# SAVE ARTIFACTS
# -------------------------
def save_artifacts(bm25, doc_mapping):
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(bm25, f)

    with open(DOC_MAPPING_PATH, "wb") as f:
        pickle.dump(doc_mapping, f)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    print("📥 Loading BM25 corpus...")
    df = load_corpus(BM25_CORPUS_PATH)

    print(f"✅ Loaded {len(df)} documents")

    print("⚙️ Building BM25 index...")
    bm25, doc_mapping = build_bm25_index(df)

    print("💾 Saving BM25 artifacts...")
    save_artifacts(bm25, doc_mapping)

    print("🎉 BM25 index build completed successfully!")


# COMMAND ----------

import numpy as np
import re


def tokenize_query(query: str):
    query = query.lower()
    query = re.sub(r"[^a-z0-9 ]", " ", query)
    query = re.sub(r"\s+", " ", query).strip()
    return query.split(" ")


def bm25_search(query: str, bm25, doc_mapping, top_k=20):
    tokens = tokenize_query(query)

    scores = bm25.get_scores(tokens)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] <= 0:
            continue

        doc = doc_mapping[idx]
        results.append({
            "product_id": doc["product_id"],
            "parent_asin": doc["parent_asin"],
            "category": doc["main_category"],
            "title": doc["title"],
            "bm25_score": float(scores[idx])
        })

    return results


# COMMAND ----------

bm25_search(
        "silicone cupping therapy",
        bm25,
        doc_mapping,
        top_k=5
    )

# COMMAND ----------

