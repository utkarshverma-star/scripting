# # import pandas as pd
# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin
# # import os
# # import re

# # excel_file = r"C:\change_file_without_func\CDSCO_Circulars.xlsx"

# # download_folder = r"C:\change_file_without_func\CDSCO_circulars_PDF"
# # os.makedirs(download_folder, exist_ok=True)

# # df = pd.read_excel(excel_file)

# # headers = {
# #     "User-Agent": "Mozilla/5.0"
# # }

# # for idx, row in df.iterrows():

# #     title = str(row["Title"]).strip()
# #     page_url = str(row["PDF_URL"]).strip()

# #     if (
# #         not page_url.startswith("http")
# #         or page_url.lower() == "nan"
# #     ):
# #         continue

# #     try:

# #         # Step 1: Open CDSCO page
# #         r = requests.get(
# #             page_url,
# #             headers=headers,
# #             timeout=60
# #         )

# #         soup = BeautifulSoup(
# #             r.text,
# #             "html.parser"
# #         )

# #         iframe = soup.find("iframe")

# #         if not iframe:
# #             print(f"No iframe found -> Row {idx+1}")
# #             continue

# #         pdf_url = urljoin(
# #             "https://cdsco.gov.in",
# #             iframe["src"]
# #         )

# #         # Step 2: Download actual PDF
# #         pdf_response = requests.get(
# #             pdf_url,
# #             headers=headers,
# #             timeout=120,
# #             stream=True
# #         )

# #         pdf_response.raise_for_status()

# #         safe_name = re.sub(
# #             r'[\\/*?:"<>|]',
# #             "_",
# #             title
# #         )

# #         safe_name = safe_name[:180]

# #         file_path = os.path.join(
# #             download_folder,
# #             safe_name + ".pdf"
# #         )

# #         with open(file_path, "wb") as f:
# #             for chunk in pdf_response.iter_content(8192):
# #                 if chunk:
# #                     f.write(chunk)

# #         size_kb = round(
# #             os.path.getsize(file_path) / 1024,
# #             2
# #         )

# #         print(
# #             f"{idx+1} Downloaded -> {size_kb} KB"
# #         )

# #     except Exception as e:

# #         print(
# #             f"Failed Row {idx+1}: {e}"
# #         )

# # print("\nDone")

# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# url = "https://cdsco.gov.in/opencms/opencms/system/modules/CDSCO.WEB/elements/download_file_division.jsp?num_id=MTQzMjM="

# r = requests.get(url)

# soup = BeautifulSoup(r.text, "html.parser")

# iframe = soup.find("iframe")

# pdf_url = urljoin(
#     "https://cdsco.gov.in",
#     iframe["src"]
# )

# print(pdf_url)

import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests.utils import requote_uri
import os
import re
import time


download_folder = r"C:\change_file_without_func\CDSCO_Medical_Device_Diagnostics_PDF"
excel_file = r"C:\change_file_without_func\CDSCO_Medical_Device_Diagnostics.xlsx"

# # download_folder = r"C:\change_file_without_func\CDSCO_circulars_PDF"
# # os.makedirs(download_folder, exist_ok=True)
os.makedirs(download_folder, exist_ok=True)

df = pd.read_excel(excel_file)

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

for idx, row in df.iterrows():

    title = str(row["Title"]).strip()
    page_url = str(row["PDF_URL"]).strip()

    if not page_url.startswith("http"):
        continue

    safe_name = re.sub(r'[\\/*?:"<>|]', "_", title)
    safe_name = safe_name[:180]

    pdf_file = os.path.join(
        download_folder,
        safe_name + ".pdf"
    )

    # Skip already downloaded files
    if os.path.exists(pdf_file):
        print(f"Skip {idx+1}")
        continue

    success = False

    for attempt in range(5):

        try:

            r = session.get(
                page_url,
                timeout=60
            )

            soup = BeautifulSoup(
                r.text,
                "html.parser"
            )

            iframe = soup.find("iframe")

            if not iframe:
                raise Exception("No iframe found")

            pdf_url = urljoin(
                "https://cdsco.gov.in",
                iframe["src"]
            )

            pdf_url = requote_uri(pdf_url)

            pdf_response = session.get(
                pdf_url,
                timeout=120,
                stream=True
            )

            pdf_response.raise_for_status()

            with open(pdf_file, "wb") as f:

                for chunk in pdf_response.iter_content(8192):

                    if chunk:
                        f.write(chunk)

            size_kb = round(
                os.path.getsize(pdf_file) / 1024,
                2
            )

            print(
                f"{idx+1} Downloaded -> {size_kb} KB"
            )

            success = True
            break

        except Exception as e:

            print(
                f"Row {idx+1} Retry {attempt+1}/5 -> {e}"
            )

            time.sleep(10)

    if not success:

        with open(
            "failed_rows.txt",
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                f"{idx+1}|{title}|{page_url}\n"
            )

    # Prevent server blocking
    time.sleep(1)

print("\nDone")