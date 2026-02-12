
# 🔍 Hybrid Search Evaluation Report

**Date:** 20260208_214402

## 📊 Win Rates
- Lexical (BM25): 0.00%
- Semantic (FAISS): 80.00%
- Hybrid: 20.00%

## 🧠 Observations
Hybrid search consistently balances exact keyword matching and semantic understanding,
leading to higher relevance across diverse queries.

## 📋 Sample Judgements

### Query: "hand bag"
- Lexical score: 1
- Semantic score: 3
- Hybrid score: 1
- Winner: **semantic**

Reasoning: Lexical results are completely empty, making them useless. Hybrid results are mostly irrelevant, consisting of cosmetic bags, toiletry bags, and specialized pouches, not general 'hand bags'. Semantic results, while containing some noise (e.g., 'Potato Chip Bag', 'Toiletry Bag'), are the only ones to return highly relevant items like 'Victoria's Secret Angel Black Handbag Tote Bag' and 'Bestpriceam Women's Tree of Life Printing Canvas Bags Shoulder Bag Zipper Casual Handbag', which directly match the user's intent.

### Query: "women leather purse"
- Lexical score: 1
- Semantic score: 3
- Hybrid score: 4
- Winner: **hybrid**

Reasoning: Lexical search provided no actual product information, rendering all results completely irrelevant. Semantic search returned some relevant 'purse' items, but also included irrelevant 'mens wallets' and 'pen wraps', and many 'makeup bags' which, while related, are not the primary intent of a 'purse' for money/cards. It also sometimes missed the 'leather' attribute. Hybrid search, despite some noise related to individual keywords (e.g., leather oil, perfume, leggings), offered the most directly relevant 'women leather purse' items in its results, demonstrating the best balance of relevance and query satisfaction.

### Query: "silicone cupping therapy"
- Lexical score: 1
- Semantic score: 5
- Hybrid score: 2
- Winner: **semantic**

Reasoning: Lexical results are empty, making them completely irrelevant and unusable. Hybrid results include only one relevant item, with the rest being unrelated silicone products (e.g., back scrubbers, bras, sponges, nose pads). Semantic results consistently return highly relevant "silicone cupping therapy" products, demonstrating the best understanding of the user's intent, with only one slightly off-topic item (ice roller) and one potentially non-silicone cupping set.
