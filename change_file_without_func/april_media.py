import pandas as pd
import requests
from urllib.parse import urlparse
from datetime import datetime

# ====================================================
# FILE PATHS
# ====================================================

PARQUET_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202605.parquet"

OUTPUT_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202605_CURRENT_DATE.parquet"

SPREADSHEET_ID = "1JR7prbTgekZvKZPPnqg7ZNRWAi88W0YF090bnKZhwFs"

DOWNLOAD_FILE = r"C:\Users\admin\Downloads\downloaded_sheet.xlsx"

# ====================================================
# DOWNLOAD GOOGLE SHEET
# ====================================================

print("Downloading Google Sheet...")

url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=xlsx"
)

response = requests.get(url, timeout=60)
response.raise_for_status()

with open(DOWNLOAD_FILE, "wb") as f:
    f.write(response.content)

print("Google Sheet Downloaded")

# ====================================================
# SHORTCODE EXTRACTOR
# ====================================================

def extract_shortcode(url):

    if pd.isna(url):
        return ""

    try:
        parts = [
            x
            for x in urlparse(str(url)).path.split("/")
            if x
        ]

        if len(parts) >= 2 and parts[0].lower() in [
            "p",
            "reel",
            "reels"
        ]:
            return parts[1].strip().lower()

    except Exception:
        pass

    return ""

# ====================================================
# READ PARQUET
# ====================================================

print("Reading Parquet...")

parquet_df = pd.read_parquet(PARQUET_FILE)

print("Parquet Rows:", len(parquet_df))

parquet_df["shortCode"] = (
    parquet_df["shortCode"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# ====================================================
# READ EXCEL
# ====================================================

print("Reading Excel...")

xls = pd.ExcelFile(DOWNLOAD_FILE)

all_dfs = []

for sheet in xls.sheet_names:

    df = pd.read_excel(
        DOWNLOAD_FILE,
        sheet_name=sheet
    )

    if not df.empty:
        all_dfs.append(df)

live_df = pd.concat(
    all_dfs,
    ignore_index=True
)

print("Live Link Rows:", len(live_df))

live_df.columns = live_df.columns.str.strip()

# ====================================================
# SHORTCODE
# ====================================================

live_df["ShortCode"] = (
    live_df["Live Links"]
    .apply(extract_shortcode)
)

# ====================================================
# DATE CONVERSION
# ====================================================

live_df["Media Promotion Start Date"] = pd.to_datetime(
    live_df["Media Promotion Start Date"],
    errors="coerce"
)

live_df["Media Promotion End Date"] = pd.to_datetime(
    live_df["Media Promotion End Date"],
    errors="coerce"
)

# ====================================================
# REMOVE DUPLICATES
# ====================================================

live_df = live_df.drop_duplicates(
    subset=["ShortCode"],
    keep="last"
)

# ====================================================
# LOOKUP
# ====================================================

lookup = live_df.set_index(
    "ShortCode"
)[
    [
        "Media Promotion Start Date",
        "Media Promotion End Date"
    ]
].to_dict("index")

# ====================================================
# CURRENT DATE LOGIC
# ====================================================

today = pd.Timestamp.today().normalize()

print("Current Date:", today.date())

def get_media_type(shortcode):

    shortcode = str(shortcode).strip().lower()

    if shortcode not in lookup:
        return 0

    start_date = lookup[shortcode][
        "Media Promotion Start Date"
    ]

    end_date = lookup[shortcode][
        "Media Promotion End Date"
    ]

    if pd.isna(start_date):
        return 0

    if pd.isna(end_date):
        return 0

    # CURRENTLY PAID
    if start_date <= today <= end_date:
        return 1

    return 0

# ====================================================
# CREATE COLUMN
# ====================================================

print("Calculating Media Promotion Type...")

parquet_df["Media Promotion Type"] = (
    parquet_df["shortCode"]
    .apply(get_media_type)
)

# ====================================================
# SUMMARY
# ====================================================

print("\nSummary")

print(
    parquet_df["Media Promotion Type"]
    .value_counts(dropna=False)
)

print(
    "\nPaid Rows Found:",
    (parquet_df["Media Promotion Type"] == 1).sum()
)

# ====================================================
# SAVE
# ====================================================

parquet_df.to_parquet(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:")
print(OUTPUT_FILE)