import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
from io import StringIO
import csv
from datetime import date
from gspread_utils import init_gspread

df = pd.read_csv("jobs/deepmind/data/deepmind_raw.csv")

df["New"] = df["Title"].str.endswith("New").map({True: "True", False: ""})
df["Title"] = df["Title"].str.replace(r"New$", "", regex=True)

df = df[df["Location"].str.contains("California", na=False)]
df.drop(columns=["Department"], inplace=True)

for s in [
    "ABP",
    "Architect",
    "Business Operations",
    "Business Partner",
    "Compensation",
    "Director",
    "Electrical Engineer",
    "Ethics",
    "Front-End",
    "iOS Mobile",
    "iOS/Swift",
    "Manager",
    "micro-architect",
    "Nuclear Engineer",
    "People & Culture",
    "People Experience",
    "People & Talent",
    "Principal",
    "Product Designer",
    "Psychologist",
    "Research Scientist",
    "Security Lead",
    "Senior Data Scientist",
    "Senior Laboratory",
    "Senior Security",
    "Senior Staff",
    "Silicon",
    "Staff Data Scientist",
    "Staff Research",
    "Stagiaire de niveau",
    "Team Lead, Research Engineering",
    "Visual Designer",
    "Writer",
]:
    p = len(df)
    df = df[~df["Title"].str.contains(s, na=False)]
    print(f"Removed {s} rows: {p - len(df)}")
df.sort_values(by="Title", inplace=True)
df = df[["New", "Title", "URL", "Location"]]
print(df["Title"].to_string(index=False))
print(f"\n{len(df)} jobs remaining")

gc = init_gspread()
sh = gc.open("DeepMind Jobs")

sheet_name = date.today().isoformat()
existing = {w.title for w in sh.worksheets()}
if sheet_name in existing:
    n = 2
    while f"{sheet_name}.{n}" in existing:
        n += 1
    sheet_name = f"{sheet_name}.{n}"

ws = sh.add_worksheet(title=sheet_name, rows=len(df) + 1, cols=len(df.columns))

csv_buf = StringIO()
df.to_csv(csv_buf, index=False)
rows = list(csv.reader(StringIO(csv_buf.getvalue())))
ws.update(rows, value_input_option="USER_ENTERED")
print(f"Uploaded {len(rows) - 1} rows to new sheet '{sheet_name}'")
