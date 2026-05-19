"""Debug KCI with session."""
import requests
from bs4 import BeautifulSoup

s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

# First visit main page to get cookies
s.get("https://www.kci.go.kr/kciportal/main.kci", timeout=15)

# Then search with session
resp = s.post(
    "https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci",
    data={"poSearchBean.keywordList": "smart grid", "poSearchBean.searType": "TOTAL"},
    timeout=15,
)

print(f"Status: {resp.status_code}, Length: {len(resp.text)}")
if "검색결과가 없습니다" in resp.text:
    print("NO RESULTS")
else:
    print("HAS RESULTS!")

# Try using referer
resp2 = s.post(
    "https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci",
    data={"poSearchBean.keywordList": "smart grid", "poSearchBean.searType": "TOTAL"},
    headers={"Referer": "https://www.kci.go.kr/kciportal/main.kci"},
    timeout=15,
)
print(f"With referer - Status: {resp2.status_code}, Length: {len(resp2.text)}")
if "검색결과가 없습니다" in resp2.text:
    print("NO RESULTS")
else:
    print("HAS RESULTS!")
    soup = BeautifulSoup(resp2.text, "lxml")
    titles = soup.select(".subject a, .title a")
    print(f"Found {len(titles)} titles:")
    for t in titles[:5]:
        print(f"  {t.get_text(strip=True)[:60]}")

# Try the detailed search page (thesis-specific)
resp3 = s.post(
    "https://www.kci.go.kr/kciportal/po/search/poArtiSearList.kci",
    data={"poSearchBean.keywordList": "smart grid", "poSearchBean.searType": "thesis", "poSearchBean.startPg": "1"},
    headers={"Referer": "https://www.kci.go.kr/kciportal/main.kci"},
    timeout=15,
)
print(f"\nThesis search - Status: {resp3.status_code}")
if "검색결과가 없습니다" in resp3.text:
    print("NO RESULTS")
else:
    print("HAS RESULTS!")
    soup3 = BeautifulSoup(resp3.text, "lxml")
    subjects = soup3.select(".subject a")
    print(f"Found {len(subjects)} subjects")
    for s in subjects[:3]:
        print(f"  {s.get_text(strip=True)[:60]}")

# Print cookies
print(f"\nCookies: {dict(s.cookies)}")
