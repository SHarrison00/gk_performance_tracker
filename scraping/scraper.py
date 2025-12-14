import time
from io import StringIO
from pathlib import Path

import pandas as pd
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from .utils import ts


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


    def scrape_url_to_df(self, url: str) -> pd.DataFrame:
        
        self.driver.get(url)
        time.sleep(self.wait_seconds)
        
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
