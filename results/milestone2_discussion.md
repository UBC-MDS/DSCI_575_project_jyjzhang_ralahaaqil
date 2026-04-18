# Milestone 2 Discussion

## Prompt Template Design

The primary test query used prompt testing (as seen in `results/milestone2_rag.ipynb`) is "game with pung and chow", referring to mahjong. This is used as it is a complex query that would be difficult to understand with just semantic or BM25 search

### Iteration 1

We first start with a slightly modified version of the provided example prompt in the milestone:

```
You are a helpful Amazon shopping assistant for software products.
Answer the question using ONLY the following context (real product reviews + metadata).
Always cite the product ASIN and title when possible.
```

We include additional context about being a shopping assistant for specifically software products, and also request that the output cites the title, which is more interpretable to the user than just the product ASIN. This results in the following output:

```
Based on the reviews provided, the game that involves **pung** (pong) and **chow** mechanics is:

**ASIN: B00HPOGTRC** (Mahjong game)

A reviewer specifically mentions these Mahjong terms: "when I had a calling hand and another player discard my winning tile, but another player had a pair, the **PONG** preceed my winning hand which is totally wrong. Same for **CHOW**." The review indicates this is a Mahjong game where players can call "Pong" (claiming a discard to make three identical tiles) and "Chow" (claiming a discard to complete a sequence), though the reviewer notes errors in how these mechanics are implemented in this particular version.
```

There are a few issues here; the response does not mention the average rating of the product and the ouput implies that it would not be able to correctly identify the game as mahjong if the review did not specifically include pong and chow as terms.

## Iteration 2

We adjust the prompt so that it also mentions the average rating. In addition, we inform the LLM that it is acceptable for it to use outside information to learn about unfamiliar concepts that can help support its interpretation of the query instead of only relying on reviews.

```
You are a helpful Amazon shopping assistant for software products.
You may use information from outside the given context to learn about concepts.
However, answer the question using ONLY the following context (real product reviews + metadata).
Always cite the product ASIN, title, and average rating when possible.
```

This results in the following output:

```
Based on the provided reviews, the game featuring **Pung** (spelled "PONG" in the review) and **Chow** mechanics is:

**ASIN:** B00HPOGTRC  
**Average Rating:** 3.6/5 (77 ratings)

The review for this product discusses Mahjong gameplay rules, specifically mentioning errors in how the game handles claiming tiles: *"when I had a calling hand and another player discard my winning tile, but another player had a pair, the PONG preceed my winning hand which is totally wrong. Same for CHOW. e.g.my opposite player discard my winning tile but my upper player can CHOW, the upper player took the tile."*

*(Note: The Title field was not provided in the metadata for this ASIN, but the review text identifies it as a Mahjong game.)*
```

One issue that we found was that the output was listing ASIN first, which is not as useful to the user as the title of the product. Another is that the output would either get sidetracked answering questions instead of recommended products for certain queries, or recommending far too many products. We addressed these in the final prompt that we decided to go with.

## Iteration 3 (Final)

```
You are a helpful Amazon shopping assistant for software products.
Use the provided context to recommend up to 3 relevant products.
You may use information from outside the given context to learn about concepts.
However, answer the question using ONLY the following context (real product reviews + metadata).
Always cite the product title, ASIN, and average rating when possible.
```

This resulted in the following output:

```
Based on the reviews provided, here is the relevant product featuring **Pung (Pong) and Chow** mechanics:

**1. Mahjong Game (ASIN: B00HPOGTRC)**  
- **Average Rating:** 3.6/5 (77 ratings)  
- **Details:** While the title is not specified in the provided context, the review explicitly confirms this is a **Mahjong** game that includes both **PUNG** (referenced as "PONG") and **CHOW** mechanics. The reviewer describes specific gameplay scenarios involving calling hands, winning tiles, and the rules governing when players can declare Pong or Chow on a discard—core mechanics of Mahjong. Note that the reviewer mentions rule implementation errors regarding priority between these calls and winning hands.

*Note: No other products in the provided context feature Pung and Chow as game mechanics; other mentions of "chow" refer to the dog breed or developer names, while "pong" references table tennis or character names.*
```

This results in more helpful output that explicitly comments on recommended products in a way that is intuitive to the person making the query.

## Model choice for the RAG pipeline

In the rag pipeline, the final language model selected for answer generation was `kimi-k2.5`. This choice was based on a practical comparison against Gemini 3 Flash and Gemma 4. All three models were able to answer questions from the retrieved review context, but Kimi produced the most consistently well-structured responses. Its answers were easier to read and better organized for a shopping-assistant style application.

Gemini Flash performed reasonably well and generated answers of similar overall quality, but its responses were not as consistently structured as Kimi's. Gemma 4 produced outputs that were also similar in quality to Gemini Flash, but inference time was noticeably slower. Gemma did not offer a clear quality advantage to justify the extra latency. Kimi was therefore the best tradeoff among the three models - it was faster than both Gemini Flash and Gemma 4 while also giving the most organized final responses.

Public documentation for the related K2 base model reports about 1 trillion total parameters with 32 billion active parameters per token, which helps explain its strong response quality while still keeping inference efficient through sparse activation. By contrast, Gemma 4 is offered in several smaller and mid-sized variants, ranging from effective 2B and 4B edge models up to 26B and 31B larger models, so it is generally more compact depending on the specific variant used. Gemini Flash is a closed model and Google does not publicly disclose its parameter count, but it is positioned as a speed-optimized model rather than a very large open-weight model.
