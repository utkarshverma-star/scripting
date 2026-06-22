import pandas as pd
from urllib.parse import urlparse
from datetime import datetime

# ====================================================
# FILE PATHS
# ====================================================

PARQUET_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202604.parquet"

LIVE_LINK_FILE = r"C:\Users\admin\Downloads\downloaded_sheet.xlsx"

OUTPUT_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202604_UPDATEDED_CURRENT_DATE.parquet"

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

        if len(parts) >= 2 and parts[0] in [
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

# ====================================================
# READ EXCEL ALL SHEETS
# ====================================================

print("Reading Internal Live Link Sheets...")

xls = pd.ExcelFile(LIVE_LINK_FILE)

all_dfs = []

for sheet in xls.sheet_names:

    df = pd.read_excel(
        LIVE_LINK_FILE,
        sheet_name=sheet,
        dtype=str
    )

    if not df.empty:
        all_dfs.append(df)

live_df = pd.concat(
    all_dfs,
    ignore_index=True
)

print("Live Link Rows:", len(live_df))

# ====================================================
# CLEAN COLUMN NAMES
# ====================================================

live_df.columns = (
    live_df.columns
    .str.strip()
)

# ====================================================
# EXTRACT SHORTCODE
# ====================================================

live_df["ShortCode"] = (
    live_df["Live Links"]
    .apply(extract_shortcode)
)

live_df["ShortCode"] = (
    live_df["ShortCode"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
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

print(
    "Unique ShortCodes In Sheet:",
    live_df["ShortCode"].nunique()
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
# CLEAN PARQUET SHORTCODE
# ====================================================

parquet_df["shortCode"] = (
    parquet_df["shortCode"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# ====================================================
# MEDIA PROMOTION TYPE
# ====================================================

today = datetime.today().date()

print("Today's Date :", today)

def get_media_type(row):

    shortcode = row["shortCode"]

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

    start_date = start_date.date()
    end_date = end_date.date()

    if start_date <= today <= end_date:
        return 1

    return 0

# ====================================================
# CREATE COLUMN
# ====================================================

print("Calculating Media Promotion Type...")

parquet_df["Media Promotion Type"] = (
    parquet_df.apply(
        get_media_type,
        axis=1
    )
)

# ====================================================
# SUMMARY
# ====================================================

print("\nSummary")

print(
    parquet_df[
        "Media Promotion Type"
    ].value_counts(
        dropna=False
    )
)

print(
    "\nPaid Rows Found:",
    (
        parquet_df[
            "Media Promotion Type"
        ] == 1
    ).sum()
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