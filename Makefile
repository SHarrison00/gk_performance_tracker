.PHONY: help pipeline scrape load transform stage upload

help:
	@echo "Available targets:"
	@echo "  make pipeline  - Run full data pipeline (scrape → load → transform → stage → upload)"
	@echo "  make scrape    - Scrape raw matchlogs data"
	@echo "  make load      - Load raw data into DuckDB"
	@echo "  make transform - Run dbt transformations"
	@echo "  make stage     - Export curated tables to public/"
	@echo "  make upload    - Upload public/ data to S3"

pipeline:
	python -m scraping.cli --config scraping/config.yml
	python -m scripts.load_duckdb
	python -m scripts.run_dbt_build
	python -m scripts.stage_public_tables
	python -m scripts.upload_public_to_s3

scrape:
	python -m scraping.cli --config scraping/config.yml

load:
	python -m scripts.load_duckdb

transform:
	python -m scripts.run_dbt_build

stage:
	python -m scripts.stage_public_tables

upload:
	python -m scripts.upload_public_to_s3
