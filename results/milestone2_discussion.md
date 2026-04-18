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

## Evaluation

We will be rating on a scale of 1-5, with 5 being the best and 1 being the worst.

### Query 1: game with pung and chow

```
Based on your request for a game featuring **pung** (pong) and **chow** mechanics—specific terms from Mahjong—I found one relevant product in the provided context:

**ASIN:** B00HPOGTRC  
**Title:** [Title not specified in context; review indicates Mahjong game]  
**Average Rating:** 3.6/5 (77 ratings)

This appears to be a **Mahjong** game that specifically implements both **Pung (Pong)** and **Chow** mechanics. The customer review explicitly mentions gameplay involving these elements: *"when I had a calling hand and another player discard my winning tile, but another player had a pair, the PONG preceed my winning hand... Same for CHOW"* and describes scenarios involving claiming tiles for these combinations. Note that the reviewer indicates the game contains rule errors regarding the priority of these calls, but confirms these mechanics are central to the gameplay.

*No other products in the provided context specifically feature Mahjong-style pung and chow mechanics.*
```

| Dimension | What to assess |
|---|---|
| Accuracy | 5 |
| Completeness | 3 |
| Fluency | 4 |

The answer is factually correct; in that it returns Mahjong game. However, other Mahjong games that appear in the dataset are not mentioned.

### Query 2: how do I keep my computer safe

```
Based on the provided customer reviews and metadata, here are **3 recommended products** to keep your computer safe:

**1. ESET SMART Security** (ASIN: B01723PG10)  
*Average Rating: 4.3/5 (84 reviews)*  
This all-in-one Internet security software provides "excellent" protection without slowing down your computer. According to reviewers, it includes **automatic Banking and Payment Protection** for safe online transactions, **Anti-Theft features** to track and locate missing laptops, and technology that has earned more consecutive Virus Bulletin VB100 awards than any other vendor. Users report it runs "stealthily in the background" while keeping systems "safe, smooth and trouble free."

**2. Norton AntiVirus** (ASIN: B00FGDEFPC)  
*Average Rating: 3.8/5 (381 reviews)*  
Described as keeping "your PC safe from viruses, identity theft and social media dangers," this software ensures your virus protection is always up-to-date when you surf, shop, and bank online. Reviewers note it uses "exclusive, patented layers of protection" to block scam websites and suspicious social media content. One long-term user mentioned they "never suffered any real viruses" while running it, and recommends pairing it with a secondary free manual scanner for extra safety.

**3. Trend Micro Titanium Maximum Security 2012** (ASIN: B005AAWOT0)  
*Average Rating: 3.7/5 (186 reviews)*  
This all-in-one security solution uses **cloud technology to proactively stop viruses and spyware before they reach your computer**. It includes parental controls, data theft prevention to keep passwords and credit card numbers safe, a secure file shredder, and protection for smartphones/tablets. Reviewers appreciate that it provides "maximum protection for everything you do online" without the distracting alerts and pop-ups common with other security suites.

**Additional Safety Tips from the Reviews:**
- Keep antivirus and protection software up-to-date (ASIN: B0099PCQYK)
- Use strong password controls and consider a password manager like **PasswdSafe** (ASIN: B008K4WNRG, 3.4/5 rating) to securely store login credentials
- Maintain a secondary free scanner for occasional manual scans to catch anything your main antivirus might miss (as recommended in ASIN: B00N14IYUU)
```

| Dimension | What to assess |
|---|---|
| Accuracy | 5 |
| Completeness | 5 |
| Fluency | 3 |

The answer provides correctly provides antivirus/compute security software, with a helpful description of what each of them includes. Moreover, it provides additional safety tips that help further answer the question. However, it has a tendency to refer to products by the ASIN instead of their name, which makes it difficult to interpret for the user.

### Query 3: good application for taking notes on physics

```
Based on the context provided, here are the top recommendations for note-taking applications suitable for physics:

**1. LectureNotes (ASIN: B00CPR42EG)**
- **Average Rating:** 3.3/5 (161 reviews)
- **Why it's good for physics:** This app is specifically praised by students in technical courses. One reviewer noted using it for "three graduate level chemistry courses," highlighting its ability to handle complex scientific notation and math equations. It features smooth handwriting with stylus support (essential for physics equations), palm rejection, PDF import capability for lecture slides, and continuous page view. The app allows you to "write freestyle on top of imported PDF notes" and supports pressure sensitivity for detailed sketching of diagrams.

**2. Note Everything (ASIN: B004V4S54E)**
- **Average Rating:** 3.6/5 (367 reviews)
- **Why it's good for physics:** This versatile app offers multiple note types including text, voice memos, and PaintNotes for hand-drawn diagrams (useful for sketching physics concepts like force diagrams or circuits). Reviewers praise its organizational features with folders/subfolders and automatic saving. One user noted it's "great for school and taking notes" with the ability to handle "labs" and complex organizational needs.

**3. Quick Notes (ASIN: B0098TQD14)**
- **Average Rating:** 3.0/5 (73 reviews)
- **Why it's good for physics:** A simpler option for straightforward physics note-taking. It offers color-coded organization for different topics (e.g., mechanics, thermodynamics), basic handwriting support, and works offline without requiring cloud connectivity. While less feature-rich than the others, reviewers find it "easy to use" for jotting down quick formulas and concepts during lectures.

*Note: While products like "Physics: Motion" (B004XJE1RC) exist in the catalog, those are physics learning/reference tools rather than note-taking applications.*
```

