# Goalkeeper Performance Tracker

An end-to-end analytics platform to analyse the performance of goalkeepers in the English Premier League — built for fun and inspired by my passion for both goalkeeping and data engineering.

## Project Objective

In one sentence:

> **A lightweight, end-to-end goalkeeper analytics platform for the Premier League that demonstrates modern data engineering principles through a domain I deeply understand.**

More broadly, this project explores how a lightweight performance framework can be constructed for sports analytics use cases. Here, that framework is used to assess and compare the performance of Premier League goalkeepers.

## Scope & Constraints

This project uses goalkeeper match-level performance data from [FBRef.com](https://fbref.com/en/) as its primary data source. Due to the relatively small number of Premier League goalkeepers and the fixed match schedule, the resulting dataset is modest in size, with low data volume and low velocity by modern data engineering standards.

Scraping is throttled to comply with Sports-Reference’s published [bot-traffic limits](https://www.sports-reference.com/bot-traffic.html) (≈10 requests per minute), with conservative delays and backoff on rate-limit responses. The project is strictly non-commercial, does not compete with or substitute for Sports-Reference services, and does not use any collected data for training or supporting AI or machine-learning models, in accordance with the [Site Terms of Use](https://www.sports-reference.com/termsofuse.html).

All underlying data remains the property of Sports-Reference and its data providers; this project acknowledges and appreciates the availability of FBRef for personal use.

## Data Architecture

The data architecture for this project is intentionally simple and lightweight, and demonstrates the data engineering lifecycle—ingestion, transformation, and serving—on a small, low-velocity dataset. The platform follows a batch-oriented ELT pattern. Goalkeeper match data is scraped from FBRef, loaded into a local analytical database (DuckDB), transformed using dbt into curated analytical tables, and served via a lightweight web application. The entire pipeline is orchestrated locally using a Makefile to allow end-to-end or stepwise execution.

**Ingestion:** Data ingestion is handled via a Python-based web scraper using Selenium. A two-step approach is used:
1. Scraping a central “Premier League Goalkeepers” page to build a players manifest, and
2. Iterating over each goalkeeper’s match log URL to extract match-level performance data

The players manifest also stores metadata (e.g. last scraped date), illustrating how idempotency and incremental logic could be introduced in a more production-grade pipeline.

**Storage & Loading:** Raw match-level data is persisted locally and loaded into DuckDB, which serves as the project’s analytical database. DuckDB is well-suited to this use case because it is an OLAP-oriented engine designed for read-heavy, analytical SQL workloads, aligning with the project’s focus. It also offers native Python integration, enabling fast iteration while keeping the overall architecture simple.

**Transformation:** All transformations are handled exclusively in dbt, using a simple layered model structure (see below). Raw match logs are unified and parsed into clean, match-level staging models before being aggregated into fact tables representing goalkeeper performance across key dimensions (shot-stopping, distribution, sweeping, and crossing).

**Serving:** Curated analytical tables are exported and uploaded to a private Amazon S3 bucket, where they are consumed by a lightweight Flask-based web application (WIP). This separates analytical processing from presentation and mirrors common patterns used in production analytics systems.

Tooling choices were guided by fitness-for-purpose, with the aim of maximising clarity and iteration speed over architectural complexity. Given the low data volume, batch cadence, and stable schema, a simple data stack was most appropriate. The project illustrates how many real-world analytics problems can be solved cleanly with a small number of well-chosen tools, provided the underlying design is sound.

**Diagram:** TO ADD

## Data Modelling Approach

Data is modelled using a simple layered approach designed to minimise ambiguity with each layer having a clear, single responsibility. Given the project’s objective, the modelling approach prioritises analytics-ready data marts that support direct reads in the front end. For example, `fct_goalkeeper_performance` serves as the primary source of truth for goalkeeper performance metrics, while `mart_goalkeeper_league_ratings` builds on this foundation to compare goalkeepers relative to the league.

**Model layers:**

-	`stg_matchlogs_all`: All raw match log data from FBRef.com.
-	`stg_matchlogs_parsed`: Cleaned and parsed match-level goalkeeper data derived from match logs.
-	`fct_goalkeeper_performance`: Aggregated goalkeeper performance over all EPL matches.
-	`mart_goalkeeper_league_ratings`: Goalkeeper performance relative to other goalkeepers in the EPL.

## Goalkeeper Performance Framework

This project approaches goalkeeper performance as inherently multi-dimensional. Rather than relying on a single headline statistic, performance is conceptualised as a combination of distinct but complementary skill areas that together describe how a goalkeeper contributes to preventing goals and supporting team play. The aim of the framework is not to define a “best” goalkeeper, but to provide a structured lens through which goalkeeper performance can be compared and explored across multiple dimensions.

**Core Performance Dimensions:** Based on the data available and a football-first view of the role, goalkeeper performance is assessed across the following core dimensions and metrics:

| Performance Dimension | Description | Metrics Used |
|----------------------|-------------|--------------|
| **Shot Stopping** | The most fundamental goalkeeper responsibility, capturing how effectively a goalkeeper prevents shots on target from becoming goals. | **Save %** – Percentage of shots on target saved by the goalkeeper.<br><br>**PSxG − GA** – Difference between post-shot expected goals conceded and actual goals conceded, indicating goals prevented relative to shot quality. |
| **Crossing** | A goalkeeper’s ability to deal with aerial threats in the penalty area, including claiming, punching, or otherwise neutralising opposition crosses. | **Crosses Stopped %** – Percentage of opposition crosses into the penalty area that are successfully stopped by the goalkeeper. |
| **Distribution** | Reflecting the modern role of goalkeepers as additional ball-players, this dimension captures involvement and effectiveness in passing and ball progression. | **Passes Attempted (per 90)** – Average number of passes attempted per 90 minutes, excluding goal kicks.<br><br>**Long Kick Pass Completion %** – Completion rate for launched passes over 40 yards, calculated as completed versus attempted long passes. |
| **Sweeping** | Proactive defensive actions, often outside the penalty area, capturing how goalkeepers prevent dangerous situations before a shot occurs. | **Defensive Actions Outside Penalty Area (per 90)** – Average number of defensive interventions made outside the penalty area per 90 minutes, representing sweeping activity. |


**Standardised Comparison:** To enable fair comparison across goalkeepers, metrics are standardised at the league level. This allows performance to be interpreted relative to peers, rather than in isolation, and helps surface strengths and weaknesses across different dimensions without relying on raw totals. The resulting outputs are intended to support comparison, not final judgments.

**Subjectivity:** This framework is explicitly subjective. Other dimensions could reasonably be included, and many metrics are influenced by external factors such as team defensive structure, opposition quality, and tactical role. Rather than claiming objectivity, the framework aims to provide a transparent and interpretable view of performance based on dimensions that are widely recognised in football analysis. The choices of dimensions, metrics, and relative importance reflect informed judgment rather than universal truth.

## Outputs & Intended Use

The core data products are the `fct_goalkeeper_performance` and `mart_goalkeeper_league_ratings` tables described above. These datasets are designed to be served to a lightweight Flask application and consumed via tables and simple visual summaries (e.g. sortable tables, radar charts), enabling users to explore and compare goalkeepers without requiring any additional transformation logic in the front end.

![Example](notebooks/example_plot.png)

**Example:** Radar chart to compare three goalkeeper's performance.

## Current Status & Roadmap

**Current status:**

- Data ingestion, transformation, and modelling pipeline is complete.
- Analytics-ready fact and mart tables have been finalised.
- Front-end views and visualisations have been conceptualised at a design level.

**Next steps**
- Implement a minimal Flask front end to serve curated datasets.
- Expose core tables via simple charts and tables for exploratory analysis.