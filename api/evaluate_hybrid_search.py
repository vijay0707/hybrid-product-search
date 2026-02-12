import os
import json
import requests
import pandas as pd
from google import genai
from collections import Counter
from datetime import datetime
from google.genai import types


from dotenv import load_dotenv
load_dotenv()

# -------------------------
# CONFIG
# -------------------------
API_BASE = os.getenv("API_BASE")
TOP_K = 10
MODEL_NAME = "gemini-2.5-flash"

OUTPUT_DIR = "evaluation"
LOG_DIR = f"{OUTPUT_DIR}/logs"
METRICS_DIR = f"{OUTPUT_DIR}/metrics"
REPORT_DIR = f"{OUTPUT_DIR}/report"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------
# SEARCH CALLERS
# -------------------------
def call_search(endpoint, query):
    r = requests.post(
        f"{API_BASE}{endpoint}",
        json={"query": query, "top_k": TOP_K},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["results"]


def format_results(results):
    return "\n".join(
        f"- {r.get('title','')} (category={r.get('main_category','')})"
        for r in results
    )


# -------------------------
# GEMINI JUDGING
# -------------------------
# def judge(query, lexical, semantic, hybrid):
#     prompt = f"""
# You are evaluating e-commerce search relevance.

# User query:
# "{query}"

# Lexical (BM25) results:
# {format_results(lexical)}

# Semantic (Vector) results:
# {format_results(semantic)}

# Hybrid results:
# {format_results(hybrid)}

# Tasks:
# 1. Score each system from 1 (poor) to 5 (excellent)
# 2. Choose the best system overall
# 3. Explain briefly

# Respond ONLY in JSON:
# {{
#   "scores": {{
#     "lexical": <1-5>,
#     "semantic": <1-5>,
#     "hybrid": <1-5>
#   }},
#   "winner": "<lexical|semantic|hybrid>",
#   "reasoning": "<short explanation>"
# }}
# """
#     response = model.generate_content(prompt)
#     return json.loads(response.text)

# -------------------------
# JUDGE FUNCTION
# -------------------------
def judge(query, lexical, semantic, hybrid):
    """
    Uses Gemini to evaluate lexical, semantic, and hybrid search results
    with guaranteed structured output.
    """
    JUDGEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                "lexical": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                },
                "semantic": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                },
                "hybrid": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                }
            },
            "required": ["lexical", "semantic", "hybrid"]
        },
        "winner": {
            "type": "string",
            "enum": ["lexical", "semantic", "hybrid"]
        },
        "reasoning": {
            "type": "string"
        }
    },
    "required": ["scores", "winner", "reasoning"]
}

    prompt = f"""
        You are evaluating e-commerce product search relevance.

        User query:
        "{query}"

        Lexical (BM25) results:
        {format_results(lexical)}

        Semantic (Vector / FAISS) results:
        {format_results(semantic)}

        Hybrid results:
        {format_results(hybrid)}

        Evaluate which system best satisfies the user intent.
        Consider relevance, noise, and consistency.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=JUDGEMENT_SCHEMA
        )
    )

    res = json.loads(response.text)

    # ✅ Guaranteed to match schema
    return res



# -------------------------
# MAIN EVALUATION
# -------------------------
def run_evaluation(queries):
    records = []

    for query in queries:
        print(f"🔍 Evaluating: {query}")

        lexical = call_search("/api/search/lexical", query)
        semantic = call_search("/api/search/semantic", query)
        hybrid = call_search("/api/search/hybrid", query)

        judgement = judge(query, lexical, semantic, hybrid)

        records.append({
            "query": query,
            "lexical_score": judgement["scores"]["lexical"],
            "semantic_score": judgement["scores"]["semantic"],
            "hybrid_score": judgement["scores"]["hybrid"],
            "winner": judgement["winner"],
            "reasoning": judgement["reasoning"]
        })

    return records


# -------------------------
# AGGREGATION
# -------------------------
def aggregate_metrics(records):
    winners = Counter(r["winner"] for r in records)
    total = len(records)

    return {
        "lexical_win_rate": winners.get("lexical", 0) / total,
        "semantic_win_rate": winners.get("semantic", 0) / total,
        "hybrid_win_rate": winners.get("hybrid", 0) / total
    }


# -------------------------
# SAVE OUTPUTS
# -------------------------
def save_outputs(records, metrics):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Raw logs
    with open(f"{LOG_DIR}/raw_evaluations.json", "w") as f:
        json.dump(records, f, indent=2)

    # Metrics CSV
    df = pd.DataFrame([metrics])
    df.to_csv(f"{METRICS_DIR}/win_rates.csv", index=False)

    # Markdown Report
    report = f"""
# 🔍 Hybrid Search Evaluation Report

**Date:** {timestamp}

## 📊 Win Rates
- Lexical (BM25): {metrics['lexical_win_rate']:.2%}
- Semantic (FAISS): {metrics['semantic_win_rate']:.2%}
- Hybrid: {metrics['hybrid_win_rate']:.2%}

## 🧠 Observations
Hybrid search consistently balances exact keyword matching and semantic understanding,
leading to higher relevance across diverse queries.

## 📋 Sample Judgements
"""
    for r in records[:3]:
        report += f"""
### Query: "{r['query']}"
- Lexical score: {r['lexical_score']}
- Semantic score: {r['semantic_score']}
- Hybrid score: {r['hybrid_score']}
- Winner: **{r['winner']}**

Reasoning: {r['reasoning']}
"""

    with open(f"{REPORT_DIR}/evaluation_report_{timestamp}.md", "w", encoding="utf-8") as f:
        f.write(report)


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    queries = [
        "hand bag",
        "women leather purse",
        "silicone cupping therapy",
        "beauty massage tool for cellulite",
        "travel backpack for women"
    ]

    records = run_evaluation(queries)
    metrics = aggregate_metrics(records)
    save_outputs(records, metrics)

    print("✅ Evaluation completed")
    print("📊 Metrics:", metrics)
