"""Parse KCI thesis search results."""
import requests
from bs4 import BeautifulSoup

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
s.get("https://www.kci.go.kr/kciportal/main.kci", timeout=15)

resp = s.post(
    "https://www.kci.go.kr/kciportal/po/search/poArtiSearList.kci",
    data={"poSearchBean.keywordList": "smart grid", "poSearchBean.searType": "thesis", "poSearchBean.startPg": "1"},
    headers={"Referer": "https://www.kci.go.kr/kciportal/main.kci"},
    timeout=15,
)

print(f"Status: {resp.status_code}, Length: {len(resp.text)}")
soup = BeautifulSoup(resp.text, "lxml")

# Find ALL td elements
tds = soup.find_all("td")
print(f"Total <td>: {len(tds)}")
for i, td in enumerate(tds[:10]):
    print(f"  td[{i}]: class={td.get('class','')}, colspan={td.get('colspan','')}, text={td.get_text(strip=True)[:50]}")

# Find all div with class
divs = soup.find_all("div", class_=True)
for d in divs:
    cls = " ".join(d.get("class", []))
    if "search" in cls.lower() or "result" in cls.lower() or "answer" in cls.lower():
        print(f"\nDiv class='{cls}' len={len(str(d))}")

# Find all rows in search-answer-tbl
tables = soup.select(".search-answer-tbl")
print(f"\nTables with search-answer-tbl: {len(tables)}")
for tbl in tables:
    rows = tbl.find_all("tr")
    print(f"  Rows: {len(rows)}")
    for row in rows[:3]:
        cells = row.find_all("td")
        print(f"    Cells: {len(cells)}")
        for ci, c in enumerate(cells):
            print(f"      td[{ci}]: {c.get_text(strip=True)[:60]}")

# Print the page content between body tags
body = soup.find("body")
if body:
    text = body.get_text("\n", strip=True)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "smart" in line.lower() or "grid" in line.lower() or "전력" in line or line.strip():
            if len(line.strip()) > 10:
                print(f"  text[{i}]: {line[:80]}")

# Look for paper titles in the entire HTML
import re
all_links = soup.find_all("a")
print(f"\nAll links: {len(all_links)}")
for a in all_links:
    txt = a.get_text(strip=True)
    if txt and len(txt) > 15:
        print(f"  {txt[:70]}")
        print(f"    href: {a.get('href','')[:60]}")
