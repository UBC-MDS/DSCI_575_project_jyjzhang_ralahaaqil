PYTHON ?= python

.PHONY: download-data

download-data:
	$(PYTHON) src/download_data.py
