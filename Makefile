PYTHON ?= python

.PHONY: download-data clean-data bm25 run-app

download-data:
	$(PYTHON) src/download_data.py

clean-data:
	$(PYTHON) src/preprocessing/clean_data.py

bm25:
	$(PYTHON) -m src.bm25

run-app:
	$(PYTHON) -m streamlit run app/app.py
