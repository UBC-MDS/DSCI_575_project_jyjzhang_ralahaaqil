# Milestone 1 Discussion

Note that we have the full query search results in `results/query_results.ipynb`.

## Individual Query Comparison

### Easy Query: "language learning software"

We have the following results from the query "language learning software", which is designed to be an easy keyword-based query:

BM25:
    Instant Immersion German Deluxe v3.0
    Instant Immersion English Deluxe v3.0
    Tell Me More Spanish Premium Version 7 [Old Version]
    Instant Immersion French Deluxe v3.0
    Instant Immersion Italian Deluxe v3.0
Semantic:
    Rosetta Stone Spanish (Spain) Level 1-2 Set
    Tell Me More v10 German - 10 Levels
    Rosetta Stone V2: Polish, Level 1
    EuroTalk Interactive - Talk Now! Learn Russian
    Rosetta Stone: Latin Explorer

Overall, both methods were able to return software related to learning languages. However, the results for the BM25 approach appear more uniform, with most of them being dominated by some version of Instant Immersion v3.0. The semantic search, on the other hand, has slightly more varied results.

### Easy Query: "Google Maps"

We have the following results from the query "Google Maps", which is designed to be an easy keyword-based query:

BM25:
    Maps For Google
    Tamriel Maps
    MapPad Pro - Measure Area or Distance using GPS or Map
    Google Maps
    Android Delete History
Semantic:
    GMap Demo by AppLaud
    iOffMap
    Helsinki, Finland Offline Map: PLACE STARS
    GPS Maps Navigation and Transport
    GPS Maps

While both methods returned maps related software, only BM25 was able to return the desired results of Google Maps software specifically. However, BM25 also returns items such as Android Delete History, which is not relevant to the search and likely only appears due to it mentioning Google Maps in its description.

### Medium Query: "app for navigating cities"

We have the following results from the query "app for navigating cities", which is designed to be an medium semantic-based query:

BM25:
    iOffMap
    GPS Maps
    BackPage Cruiser: Free Classifieds App
    Italy offline map and guide (Free edition)
    weather(unofficial)
Semantic:
    Microsoft AutoRoute Europe 2007 [Old Version]
    Russian Topo Maps PRO
    Dallas, TX, USA GPS Navigator: PLACE STARS
    Offline Map Barcelona, Spain - CNM
    Washington DC Meto for Kindle Fire

Semantic search performed better here, returning results that are consistently related to navigation. BM25 struggled more; while it does have some navigation related software, it also includes both a classifieds and a weather app, none of which are relevant here.

### Medium Query: "learn about the latest tech innovations"

We have the following results from the query "learn about the latest tech innovations", which is designed to be an medium semantic-based query:

BM25:
    Fast Company Network
    New Ubuntu Linux Desktop 20.10 Official 64-bit Groovy Gorilla
    Adobe Acrobat Pro 2017 | PC Disc
    UWTV
    EYES IN(Kindle Tablet Edition)
Semantic:
    The TECH Show
    Currently Tech News
    Inventor Labs - Technology
    Gadget Guru
    Inventions and Gadgets

Semantic search performed better here, returning the desired software related to tech news. BM25 struggled much more; while results such as Fast Company Network do provide tech news, there are also completely unrelated results such as Adobe Acrobat Pro 2017 | PC Disc. On the other hand, the semantic search consistently returns topics associated with tech innovations.

### Complex Query: "game with pung and chow"

We have the following results from the query "game with pung and chow"", which is designed to be a complex query. In particular, it refers to the game of mahjong, which involves calling using the words pung and chow.

BM25:
    Chow Chow Spa Salon
    Downhill Moutain Biking Game
    Voicent AgentDialer Pro 8 [Download]
    Shark Island Frenzy
    War of Jungle King : Lion Sim
Semantic:
    Pony Simulator
    Russian Poolette
    Slots Inca - Free Casino Slot Machine Games
    Little Pony ZigZag
    Pocmon FPV

Neither of the methods performed well here; both successfully return results that are games, but none of them are related to mahjong. The closest 'correct' answer would be Chow Chow Spa Salon from the BM25 search, which is not related to mahjong but does include the word 'chow'.

## Overall Findings

Generally, BM25 search excels when the queries contain explicit keywords that match up with the text related to the app; for example, when the name of the software is explicitly searched for. However, it has much more difficulty searching for semantic-based queries, and will often return unrelated items that might briefly mention the same keywords in the description.

 Meanwhile, the semantic search works well in cases where the query describes the item in a way semantically similar to the text. When using keyword-based queries, it generally returns the right category of software, but not the specific desired software.

 Both methods struggle with more complex queries that might require outside information, such as in the case where we try the query "game with pung and chow" to describe mahjong. This is where RAG might help, since it would allow us to provide additional context that could inform the search that mahjong is a game where players call 'pung' and 'chow'.

 One thing to notes is that while the top results are generally somewhat related to the query, above observations notwithstanding, the searches often return outdated software that is not necessarily useful for the user. Results often explicitly say '[Old Version]', when the user would likely prefer the new version as a top result instead. Therefore, it may make sense to incorporate additional information such as the recency of the software when performing the search.
 