| Dimension | What to assess |
|---|---|
| Accuracy | 4 |
| Completeness | 5 |
| Fluency | 4 |

The answer correctly recommends notes apps, with third bullet point for each recommendation specifically mentioning why it is good for physics. However, some the of explanations are not particularly relevant to physics only, though they are still potentially useful features of the software to mention.

### Query 4: navigation app with real time traffic updates

```
Based on your request for a navigation app with real-time traffic updates, here are the top 3 recommendations from the available context:

**1. Google Maps**  
- **ASIN:** B00SZFFC2I  
- **Average Rating:** 4.1/5 (6,105 ratings)  
- **Why it's recommended:** This app offers powerful live traffic updates that show accidents, lane closures, and incidents in real-time. It provides accurate turn-by-turn navigation that rivals expensive GPS systems like Garmin or TomTom, and most users now prefer it over separate GPS devices.

**2. My Route Planner: Travel Assistant & Free GPS Maps**  
- **ASIN:** B0829XWJCY  
- **Average Rating:** 3.5/5 (2,009 ratings)  
- **Why it's recommended:** Features a real-time traffic map that helps you draw fast routes and avoid congestion. It includes live voice alerts, voice navigation, and real-time weather forecasts to help plan your journey effectively.

**3. GPS Navigation Tracker - Free Route Finder**  
- **ASIN:** B076F7L8MD  
- **Average Rating:** 3.4/5 (70 ratings)  
- **Why it's recommended:** Provides real-time traffic updates to help prevent traffic jams, along with real-time path sharing so you can share your planned route, estimated arrival time, and current location with others. It also includes lane assistance and junction view for safer navigation.

**Note:** Some users reported that certain navigation apps (including options 2 and 3 above) may have compatibility issues with Kindle Fire tablets that lack dedicated GPS chips, so please verify your device's GPS capabilities before downloading.
```

| Dimension | What to assess |
|---|---|
| Accuracy | 5 |
| Completeness | 5 |
| Fluency | 5 |

The answer correctly provides navigation apps with real time traffic updates, with useful information on the features of each one. It also comments on the possible compatibility issues with Kindle Fire tablets, which is useful information. This particular answer also has very concise description of each product.

### Query 5: what is the best source of information on AI

```
Based on the provided context, there are no dedicated educational resources or books about Artificial Intelligence theory. Instead, the available products are **apps and games that implement AI features** (opponents, pattern recognition, or adaptive algorithms). 

Here are the top 3 relevant products from the context that utilize AI technology:

**1. Mood & Journal Tracker with Pattern Recognition AI**
- **ASIN:** B06VVPZB6S
- **Average Rating:** 3.3/5 (30 ratings)
- **AI Application:** Uses Artificial Intelligence to identify "new and emerging patterns" in your daily mood and activities, helping you recognize habits and build new ones through statistical analysis.

**2. Transport Tycoon**
- **ASIN:** B00FK916SG
- **Average Rating:** 3.9/5 (116 ratings)
- **AI Application:** Features "advanced A.I.-driven competitor's companies" that you compete against in building transport empires. Reviews detail extensive AI behavior analysis (e.g., vehicle pathfinding, competitor decision-making), though some note the AI has limitations with train routing and vehicle replacement logic.

**3. Tic Tac Toe Game Free**
- **ASIN:** B00NK0EDCS
- **Average Rating:** 3.6/5 (21 ratings)
- **AI Application:** Features an adaptive AI that "adapts to your play style and is highly unpredictable" with adjustable difficulty levels that can be changed mid-game.

*Note: The context also includes an American Idol fan app (ASIN B006T2OB8A), but reviews indicate it is an unofficial app that frequently malfunctions and does not provide reliable information.*
```

| Dimension | What to assess |
|---|---|
| Accuracy | 1 |
| Completeness | 3 |
| Fluency | 5 |

The answer does not include any relevant suggestions; this is likely due to the semantic and BM25 searches being unable to pick up any relevant documents related to information on AI. However, it is aware of the fact that the user is looking for educational resources on AI, and makes an attempt to recommend products related to AI with descriptions of what each of them does.

### Overall Conclusion

Overall, the RAG workflow is performing decently. It is able to consistently identify what the query is specifying, although it sometimes struggles with identifying relevant products, likely due to limitations of the hybrid search itself. Answers reliably list each recommended product and their relevant details, and also occasionally include pertinent background information that can either answer the question more fully or provide more general comments on its recommendations. The workflow occasionally struggles with being readable; it often includes information on reviews in the general app description, when it would likely be more intuitive if it was listed in a separate bullet point. It also sometimes fails to list the name of a mentioned product, listing the ASIN instead.

One limitation of the RAG workflow is that the answers are formatted inconsistently; it mixes reviews with general app information, and has a tendency to list the ASIN instead of the product name. This can be improved by provided an output schema for the LLM to strictly follow. Another limitation is that the BM25 and semantic searches are not always able to capture the most relevant products; this is most apparent in query 1, where it returned only one mahjong game when there are multiple mahjong games in the dataset (this is even more apparent in the unchunked version, where it is unable to identify any mahjong games at all). A possible way to improve this would be to adjust the weighting between the BM25 and semantic searched; other possible solutions could include tuning how the documents are chunked, or allowing the LLM to expand on the user query before using it to run the hybrid search.
