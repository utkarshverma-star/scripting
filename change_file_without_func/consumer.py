import re
import time
import pandas as pd
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


BASE = "https://consumeraffairs.gov.in"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

all_data = []

# =====================================================
# TOTAL RESULTS -> TOTAL PAGES
# =====================================================

driver.get("https://consumeraffairs.gov.in/pages/latest-news")
time.sleep(5)

txt = driver.find_element("tag name", "body").text

m = re.search(
    r"Showing\s+\d+\s+to\s+\d+\s+of\s+(\d+)\s+results",
    txt,
    re.I
)

total_results = int(m.group(1))
page_size = 10
total_pages = (total_results + page_size - 1) // page_size

print("TOTAL RESULTS:", total_results)
print("TOTAL PAGES:", total_pages)

# =====================================================
# LOOP PAGES
# =====================================================

for page in range(1, total_pages + 1):

    url = (
        "https://consumeraffairs.gov.in/pages/latest-news"
        if page == 1
        else f"https://consumeraffairs.gov.in/pages/latest-news?page={page}"
    )

    print("\nPAGE", page)

    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    rows = soup.select("table tbody tr")

    print("ROWS:", len(rows))

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 5:
            continue

        title = cols[1].get_text(" ", strip=True)

        published_date = cols[3].get_text(" ", strip=True)

        archive_date = cols[4].get_text(" ", strip=True)

        pdf_url = ""

        # =================================================
        # CASE 1 : DIRECT PDF
        # =================================================

        pdf_link = row.select_one('a[href$=".pdf"]')

        if pdf_link:

            pdf_url = pdf_link.get("href", "")

            if pdf_url.startswith("/"):
                pdf_url = BASE + pdf_url

        else:

            # =============================================
            # CASE 2 : VIEW LINK -> OPEN DETAIL PAGE
            # =============================================

            view_link = row.select_one("a")

            if view_link:

                detail_url = view_link.get("href", "")

                if detail_url.startswith("/"):
                    detail_url = BASE + detail_url

                try:

                    r = requests.get(
                        detail_url,
                        timeout=30,
                        verify=False
                    )

                    dsoup = BeautifulSoup(r.text, "html.parser")

                    pdf = dsoup.select_one('a[href$=".pdf"]')

                    if pdf:

                        pdf_url = pdf.get("href", "")

                        if pdf_url.startswith("/"):
                            pdf_url = BASE + pdf_url

                except Exception:
                    pass

        all_data.append(
            {
                "Title": title,
                "Published_Date": published_date,
                "Archive_Date": archive_date,
                "PDF_URL": pdf_url
            }
        )

driver.quit()

df = pd.DataFrame(all_data)

df.drop_duplicates(
    subset=["Title", "Published_Date"],
    inplace=True
)

print(df.head())
print("\nTOTAL RECORDS:", len(df))

df.to_excel(
    "Consumer_Affairs_Latest_News.xlsx",
    index=False
)

print("\nSaved Successfully")