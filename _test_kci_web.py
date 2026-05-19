"""Test KCI website POST search with proper parsing."""
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Test with English keyword
resp = requests.post(
    "https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci",
    data={"searchType": "TOTAL", "searchWord": "smart grid"},
    headers=headers, timeout=15,
)
print(f"Status: {resp.status_code}, Length: {len(resp.text)}")
print(f"Encoding: {resp.encoding}")

soup = BeautifulSoup(resp.text, "lxml")

# Find all links
all_links = soup.find_all("a")
print(f"\nTotal <a> tags: {len(all_links)}")

# Find elements with 'subject' class
subjects = soup.find_all(class_="subject")
print(f"Subject class elements: {len(subjects)}")

# Find table rows in the search result table
tables = soup.find_all("table", class_="search-answer-tbl")
print(f"\nSearch answer tables: {len(tables)}")

# Look for tr/td patterns that might contain paper data
for table in tables:
    rows = table.find_all("tr")
    print(f"  Table rows: {len(rows)}")
    for row in rows[:3]:
        print(f"  Row HTML: {str(row)[:200]}")

# Check for any JSON data
scripts = soup.find_all("script")
for script in scripts:
    if script.string and ("searchWord" in script.string or "articles" in script.string):
        print(f"\nFound relevant script: {script.string[:200]}")

# Try Korean keyword
resp2 = requests.post(
    "https://www.kci.go.kr/kciportal/po/search/poTotalSearList.kci",
    data={"searchType": "TOTAL", "searchWord": "전력"},
    headers=headers, timeout=15,
)
soup2 = BeautifulSoup(resp2.text, "lxml")
subjects2 = soup2.find_all(class_="subject")
print(f"\nKorean keyword '전력': subject elements: {len(subjects2)}")

# Check if search results are loaded via AJAX
# Look for the article search form
forms = soup.find_all("form")
print(f"\nForms: {len(forms)}")
for f in forms:
    name = f.get("name", "")
    action = f.get("action", "")
    if "arti" in name.lower() or "search" in action.lower():
        print(f"  Form: name={name}, action={action}")
        # Check for hidden inputs with result data
        for inp in f.find_all("input", type="hidden"):
            val = inp.get("value", "")
            if val and len(val) > 20:
                print(f"    Hidden: {inp.get('name')} = {val[:100]}")

# Print first 3000 chars of the response to understand structure
print("\n--- First 3000 chars of response ---")
print(resp.text[:3000])
