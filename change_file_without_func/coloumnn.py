import pandas as pd
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASS = os.getenv("EMAIL_PASS")

EXCEL_FILE = r"C:\Users\admin\Downloads\Reckitt_Creator_Master_Updated.xlsx"

df = pd.read_excel(EXCEL_FILE, dtype=str)

missing_df = df[
    df["ShortCode"].isna()
    | (df["ShortCode"].str.strip() == "")
]

missing_count = len(missing_df)

if missing_count == 0:
    print("No missing shortcode found.")
    exit()

html_body = f"""
<p>Hi,</p>

<p><b>ShortCode Validation Report</b></p>

<p style="color:red;">
❌ Missing ShortCodes Found: <b>{missing_count}</b>
</p>

<table border="1" cellpadding="5" cellspacing="0">
<tr>
    <th>Name</th>
    <th>Live Link</th>
</tr>
"""

for _, row in missing_df.head(100).iterrows():

    html_body += f"""
    <tr>
        <td>{row.get('Name','')}</td>
        <td>{row.get('Live Link','')}</td>
    </tr>
    """

html_body += """
</table>

<br>
<p>Regards,<br>
Instagram Monitoring Bot</p>
"""

msg = MIMEMultipart()
msg["Subject"] = f"ALERT - {missing_count} Missing ShortCodes Found"
msg["From"] = SENDER_EMAIL
msg["To"] = "utkarsh.verma@teamcomputers.com"

msg.attach(MIMEText(html_body, "html"))

server = smtplib.SMTP("smtp.office365.com", 587)
server.starttls()
server.login(SENDER_EMAIL, SENDER_PASS)

server.sendmail(
    SENDER_EMAIL,
    ["utkarsh.verma@teamcomputers.com"],
    msg.as_string()
)

server.quit()

print(f"Email sent. Missing ShortCodes: {missing_count}")
import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "utkarsh.verma@teamcomputers.com"


msg = MIMEText("This is a test email from Python.")
msg["Subject"] = "Test Email"
msg["From"] = SENDER_EMAIL
msg["To"] = "utkarsh.verma@teamcomputers.com"

server = smtplib.SMTP("smtp.office365.com", 587)
server.starttls()

server.login(SENDER_EMAIL, SENDER_PASS)

server.sendmail(
    SENDER_EMAIL,
    ["utkarsh.verma@teamcomputers.com"],
    msg.as_string()
)

server.quit()

print("Email Sent Successfully")
# import pandas as pd
# from urllib.parse import urlparse

# # ====================================================
# # FILE PATHS
# # ====================================================

# PARQUET_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202606.parquet"

# LIVE_LINK_FILE = r"C:\Users\admin\Downloads\downloaded_sheet.xlsx"

# OUTPUT_FILE = r"C:\Users\admin\Downloads\DIGITAL_INFLUENCER_INSTAGRAM_URL_LINKS_202606_UPDATEDED.parquet"


# # ====================================================
# # SHORTCODE EXTRACTOR
# # ====================================================

# def extract_shortcode(url):

#     if pd.isna(url):
#         return ""

#     try:
#         parts = [
#             x
#             for x in urlparse(str(url)).path.split("/")
#             if x
#         ]

#         if len(parts) >= 2 and parts[0] in [
#             "p",
#             "reel",
#             "reels"
#         ]:
#             return parts[1].lower().strip()

#     except Exception:
#         pass

#     return ""


# # ====================================================
# # READ PARQUET
# # ====================================================

# print("Reading Parquet...")

# parquet_df = pd.read_parquet(PARQUET_FILE)

# print("Parquet Rows:", len(parquet_df))


# # ====================================================
# # READ EXCEL
# # ====================================================

# print("Reading Internal Live Link Sheets...")

# xls = pd.ExcelFile(LIVE_LINK_FILE)

# all_dfs = []

# for sheet in xls.sheet_names:

#     df = pd.read_excel(
#         LIVE_LINK_FILE,
#         sheet_name=sheet,
#         dtype=str
#     )

#     if not df.empty:
#         all_dfs.append(df)

# live_df = pd.concat(
#     all_dfs,
#     ignore_index=True
# )

# print("Live Link Rows:", len(live_df))


# # ====================================================
# # CLEAN COLUMNS
# # ====================================================

# live_df.columns = live_df.columns.str.strip()


# # ====================================================
# # SHORTCODE
# # ====================================================

# live_df["ShortCode"] = (
#     live_df["Live Links"]
#     .apply(extract_shortcode)
# )

# live_df = live_df.drop_duplicates(
#     subset=["ShortCode"],
#     keep="last"
# )

# print(
#     "Unique ShortCodes:",
#     live_df["ShortCode"].nunique()
# )


# # ====================================================
# # DATE CONVERSION
# # ====================================================

# live_df["Media Promotion Start Date"] = pd.to_datetime(
#     live_df["Media Promotion Start Date"],
#     errors="coerce"
# )

# live_df["Media Promotion End Date"] = pd.to_datetime(
#     live_df["Media Promotion End Date"],
#     errors="coerce"
# )

# parquet_df["Post_Date"] = pd.to_datetime(
#     parquet_df["timestamp"],
#     errors="coerce"
# )

# parquet_df["shortCode"] = (
#     parquet_df["shortCode"]
#     .astype(str)
#     .str.strip()
#     .str.lower()
# )


# # ====================================================
# # LOOKUP
# # ====================================================

# lookup = live_df.set_index(
#     "ShortCode"
# )[
#     [
#         "Media Promotion Start Date",
#         "Media Promotion End Date"
#     ]
# ].to_dict("index")


# # ====================================================
# # MEDIA PROMOTION TYPE
# # ====================================================

# def get_media_type(row):

#     shortcode = row["shortCode"]

#     if shortcode not in lookup:
#         return 0

#     post_date = row["Post_Date"]

#     if pd.isna(post_date):
#         return 0

#     start_date = lookup[shortcode][
#         "Media Promotion Start Date"
#     ]

#     end_date = lookup[shortcode][
#         "Media Promotion End Date"
#     ]

#     if pd.isna(start_date):
#         return 0

#     if pd.isna(end_date):
#         return 0

#     post_date = post_date.date()
#     start_date = start_date.date()
#     end_date = end_date.date()

#     if start_date <= post_date <= end_date:
#         return 1

#     return 0


# print("Calculating Media Promotion Type...")

# parquet_df["Media Promotion Type"] = (
#     parquet_df.apply(
#         get_media_type,
#         axis=1
#     )
# )


# # ====================================================
# # SUMMARY
# # ====================================================

# print("\nSummary")

# print(
#     parquet_df[
#         "Media Promotion Type"
#     ].value_counts(
#         dropna=False
#     )
# )

# print(
#     "\nPaid Rows:",
#     (parquet_df["Media Promotion Type"] == 1).sum()
# )


# # ====================================================
# # CLEANUP
# # ====================================================

# parquet_df.drop(
#     columns=["Post_Date"],
#     inplace=True,
#     errors="ignore"
# )


# # ====================================================
# # SAVE
# # ====================================================

# parquet_df.to_parquet(
#     OUTPUT_FILE,
#     index=False
# )

# print("\nSaved:")
# print(OUTPUT_FILE)