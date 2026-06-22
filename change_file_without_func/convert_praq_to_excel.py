# import pandas as pd

# PARQUET_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_RECKITT_BRAND_HASHTAG_202606_UPDATED.parquet

# EXCEL_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_RECKITT_BRAND_HASHTAG_202606_UPDATED_media.xlsx"

# df = pd.read_parquet(PARQUET_FILE)

# print("Rows :", len(df))
# print("Columns :", len(df.columns))

# df.to_excel(
#     EXCEL_FILE,
#     index=False
# )

# print("Saved ->", EXCEL_FILE)

import pandas as pd
from pathlib import Path

files = [
    r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_RECKITT_BRAND_HANDLE_202606.parquet",
    r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_COMPETITOR_HASHTAG_202606 (5).parquet",
    r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_COMPETITOR_HANDLE_202606 (1).parquet",
    r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_RECKITT_BRAND_HASHTAG_202606 (3).parquet"
]

for parquet_file in files:

    try:
        print("\n" + "=" * 80)
        print("Reading:", parquet_file)

        df = pd.read_parquet(parquet_file)

        excel_file = str(
            Path(parquet_file).with_suffix(".xlsx")
        )

        print("Rows    :", len(df))
        print("Columns :", len(df.columns))

        df.to_excel(
            excel_file,
            index=False
        )

        print("Saved ->", excel_file)

    except Exception as e:

        print("Failed ->", parquet_file)
        print("Error  ->", e)

print("\nDone Successfully")