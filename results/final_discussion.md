# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling

Our pipeline already processes 84,804 products. Therefore, no changes to the sampling strategy have been made.

### LLM Experiment

#### Models Used

We compared our current model, `kimi-k2.5` (family Kimi, size of 1T parameters) to `gemini-3-flash-preview` (family Gemini 3, unknown size since Gemini generally doesn't disclose it). 

#### Prompt

We used the following prompt:

```
You are a helpful Amazon shopping assistant for software products.
Use the provided context to recommend up to 3 relevant products.
You may use information from outside the given context to learn about concepts.
However, answer the question using ONLY the following context (real product reviews + metadata).
Always cite the product title, ASIN, and average rating when possible.
```

#### Outputs

`kimi-k2.5`:

```
Query: game with pung and chow
Based on your request for a game featuring **pung** (pong) and **chow** mechanics—specific terms from Mahjong—I found one relevant product in the provided context:

**ASIN:** B00HPOGTRC  
**Title:** [Title not specified in context; review indicates Mahjong game]  
**Average Rating:** 3.6/5 (77 ratings)

This appears to be a **Mahjong** game that specifically implements both **Pung (Pong)** and **Chow** mechanics. The customer review explicitly mentions gameplay involving these elements: *"when I had a calling hand and another player discard my winning tile, but another player had a pair, the PONG preceed my winning hand... Same for CHOW"* and describes scenarios involving claiming tiles for these combinations. Note that the reviewer indicates the game contains rule errors regarding the priority of these calls, but confirms these mechanics are central to the gameplay.

*No other products in the provided context specifically feature Mahjong-style pung and chow mechanics.*

Query: how do I keep my computer safe
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

Query: good application for taking notes on physics
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

Query: navigation app with real time traffic updates
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

Query: what is the best source of information on AI
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


`gemini-3-flash-preview`:

```
Query: game with pung and chow
Based on the provided product reviews and metadata, here are the most relevant games that include "pong" (or "pung") and "chow" mechanics or terminology:

1.  **Mahjong (Title Not Provided)**
    *   **ASIN:** B00HPOGTRC
    *   **Average Rating:** 3.6/5
    *   **Description:** This game is specifically identified by a reviewer as a Mahjong game ("love Mahjon"). The review explicitly mentions game mechanics involving **"PONG"** and **"CHOW,"** which are standard moves in Mahjong. The reviewer notes some technical errors regarding how the program prioritizes these moves during gameplay.

2.  **iFunSoft Shark Island Frenzy**
    *   **ASIN:** B00MHE33TW
    *   **Average Rating:** 3.5/5
    *   **Description:** While not a Mahjong game, this title uses the term "chow" as its primary gameplay mechanic. Players control a fish (starting as an Orville the Orca) and must **"chow down on fish smaller than you"** to grow and survive through 44 levels of increasing difficulty.

3.  **Classic Ping Pong Game (Title Not Provided)**
    *   **ASIN:** B005XQLBU4
    *   **Average Rating:** 3.5/5
    *   **Description:** This game is described as a "classic game" and a "big waste of time" by different reviewers. It is relevant because the review text includes the keywords **"pong pong ping pong,"** indicating it is a table tennis or "Pong"-style digital game focused on hand-eye coordination.

Query: how do I keep my computer safe
Based on the provided software reviews and metadata, you can keep your computer safe by using comprehensive security suites that offer multi-layered protection, managing your passwords securely, and following safe browsing habits. 

Here are three relevant products to help protect your computer:

1.  **ESET SMART Security 3U 1Y 2016 (ASIN: B01723PG10, Average Rating: 4.3/5)**
    This is an "all-in-one" security suite highly recommended by IT professionals for its ability to recognize patterns in spam and phishing. It includes anti-theft tracking for missing laptops, banking and payment protection, and a secured environment for visiting financial sites. Users appreciate that it runs "stealthily in the background" without slowing down the computer.

2.  **Norton AntiVirus - 1PC – 1 Year Subscription - Instant Download - 2019 ready (ASIN: B00FGDEFPC, Average Rating: 3.8/5)**
    This software uses patented layers of protection to block viruses, identity theft, and social media dangers. It is designed to be "not very intrusive" and provides tools to help you monitor the condition and performance of your computer. One user recommendation suggests that when installing, you should uninstall any previous versions and use a removal tool to ensure a smooth setup.

3.  **Trend Micro Titanium Maximum Security 2012 - 3 Users (ASIN: B005AAWOT0, Average Rating: 3.7/5)**
    This solution uses cloud technology to proactively stop threats before they reach your machine. It includes several specialized tools for safety:
    *   **Trend Micro Vault:** A password-protected folder to safeguard sensitive files.
    *   **Secure Erase:** A file shredder that overwrites deleted data so it cannot be retrieved.
    *   **Parental Controls:** Tools to limit internet time and restrict inappropriate content.

**Additional Tips for Computer Safety from the Context:**
*   **Use a Standard Account:** For daily internet access, use a "Standard Account" rather than an "Administrator Account" to make it harder for Trojans and viruses to gain control of your system (ASIN: B005AAWOT0).
*   **Secure Your Passwords:** Use a tool like **PasswdSafe - Password Safe (ASIN: B008K4WNRG, Average Rating: 3.4/5)** to generate strong, random passwords. This allows you to use complex login credentials without having to memorize them all.
*   **Layered Defense:** Keep your antivirus and protection software up to date and sit behind a firewall with strong password controls (ASIN: B0099PCQYK). Some users also recommend occasionally running a second "manual scan" with a different free tool to catch anything your main scanner might miss (ASIN: B00N14IYUU).

Query: good application for taking notes on physics
Based on the provided context, here are three recommended applications for taking or referencing physics notes:

1. **LectureNotes (ASIN: B00CPR42EG)**
   * **Average Rating:** 3.3/5
   * **Description:** This application is highly recommended for students in technical fields. Reviewers note that it is "good for math equations" and can be used to keep up with notes in "graduate level chemistry courses." It is designed for handwriting with a stylus and allows users to import PDFs and images, making it a versatile tool for "handwriting class notes" or sketching diagrams.

2. **Physics: Motion (ASIN: B004XJE1RC)**
   * **Average Rating:** 3.3/5
   * **Description:** This app focuses on the "essentials of motion," including velocity, acceleration, and projectile motion. While one reviewer noted it may not be detailed enough for a calculus-based college course, it is recommended for "those starting physics" or "taking a standardized test." It helps users review essential questions and provides instant access to related internet resources if they get stumped.

3. **Physics Reference (ASIN: B007AHPIKS)**
   * **Average Rating:** 3.9/5
   * **Description:** This is a "quick reference to common physics problems/equations." It is described as a functional "reference arsenal" that covers most fundamental principles. Reviewers find it useful for looking up various physics terms and equations quickly, though it is intended as a reference rather than a comprehensive primer.

Query: navigation app with real time traffic updates
Based on the provided context, here are the top recommendations for navigation apps with real-time traffic updates:

1. **Product ASIN: B00SZFFC2I**
   * **Title:** (Title not provided in context)
   * **Average Rating:** 4.1/5
   * **Description:** This app provides "extremely powerful" live traffic updates that allow users to see accidents, lane closures, and incidents in real-time. Reviewers note that its turn-by-turn navigation is highly accurate and performs better than many expensive GPS systems.

2. **My Route Planner: Travel Assistant & Free GPS Maps (ASIN: B0829XWJCY)**
   * **Average Rating:** 3.5/5
   * **Description:** This travel assistant includes a real-time traffic map that helps users draw fast routes and find short driving paths. It features voice navigation, live voice alerts for distance and estimated time, and a GPS speedometer.

3. **Live GPS Maps 2019 - GPS Navigation Driving Guide (ASIN: B07MW1T79L)**
   * **Average Rating:** 3.5/5
   * **Description:** This app features a specific "traffic updates module" designed to keep users 100% updated on road conditions. It helps drivers identify clear routes to avoid the busiest road maps and provides a route planner for multi-stop journeys.

**Note:** If you are using an Amazon Fire tablet, several reviews for these apps (particularly ASIN B0829XWJCY) mention that the device must have a built-in GPS chip for the navigation features to work correctly, as many Fire tablets rely on Wi-Fi/cellular location instead.

Query: what is the best source of information on AI
Based on the provided context, the best sources of information regarding "AI" (which is used to refer to both Artificial Intelligence and the television show *American Idol*) are:

1.  **American Idol Fan App (ASIN: B006T2OB8A)**
    *   **Average Rating:** 3.7/5
    *   **Description:** This application is explicitly described as the "ultimate source of news and info" for the FOX reality show often referred to by reviewers as "AI." It provides news, pictures, video clips of contestants and judges, and a show episode guide. 

2.  **ASIN: B06VVPZB6S**
    *   **Average Rating:** 3.3/5
    *   **Description:** This product uses Artificial Intelligence (AI) to provide "useful statistics" that can "identify new and emerging patterns in life." It is designed to track daily moods and activities intelligently to help users find patterns and build new habits.

3.  **Tic Tac Toe Game Free (ASIN: B00NK0EDCS)**
    *   **Average Rating:** 3.6/5
    *   **Description:** For those seeking information on how AI behaves and adapts, this game features an AI described as "one of the best you will see." The software provides a fresh experience by adapting to the user's specific play style, making it highly unpredictable.
```

#### Key Observations

One observation is that the `kimi-k2.5` model automatically includes the number of reviews for each app, while the `gemini-3-flash-preview` model does not (though this can likely be fixed by just including it in the prompt). Another is that the Gemini model tends to include the full name of the app, including the version number, where the Kimi model tends to shorten down product titles if they are long and include extraneous information about the version (such as 'Norton AntiVirus - 1PC – 1 Year Subscription - Instant Download - 2019 ready' as opposed to just 'Norton AntiVirus'). They also have somewhat different priorities for certain queries; in the case of the query 'game with pung and chow', the Gemini model recommends an assortment of software the use 'pung', 'pong', or 'chow' in the description, while the Kimi model focuses on just Mahjong related software. For the query 'good application for taking notes on physics', the Kimi model tends to focus more on the notes aspect, while the Gemini model tends to focus more on the physics aspect. Another main difference is that the Gemini model tends to use a standard 'Description' label to elaborate on product information, while the Kimi model uses a custom label regarding the question (for example, 'Why it's good for physics'). However, the two models still provide very similar information overall; the descriptions usually have similar main points, and both models include similar extra notes in the case of queries 'how do I keep my computer safe' and 'navigation app with real time traffic updates'.

Both models are fairly similar overall, and a lot of the differences come down more to personal preference. In this case, we will stick with the existing `kimi-k2.5` model; its willingness to make certain assumptions about the query (for example, mahjong for 'game with pung and chow' and artifical intelligence for 'AI') makes its recommendations more focused, and a user can always follow up on the query if they do want something different (for example, a game including 'chow' as in food, or 'AI' as in American Idol).

**NOTE:** While in the process of completing this milestone, we found `kimi-k2.5:cloud` is no longer accessible through the Ollama API without a subscription due to Kimi releasing a new model on April 20. Therefore, we have switched to our alternative model, `gemini-3-flash-preview:cloud`.

## Step 2: Additional Feature (App Deployment)

### What You Implemented
- Uploaded the raw and processed data, the bm25 pickle file and the faiss vector index to S3 (obtained from sample data)
- Updated the app to fetch the required data from S3 if it doesn't exist on the machine (requirement for deploying to Streamlit Community Cloud)
- Deployed the application to Streamlit Communit Cloud

### Issues Faced
- OOM crashes when using the pickle file and vector index generated by the entire dataset instead of the sample due to Streamlit Community Cloud's compute constraints

### Deployment
The deployment can be found [here](https://575-proj.streamlit.app/)

Note that this deployment uses a sample of the full dataset due to compute constraints with Streamlit community cloud.
  
## Step 3: Improve Documentation and Code Quality

### Documentation Update

- Additional instructions on how to run the app using indices created from a subset of the data, downloaded from S3.
- Added link to deployed streamlit app.

### Code Quality Changes

We added missing docstrings to functions in our code files: specifically, `app/app.py`, `src/download_data.py`, `src/hybrid.py`, `src/preprocessing/clean_data.py`, `src/rag_pipeline.py`, and `src/semantic.py`. All other requirements were already fulfilled.

## Step 4: Cloud Deployment Plan

Assuming deployment on AWS, we will store the raw data, processed data, vector index, and BM25 index in S3; Spark can be used to clean, chunk, and then create the embeddings for each document from the raw data. The Streamlit app can be deployed on an EC2 instance. The app will be able to handle concurrent users, and we can avoid loading the indices separately for each user session by loading them into memory and reusing them for each subsequent session. The LLM inference can be handled through an Ollama API like it currently is. New products can be incorporated in production by using a pipeline that triggers whenever new data is added to S3; Spark can be used to clean, chunk, and create the embeddings for the data, then rebuild the BM25 and vector indexes. In the interest of cost, it would likely be best to batch these updates instead of updating every time a new review is added. The pipeline can then switch over to the new indices, allowing it to stay up to date.
