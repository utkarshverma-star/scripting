import re
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://cdsco.gov.in/opencms/opencms/en/Medical-Device-Diagnostics/Medical-Device-Diagnostics/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=headers, timeout=60)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

data = []

for a in soup.find_all("a", href=True):

    href = a["href"]

    if ".pdf" not in href.lower():
        continue

    pdf_url = urljoin(URL, href)

    # ----------------------------------
    # Extract title
    # ----------------------------------
    title = a.get_text(" ", strip=True)

    # Get surrounding text
    container_text = ""

    tr = a.find_parent("tr")

    if tr:
        container_text = tr.get_text(" ", strip=True)
    else:
        parent = a.parent
        if parent:
            container_text = parent.get_text(" ", strip=True)

    # ----------------------------------
    # Extract year/date
    # ----------------------------------
    year_match = re.search(
        r"\b(19|20)\d{2}\b",
        container_text
    )

    date = year_match.group(0) if year_match else ""

    # ----------------------------------
    # Fix bad titles like:
    # 2014
    # 2015
    # 2016
    # ----------------------------------
    if (
        not title
        or re.fullmatch(r"(19|20)\d{2}", title)
        or title == date
    ):

        filename = os.path.basename(pdf_url)

        title = (
            filename
            .replace(".pdf", "")
            .replace("_", " ")
            .replace("-", " ")
        )

        title = re.sub(r"\s+", " ", title).strip()

    data.append({
        "Title": title,
        "Date": date,
        "PDF_URL": pdf_url
    })

df = pd.DataFrame(data)

df.drop_duplicates(
    subset=["PDF_URL"],
    inplace=True
)

df = df.sort_values(
    ["Date", "Title"],
    ascending=[False, True]
)

print(df)

print("\nTOTAL PDFs:", len(df))

df.to_excel(
    "CDSCO_Medical_Device_Diagnostics.xlsx",
    index=False
)

print("\nSaved Successfully")