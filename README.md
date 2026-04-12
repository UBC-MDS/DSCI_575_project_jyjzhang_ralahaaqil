# DSCI 575 Smart Amazon Product Query Assistant

## Dataset Description

## Data Processing

### Fields Used

### Preprocessing Steps

## Setup

### Cloning the Repository

Clone the repository and navigate to the project folder using the following commands:

```bash
git clone https://github.com/UBC-MDS/DSCI_575_project_jyjzhang_ralahaaqil.git
cd DSCI_575_project_jyjzhang_ralahaaqil
```

### Setting Up the Development Environment

Create the Conda environment with Make (if `575-project` already exists, creation is skipped):

```bash
make conda-env
```

The Makefile does not activate Conda in your current shell. Activate the environment before running other commands:

```bash
conda activate 575-project
```

Alternatively, create the environment manually:

```bash
conda env create -f environment.yml
conda activate 575-project
```

### Setting API Keys

Create a `.env` file with the following contents, filling in the ellipses with your corresponding tokens:

```
HF_TOKEN=...
ANTHROPIC_API_KEY=...  # Last milestone only
```

### Setting Up the Project

After activating `575-project`, you can run the full pipeline in one step with `make setup` (or `make setup-sample` to use a sample run for the semantic index - faster setup). The Makefile will handle downloading, cleaning, and indexing the data, and you can then run the web app with `make run-app`. You can also run the individual steps manually.

### Data Preparation

Download the data and process it using the following commands:

```bash
make download-data
make clean-data
```

### Creating Indices

Save the BM25 and semantic search indices locally using the following commands:

```bash
make bm25
make semantic
```

## Locally Running the App

With `575-project` activated, run the web app using:

```bash
make run-app
```

## Retrieval Workflows

The following steps can be used to run the retrieval workflows from the root directory. This returns a list of (Document, score) tuples for the queried items.

Run Python in the terminal using

```bash
python
```

### BM25 Search

Perform a BM25 search for a query using the following steps in Python:

```python
from src.bm25 import search

search(query, top_k=k)
```

Where `query` is the desired query string and `k` is the number of results to return.

### Semantic Search

Perform a semantic search for a query using the following steps in Python:

```python
from src.semantic import faiss_search

faiss_search(query, top_k=k)
```

Where `query` is the desired query string and `k` is the number of results to return.
