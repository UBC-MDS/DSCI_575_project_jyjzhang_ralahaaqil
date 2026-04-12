PYTHON ?= python

.PHONY: download-data clean-data bm25 bm25-sample

download-data:
	$(PYTHON) src/download_data.py

clean-data:
	$(PYTHON) src/preprocessing/clean_data.py

bm25:
	$(PYTHON) -m src.bm25

bm25-sample:
	$(PYTHON) -m src.bm25 --sample
