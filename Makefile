PYTHON ?= python

.PHONY: download-data clean-data

download-data:
	$(PYTHON) src/download_data.py

clean-data:
	$(PYTHON) src/preprocessing/clean_data.py
