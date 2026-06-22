import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://ppqs.gov.in"

all_data = []

page = 0

while True:

    url = f"https://ppqs.gov.in/notice-board?page={page}"

    print(f"Processing Page {page + 1}")

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    if response.status_code != 200:
        break

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")

    if not table:
        print("Table not found")
        break

    rows = table.find_all("tr")[1:]  # skip header

    if len(rows) == 0:
        break

    page_pdf_count = 0

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 4:
            continue

        title = cols[1].get_text(" ", strip=True)
        publish_date = cols[2].get_text(" ", strip=True)

        pdf_link = cols[3].find("a", href=True)

        if pdf_link:

            pdf_url = urljoin(
                BASE_URL,
                pdf_link["href"]
            )

            all_data.append({
                "Title": title,
                "Publish_Date": publish_date,
                "PDF_URL": pdf_url
            })

            page_pdf_count += 1

    print(f"PDFs Found: {page_pdf_count}")

    if page_pdf_count == 0:
        break

    page += 1

df = pd.DataFrame(all_data)

df.drop_duplicates(
    subset=["PDF_URL"],
    inplace=True
)

df.to_excel(
    "PPQS_Notice_Board.xlsx",
    index=False
)

print("\nTotal PDFs:", len(df))
print("Output Saved -> PPQS_Notice_Board.xlsx")