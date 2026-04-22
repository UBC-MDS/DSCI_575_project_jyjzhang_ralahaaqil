PYTHON ?= python

.PHONY: download-data clean-data bm25 bm25-sample semantic semantic-sample run-app conda-env all all-sample setup setup-sample

setup: download-data clean-data bm25 semantic

setup-sample: download-data clean-data bm25-sample semantic-sample

conda-env:
	@if conda env list | awk '$$1 == "575-project" {found=1} END {exit !found}'; then \
		echo "Conda env 575-project already exists; skipping conda env create."; \
		echo "Run `conda activate 575-project` before proceeding."; \
	else \
		conda env create -f environment.yml; \
		echo "Run `conda activate 575-project` before proceeding."; \
	fi

download-data:
	$(PYTHON) src/download_data.py

clean-data:
	$(PYTHON) src/preprocessing/clean_data.py

bm25:
	$(PYTHON) -m src.bm25

bm25-sample:
	$(PYTHON) -m src.bm25 --sample

semantic:
	$(PYTHON) -m src.semantic

semantic-sample:
	$(PYTHON) -m src.semantic --sample

run-app:
	$(PYTHON) -m streamlit run app/app.py
