import re
import time
from io import StringIO
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils.logging import ts


JS_EXTRACT_TABLE = """
const table = document.getElementById("matchlogs_all");
if (!table) return "NO_TABLE";

const rows = [];
const headerCells = table.querySelectorAll("thead tr th");
const headers = Array.from(headerCells).map(th => th.dataset.stat || th.textContent.trim());
rows.push(headers.join(","));

table.querySelectorAll("tbody tr").forEach(tr => {
  if (tr.classList.contains("thead") || tr.classList.contains("spacer")) return;

  const cells = tr.querySelectorAll("th, td");
  const values = Array.from(cells).map(td =>
    (td.textContent || "").trim().replace(/,/g, "")
  );

  if (values.some(v => v !== "")) {
    rows.push(values.join(","));
  }
});

return rows.join("\\n");
"""

# Matches: /en/players/<player_id>/<player_slug>
PLAYER_RE = re.compile(r"^/en/players/([^/]+)/([^/]+)$")


class FBRefScraper:
    def __init__(self, headless: bool = False, wait_seconds = 5):

        options = Options()
        service = Service("/usr/local/bin/chromedriver")
                
        if headless:
            options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(
            service=service,
            options=options
        )        
        self.wait_seconds = wait_seconds

    
    def close(self):
        self.driver.quit()


    @staticmethod
    def build_matchlogs_url(player_id: str, player_slug: str) -> str:
        return (
            f"https://fbref.com/en/players/{player_id}/matchlogs/"
            f"{{season}}/{player_slug}-Match-Logs"
        )


    def scrape_player_matchlogs_urls(self, base_url: str) -> list[dict]:

        self.driver.get(base_url)
        time.sleep(self.wait_seconds)

        els = self.driver.find_elements(
            By.CSS_SELECTOR, 'td[data-stat="player"] a[href]')

        players_by_id: dict[str, dict] = {}

        # Iterate across player links
        for a in els:
            href = a.get_attribute("href") or ""
            path = href.replace("https://fbref.com", "")

            match = PLAYER_RE.match(path)
            if not match:
                continue
            
            player_id, player_slug = match.group(1), match.group(2)
            matchlogs_url = self.build_matchlogs_url(player_id, player_slug)

            players_by_id[player_id] = {
                "player_id": player_id,
                "player_slug": player_slug,
                "player_url": urljoin("https://fbref.com", path),
                "matchlogs_url": matchlogs_url,
            }

        return list(players_by_id.values())


    def scrape_player_matchlogs_data(self, url: str) -> pd.DataFrame:
        
        self.driver.get(url)

        # Waits until matchlogs table exists in DOM
        wait = WebDriverWait(self.driver, self.wait_seconds)
        wait.until(EC.presence_of_element_located((By.ID, "matchlogs_all")))
        
        csv_text = self.driver.execute_script(JS_EXTRACT_TABLE)
        
        if not csv_text or csv_text.startswith("NO_TABLE"):
          raise RuntimeError(
              f"[{ts()}] Failed to extract table.\n"
              f"URL: {url}\n"
              f"csv_text: {csv_text}"
          )        
        
        return pd.read_csv(StringIO(csv_text))


def load_config(path: str | Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
