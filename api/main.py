from contextlib import asynccontextmanager
import pickle
import re
import faiss
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


# -------------------------
# CONFIG
# -------------------------
BM25_INDEX_PATH = "artifacts/bm25_index.pkl"
DOC_MAPPING_PATH = "artifacts/bm25_doc_mapping.pkl"
FAISS_INDEX_PATH = "artifacts/product_index.faiss"
METADATA_PATH = "artifacts/product_metadata.parquet"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# -------------------------
# LOAD ARTIFACTS AT STARTUP
# -------------------------
# @app.on_event("startup")
# def load_bm25_artifacts():
#     global bm25, doc_mapping

#     try:
#         with open(BM25_INDEX_PATH, "rb") as f:
#             bm25 = pickle.load(f)

#         with open(DOC_MAPPING_PATH, "rb") as f:
#             doc_mapping = pickle.load(f)

#         print("✅ BM25 artifacts loaded")

#     except Exception as e:
#         raise RuntimeError(f"Failed to load BM25 artifacts: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with open(BM25_INDEX_PATH, "rb") as f:
            app.state.bm25 = pickle.load(f)

        with open(DOC_MAPPING_PATH, "rb") as f:
            app.state.doc_mapping = pickle.load(f)

        print("✅ BM25 artifacts loaded (lifespan)")

        # Load FAISS index
        app.state.faiss_index = faiss.read_index(FAISS_INDEX_PATH)

        # Load metadata
        app.state.metadata = pd.read_parquet(METADATA_PATH)

        print("✅ FAISS artifacts loaded")


        # Load embedding model
        app.state.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        print("✅ Embedding model loaded")

        yield

    except Exception as e:
        raise RuntimeError(f"Failed to load BM25, Faiss artifacts and Model: {e}")


# -------------------------
# APP INIT
# -------------------------
app = FastAPI(
    title="Amazon Product Search",
    version="1.0.0",
    lifespan=lifespan
)


# -------------------------
# REQUEST / RESPONSE MODELS
# -------------------------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


# -------------------------
# UTILS
# -------------------------
def tokenize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.split(" ")

def normalize(vec: np.ndarray) -> np.ndarray:
    return vec / np.linalg.norm(vec, axis=1, keepdims=True)


def normalize_scores(score_dict):
    if not score_dict:
        return {}

    max_score = max(score_dict.values())
    min_score = min(score_dict.values())

    if max_score == min_score:
        return {k: 1.0 for k in score_dict}

    return {
        k: (v - min_score) / (max_score - min_score)
        for k, v in score_dict.items()
    }


# -------------------------
# BASE URL
# -------------------------
BASE_URL = "/api"


# -------------------------
# LEXICAL SEARCH ENDPOINT
# -------------------------
@app.post(f"{BASE_URL}/search/lexical")
def lexical_search(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    bm25 = app.state.bm25
    doc_mapping = app.state.doc_mapping

    tokens = tokenize(request.query)

    scores = bm25.get_scores(tokens)

    top_indices = np.argsort(scores)[::-1][: request.top_k]

    results = []
    for idx in top_indices:
        score = scores[idx]
        if score <= 0:
            continue

        doc = doc_mapping[idx]

        results.append({
            "product_id": doc["product_id"],
            "parent_asin": doc["parent_asin"],
            "main_category": doc["main_category"],
            "bm25_score": float(score)
        })

    return {
        "query": request.query,
        "results": results
    }

# -------------------------
# FAISS SEARCH ENDPOINT
# -------------------------
@app.post(f"{BASE_URL}/search/semantic")
def semantic_search(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    model = app.state.model
    index = app.state.faiss_index
    metadata = app.state.metadata

    # Encode query
    query_vec = model.encode([request.query])
    query_vec = normalize(query_vec)

    # Search FAISS
    distances, indices = index.search(query_vec, request.top_k)

    # Fetch matching products
    results = metadata.iloc[indices[0]].copy()
    results["score"] = distances[0]

    return {
        "query": request.query,
        "results": results.to_dict(orient="records")
    }


@app.post(f"{BASE_URL}/search/hybrid")
def hybrid_search(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # -------------------------
    # Load artifacts
    # -------------------------
    model = app.state.model
    faiss_index = app.state.faiss_index
    metadata = app.state.metadata

    bm25 = app.state.bm25
    doc_mapping = app.state.doc_mapping

    # -------------------------
    # 1. Semantic Search (FAISS)
    # -------------------------
    query_vec = model.encode([request.query])
    query_vec = query_vec / np.linalg.norm(query_vec, axis=1, keepdims=True)

    sem_distances, sem_indices = faiss_index.search(query_vec, request.top_k * 5)

    semantic_scores = {}
    for idx, score in zip(sem_indices[0], sem_distances[0]):
        product_id = metadata.iloc[idx]["product_id"]
        semantic_scores[product_id] = float(score)

    # -------------------------
    # 2. Lexical Search (BM25)
    # -------------------------
    query_tokens = tokenize(request.query)
    bm25_scores = bm25.get_scores(query_tokens)

    lexical_scores = {}
    for idx, score in enumerate(bm25_scores):
        if score <= 0:
            continue
        product_id = doc_mapping[idx]["product_id"]
        lexical_scores[product_id] = float(score)

    # -------------------------
    # 3. Normalize Scores
    # -------------------------
    semantic_scores = normalize_scores(semantic_scores)
    lexical_scores = normalize_scores(lexical_scores)

    # -------------------------
    # 4. Hybrid Re-ranking
    # -------------------------
    candidate_ids = set(semantic_scores) | set(lexical_scores)

    hybrid_results = []
    for product_id in candidate_ids:
        sem_score = semantic_scores.get(product_id, 0.0)
        lex_score = lexical_scores.get(product_id, 0.0)

        final_score = (0.65 * sem_score) + (0.35 * lex_score)

        hybrid_results.append({
            "product_id": product_id,
            "semantic_score": sem_score,
            "bm25_score": lex_score,
            "final_score": final_score
        })

    # -------------------------
    # 5. Sort & Fetch Metadata
    # -------------------------
    hybrid_results.sort(key=lambda x: x["final_score"], reverse=True)
    hybrid_results = hybrid_results[:request.top_k]

    result_df = metadata[metadata["product_id"].isin(
        [r["product_id"] for r in hybrid_results]
    )]

    result_map = result_df.set_index("product_id").to_dict(orient="index")

    # enrich response
    for r in hybrid_results:
        r.update(result_map.get(r["product_id"], {}))

    return {
        "query": request.query,
        "results": hybrid_results
    }



# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
