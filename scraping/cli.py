import argparse
import json
import time
from pathlib import Path

from .scraper import FBRefScraper, load_config
from utils.logging import ts, write_manifest, update_status_json, make_status_patch
from utils.scraping import is_stale


def make_scraper(scrape_cfg):
    """Return FBRedScraper object."""
    return FBRefScraper(
        headless = scrape_cfg.get("headless", False),
        wait_seconds = scrape_cfg.get("wait_seconds", 5),
        retries = scrape_cfg.get("retries", 5),
        success_delay_seconds = scrape_cfg.get("success_delay_seconds", 0),
    )


def cmd_scrape_player_matchlogs_urls(config):
    """Scrape player matchlog URLs from FBRef and write a players manifest."""
    scrape_cfg = config["scraping"]
    output_cfg = config["output"]

    public_dir = Path(output_cfg["public_dir"])
    public_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = public_dir / "players_manifest.json"
    base_url = config["discovery"].get("base_url")

    scraper = make_scraper(scrape_cfg)

    try:
        print(f"[{ts()}] Scraping player URLs from: {base_url}")
        players = scraper.scrape_player_matchlogs_urls(base_url)
        write_manifest(manifest_path, players)
        print(f"[{ts()}] Saved manifest -> {manifest_path} ({len(players)} players)")

    finally:
        scraper.close()


def cmd_scrape_player_matchlogs_data(config):
    """Scrape player matchlog data from FBRef and write CSV files."""
    scrape_cfg = config["scraping"]
    discovery_cfg = config["discovery"]
    output_cfg = config["output"]

    public_dir = Path(output_cfg["public_dir"])
    manifest_path = public_dir / "players_manifest.json"

    matchlogs_dir = Path(output_cfg["matchlogs_dir"])
    matchlogs_dir.mkdir(parents=True, exist_ok=True)

    players = json.loads(manifest_path.read_text())
    seasons = discovery_cfg.get("seasons")
    file_format = output_cfg.get("file_format")

    scraper = make_scraper(scrape_cfg)

    players_to_scrape = [p for p in players if is_stale(p)]

    try:
        for player in players_to_scrape:
            matchlogs_url = player["matchlogs_url"]
            slug = player["player_slug"]

            for season in seasons:
                url = matchlogs_url.format(season = season)

                print(f"[{ts()}] Scraping {url} ...")
                df = scraper.scrape_player_matchlogs_data(url)

                out_name = f"{slug}_{season}.{file_format}"
                out_path = matchlogs_dir / out_name
                df.to_csv(out_path, index=False)
                print(f"[{ts()}] Saved -> {out_path}")

            player["last_scraped_date"] = ts()
            write_manifest(manifest_path, players)

    finally:
        scraper.close()


def main():
    # Config
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()
    config = load_config(args.config) # Scraping params
    public_dir = Path("public")

    # Duration tracking
    started_utc = ts()
    t0 = time.perf_counter()

    # Scrape players manifest
    cmd_scrape_player_matchlogs_urls(config)

    # Reads players manifest and scrape matchlogs
    cmd_scrape_player_matchlogs_data(config)

    duration_s = round(time.perf_counter() - t0, 3)
    finished_utc = ts()

    status_patch = make_status_patch(
        step_name = "cli.py",
        info = "Extract/scrape player matchlogs raw data.",
        started_utc = started_utc,
        finished_utc = finished_utc,
        duration_s = duration_s,
    )
    update_status_json(public_dir / "status.json", status_patch)


if __name__ == "__main__":
    main()
