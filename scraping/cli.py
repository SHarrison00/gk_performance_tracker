import argparse
from pathlib import Path
import time

from .scraper import FBRefScraper, load_config


def build_matchlog_url(player_id: str, season: str, player_slug: str) -> str:
    return (
        f"https://fbref.com/en/players/"
        f"{player_id}/matchlogs/{season}/{player_slug}-Match-Logs"
    )


def cmd_scrape_matchlogs(args):
    config = load_config(args.config)
    scrape_cfg = config["scraping"]
    players = config["players"]

    output_dir = Path(scrape_cfg["output_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    scraper = FBRefScraper(
        headless = scrape_cfg.get("headless", False),
        wait_seconds = scrape_cfg.get("wait_seconds", 5),
    )

    try:
        for player in players:
            for season in player["seasons"]:
                url = build_matchlog_url(
                    player_id = player["player_id"],
                    season = season,
                    player_slug = player["player_slug"],
                )
                print(f"Scraping {url} ...")
                df = scraper.scrape_url_to_df(url)

                out_name = f"{player['player_slug']}_{season}.csv"
                out_path = output_dir / out_name
                df.to_csv(out_path, index=False)
                print(f"Saved -> {out_path}")

                time.sleep(scrape_cfg.get("request_delay_seconds", 2))

    finally:
        scraper.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yml")
    args = parser.parse_args()
    cmd_scrape_matchlogs(args)


if __name__ == "__main__":
    main()