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

Create and activate the development environment using the `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate 575-project
```

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

Run the web app using the following command:

```bash
make run-app
```

## Retrieval Workflows

### BM25 Search

### Semantic Search

