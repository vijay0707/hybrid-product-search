# Databricks notebook source
# %pip install faiss-cpu sentence-transformers pyarrow

# COMMAND ----------

# Load Gold Data
gold_df = spark.table("product_master.gold.product_text_corpus")

# Convert to Pandas (OK for Free Edition scale)
pdf = gold_df.toPandas()

pdf.head()

# COMMAND ----------

# Load Embedding Model
from sentence_transformers import SentenceTransformer
import numpy as np

model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)


# COMMAND ----------

# Generate Embeddings
texts = pdf["combined_values"].fillna("").tolist()

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True
)


# COMMAND ----------

# Normalize Embeddings
embeddings = embeddings / np.linalg.norm(
    embeddings,
    axis=1,
    keepdims=True
)

# COMMAND ----------

# Build FAISS Index
import faiss

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

print(f"Total vectors indexed: {index.ntotal}")


# COMMAND ----------

# Persist FAISS Index
faiss_index_path = "/Volumes/product_master/default/faiss/product_index.faiss"
faiss.write_index(index, faiss_index_path)

# COMMAND ----------

# Persist Metadata Mapping
metadata_path = "/Volumes/product_master/default/faiss/product_metadata.parquet"

spark_df = spark.createDataFrame(
    pdf[["product_id", "parent_asin", "title"]]
)

spark_df.write.parquet(
    metadata_path,
    mode="overwrite"
)

# COMMAND ----------

import faiss

# Validate Index Load
# Reload index
faiss_index_path = "/Volumes/product_master/default/faiss/product_index.faiss"
index = faiss.read_index(faiss_index_path)

# Sample query
query = "hand bag"

query_vec = model.encode([query])
query_vec = query_vec / np.linalg.norm(query_vec)

D, I = index.search(query_vec, k=5)

I, D


# COMMAND ----------

# Fetch Matching Products
import pandas as pd
from pyspark.sql.functions import col

metadata = pd.read_parquet(metadata_path)

# Get all matching product_ids
results = metadata.iloc[I[0]].copy()
results["score"] = D[0]

# product_df = spark.table("product_master.gold.product_text_corpus")

product_df = spark.read.parquet("/Volumes/product_master/default/faiss/product_metadata.parquet")

product_ids = results["product_id"].tolist()

filtered_df = product_df.filter(
    col("product_id").isin(product_ids)
)

display(filtered_df)

# COMMAND ----------

