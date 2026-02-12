
# 🔍 Hybrid Search Evaluation Report

**Date:** 20260208_205405

## 📊 Win Rates
- Lexical (BM25): 0.00%
- Semantic (FAISS): 100.00%
- Hybrid: 0.00%

## 🧠 Observations
Hybrid search consistently balances exact keyword matching and semantic understanding,
leading to higher relevance across diverse queries.

## 📋 Sample Judgements

### Query: "hand bag"
- Lexical score: 1
- Semantic score: 3
- Hybrid score: 1
- Winner: **semantic**

Reasoning: Lexical results were completely empty, rendering them unusable. Hybrid results were mostly irrelevant, consisting of various utility bags, pouches, and even bottles, with almost no items matching the 'hand bag' query. Semantic results, despite containing some noise like toiletry bags and a 'potato chip bag pouch', successfully retrieved directly relevant items such as 'Victoria's Secret Angel Black Handbag Tote Bag' and 'Women's Tree of Life Printing Canvas Bags Shoulder Bag Zipper Casual Handbag'. This makes semantic the clear winner as it was the only system to provide truly relevant products.

### Query: "women leather purse"
- Lexical score: 1
- Semantic score: 3
- Hybrid score: 2
- Winner: **semantic**

Reasoning: Lexical results were completely irrelevant, returning only 'All Beauty' items with no product titles. Semantic results, while containing some noise like men's wallets and makeup bags, generally stayed within the broader category of small bags and wallets, and included several relevant 'coin purses' and 'lady' bags. Hybrid results had a few highly relevant items that perfectly matched 'women leather purse,' but were severely diluted by a large number of completely irrelevant product types such as leggings, fragrance, leather oil, manicure sets, and toiletry bags. The high volume of out-of-category noise in Hybrid makes Semantic the better system overall due to its greater consistency in returning items within the expected product domain.

### Query: "silicone cupping therapy"
- Lexical score: 1
- Semantic score: 5
- Hybrid score: 1
- Winner: **semantic**

Reasoning: The user query is 'silicone cupping therapy'. Lexical results are completely empty, indicating a critical failure. Hybrid results are largely irrelevant, containing many silicone products that are not related to cupping therapy (e.g., silicone bras, back scrubbers). Semantic results, however, are highly relevant, featuring multiple 'silicone cupping therapy' sets, massage cups, and related products for both body and face. The semantic system clearly understands the intent much better than the other two.
