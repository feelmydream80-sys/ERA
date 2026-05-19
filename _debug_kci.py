"""Debug KCI web response."""
import requests, re

headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.post(
    "https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci",
    data={"poSearchBean.keywordList": "smart grid", "poSearchBean.searType": "TOTAL"},
    headers=headers, timeout=15,
)

print(f"Status: {resp.status_code}, Length: {len(resp.text)}")

# Check if results exist
if "검색결과가 없습니다" in resp.text:
    print("NO RESULTS in response")
else:
    print("HAS RESULTS!")
    
# Find ALL links
titles = re.findall(r"<a[^>]*>([^<]+)</a>", resp.text)
print(f"Total links: {len(titles)}")
for t in titles[:20]:
    t = t.strip()
    if t and len(t) > 5:
        print(f"  {t[:60]}")

# Find tables
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, "lxml")

# Check all forms
for form in soup.find_all("form"):
    name = form.get("name", "")
    action = form.get("action", "")
    print(f"\nForm: name={name}, action={action}, len={len(str(form))}")

# Find all table rows
rows = soup.select("tr")
print(f"\nTotal <tr>: {len(rows)}")
for row in rows[:5]:
    print(f"  {str(row)[:200]}")

# Print the body content around where results should be
body = soup.find("body")
if body:
    text = body.get_text("\n", strip=True)
    # Find the result section
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "검색" in line and ("결과" in line or "결과" in line):
            print(f"\nResult line {i}: {line[:100]}")
