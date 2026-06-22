import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://ppqs.gov.in/acts"

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

records = []

table = soup.find("table")

if not table:
    raise Exception("Table not found")

rows = table.find_all("tr")

for row in rows[1:]:  # Skip header

    cols = row.find_all("td")

    if len(cols) < 4:
        continue

    title = cols[1].get_text(" ", strip=True)
    publish_date = cols[2].get_text(" ", strip=True)

    pdf_tag = cols[3].find("a", href=True)

    pdf_url = ""

    if pdf_tag:
        pdf_url = urljoin(URL, pdf_tag["href"])

    records.append({
        "Title": title,
        "Publish_Date": publish_date,
        "PDF_URL": pdf_url
    })

df = pd.DataFrame(records)

df.drop_duplicates(
    subset=["Title", "PDF_URL"],
    inplace=True
)

print(df.head())
print("\nTotal Records:", len(df))

df.to_excel(
    "PPQS_Acts.xlsx",
    index=False
)

print("Saved -> PPQS_Acts.xlsx")