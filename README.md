# 🛒 Hybrid Product Search Engine

A **production-style hybrid search system** for Amazon product data that combines:

* 🔍 **Lexical search (BM25)** for exact keyword precision
* 🧠 **Semantic search (FAISS + Sentence Transformers)** for meaning-aware retrieval
* ⚖️ **Hybrid re-ranking** to balance precision and recall
* 🧪 **LLM-based evaluation (Gemini)** to assess search quality without labeled data

This project demonstrates **real-world search system design**, not toy examples.

---

## 🚀 Features

* ✅ BM25 lexical search over product text
* ✅ FAISS-based semantic similarity search
* ✅ Hybrid ranking (BM25 + Semantic)
* ✅ FastAPI serving layer
* ✅ Databricks + Delta Lake offline preprocessing
* ✅ LLM (Gemini) as a relevance judge
* ✅ Automated evaluation reports & win-rate metrics

---

## 🏗️ System Architecture (High Level)

```text
Databricks (Delta Tables)
        |
        v
Spark Preprocessing
(Text cleaning, tokenization)
        |
        +--> BM25 Corpus (Parquet)
        |
        +--> Embeddings (Sentence Transformers)
                 |
                 v
              FAISS Index
        |
        v
FastAPI Service
  ├─ /search/lexical
  ├─ /search/semantic
  └─ /search/hybrid
        |
        v
Evaluation Framework (Gemini LLM)
```

---

## 📦 Dataset

Amazon product data with schema:

```text
product_id        STRING
parent_asin       STRING
title             STRING
main_category     STRING
combined_values   STRING
```

Data is stored and processed in **Databricks Delta tables** and exported for serving.

---

## 🔍 Search Approaches

### 1️⃣ Lexical Search (BM25)

* Exact keyword matching
* Strong for brands, product terms, and precision
* Implemented using `rank-bm25`

### 2️⃣ Semantic Search (FAISS)

* Meaning-aware retrieval using embeddings
* Handles synonyms and natural language queries
* Implemented using `sentence-transformers` + FAISS

### 3️⃣ Hybrid Search (Recommended)

Combines both approaches:

```text
final_score =
  0.65 × semantic_score (normalized)
+ 0.35 × bm25_score (normalized)
```

This provides **better relevance than either method alone**.

---

## 🌐 API Endpoints

### 🔹 Lexical Search

```http
POST /api/search/lexical
```

### 🔹 Semantic Search

```http
POST /api/search/semantic
```

### 🔹 Hybrid Search

```http
POST /api/search/hybrid
```

**Request**

```json
{
  "query": "hand bag",
  "top_k": 5
}
```

---

## ⚙️ Tech Stack

* **Python**
* **FastAPI**
* **FAISS**
* **Sentence Transformers**
* **BM25 (rank-bm25)**
* **Databricks + Spark**
* **Delta Lake**
* **Gemini (LLM evaluation)**

---

## 🧪 Evaluation Strategy

Since labeled relevance data is not available, evaluation is done using:

### 🧠 LLM-Based Judging (Gemini)

* Scores each system (1–5)
* Chooses the best system
* Provides reasoning

### 📊 Metrics Generated

* Win-rate per system
* Per-query scores
* Aggregated evaluation report

### 📁 Evaluation Outputs

```text
evaluation/
│
├── logs/
│   └── raw_evaluations.json
│
├── metrics/
│   └── win_rates.csv
│
└── report/
    └── evaluation_report.md
```

---

## 📈 Why Hybrid Search Wins

| Approach | Strengths        | Weaknesses                |
| -------- | ---------------- | ------------------------- |
| BM25     | Precise keywords | No semantic understanding |
| Semantic | Handles synonyms | Can return noisy results  |
| Hybrid   | Best of both     | Slightly more complex     |

Evaluation consistently shows **hybrid search outperforming** lexical-only and semantic-only systems.

---

## 🧠 Key Design Decisions

* Heavy processing done **offline in Databricks**
* Search APIs are **low-latency and in-memory**
* No Spark dependency in serving layer
* No globals in FastAPI (uses `lifespan`)
* Evaluation is **repeatable and automated**

---

## 📌 How to Run (Local)

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔮 Future Enhancements

* Learning-to-rank
* Query intent classification
* Clustering-based result diagnostics
* Online evaluation & A/B testing
* Category-aware hybrid weighting

---

## 🏁 Conclusion

This repository demonstrates how **modern search systems are actually built**:

* Not just embeddings
* Not just BM25
* But **hybrid, evaluated, and production-aware**

---
## 🌐 Connect
Built with ❤️ by 
**Vijay Kumar Saravanan**
<p align="left">
<a href="https://linkedin.com/in/https://www.linkedin.com/in/vijay-kumar-saravanan-71b8561a2/" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/linked-in-alt.svg" alt="https://www.linkedin.com/in/vijay-kumar-saravanan-71b8561a2/" height="30" width="40" /></a>
</p>
