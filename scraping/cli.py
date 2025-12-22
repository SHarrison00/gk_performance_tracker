import argparse
import json
import time
from pathlib import Path

from .scraper import FBRefScraper, load_config
from utils.logging import ts, write_manifest, now_iso_utc


def cmd_scrape_player_matchlogs_urls(args):
    config = load_config(args.config)
    scrape_cfg = config["scraping"]
    output_cfg = config["output"]

    player_urls_dir = Path(output_cfg["player_urls_dir"])
    player_urls_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = player_urls_dir / "players_manifest.json"

    base_url = config["discovery"].get("base_url")
    
    scraper = FBRefScraper(
        headless = scrape_cfg.get("headless", False),
        wait_seconds = scrape_cfg.get("wait_seconds", 5),
    )        

    try:
        print(f"[{ts()}] Scraping player URLs from: { base_url }")
        players = scraper.scrape_player_matchlogs_urls(base_url)
        manifest_path.write_text(json.dumps(players, indent=2))
        print(f"[{ts()}] Saved manifest -> {manifest_path} ({len(players)} players)")

    finally:
        scraper.close()


def cmd_scrape_player_matchlogs_data(args):
    config = load_config(args.config)
    scrape_cfg = config["scraping"]
    discovery_cfg = config["discovery"]
    output_cfg = config["output"]

    # Read manifest for matchlog URLs
    player_urls_dir = Path(output_cfg["player_urls_dir"])
    manifest_path = player_urls_dir / "players_manifest.json"
    
    # Where matchlogs data will be written
    matchlogs_dir = Path(output_cfg["matchlogs_dir"])
    matchlogs_dir.mkdir(parents=True, exist_ok=True)

    players = json.loads(manifest_path.read_text())
    seasons = discovery_cfg.get("seasons")

    scraper = FBRefScraper(
        headless=scrape_cfg.get("headless", False),
        wait_seconds=scrape_cfg.get("wait_seconds", 5),
    )

    # TODO: Freshness logic
    # Scrape players based on data freshness, i.e. p["last_scraped_date"]
    # For now, scrape everyone:
    players_to_scrape = players

    try:
        for player in players_to_scrape:
            matchlogs_url = player["matchlogs_url"]
            slug = player["player_slug"]

            for season in seasons:
                url = matchlogs_url.format(season=season)
                
                print(f"[{ts()}] Scraping {url} ...")
                df = scraper.scrape_player_matchlogs_data(url)
                out_name = f"{slug}_{season}.csv"
                out_path = matchlogs_dir / out_name
                df.to_csv(out_path, index=False)
                print(f"[{ts()}] Saved -> {out_path}")
                
                time.sleep(scrape_cfg.get("request_delay_seconds"))
            
            # Update manifest after each scrape
            player["last_scraped_date"] = now_iso_utc()
            write_manifest(manifest_path, players)

            time.sleep(scrape_cfg.get("request_delay_seconds"))

    finally:
        scraper.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()
    
    # Run discovery -> writes players_manifest.json
    cmd_scrape_player_matchlogs_urls(args)

    # Run scrape -> reads players_manifest.json and writes matchlogs
    cmd_scrape_player_matchlogs_data(args)


if __name__ == "__main__":
    main()


""" 
    
    python3 -m scraping.cli --config scraping/config.yml

"""