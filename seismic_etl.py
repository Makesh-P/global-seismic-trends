import requests
import pandas as pd
import pymysql
from datetime import datetime
from sqlalchemy import create_engine

# DATA COLLECTION (USGS API)

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
all_records = []

end_date = datetime.now()
start_date = end_date.replace(year=end_date.year - 5)

for year in range(start_date.year, end_date.year + 1):
    for month in range(1, 13):
        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year+1}-01-01"
        else:
            end = f"{year}-{month+1:02d}-01"

        if datetime.strptime(start, "%Y-%m-%d") > end_date:
            continue
        if datetime.strptime(end, "%Y-%m-%d") > end_date:
            end = end_date.strftime("%Y-%m-%d")

        params = {
            "format": "geojson",
            "starttime": start,
            "endtime": end,
            "minmagnitude": 4
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Request failed for {start}: {response.status_code}")
            continue
        data = response.json()

        for f in data["features"]:
            p = f["properties"]
            g = f["geometry"]["coordinates"]
            all_records.append({
                "id": f.get("id"),
                "time": pd.to_datetime(p.get("time"), unit="ms"),
                "updated": pd.to_datetime(p.get("updated"), unit="ms"),
                "latitude": g[1] if g else None,
                "longitude": g[0] if g else None,
                "depth_km": g[2] if g else None,
                "mag": p.get("mag"),
                "magType": p.get("magType"),
                "place": p.get("place"),
                "status": p.get("status"),
                "tsunami": p.get("tsunami"),
                "felt": p.get("felt"),
                "alert": p.get("alert"),
                "sig": p.get("sig"),
                "net": p.get("net"),
                "nst": p.get("nst"),
                "dmin": p.get("dmin"),
                "rms": p.get("rms"),
                "gap": p.get("gap"),
                "magError": p.get("magError"),
                "depthError": p.get("depthError"),
                "magNst": p.get("magNst"),
                "locationSource": p.get("locationSource"),
                "magSource": p.get("magSource"),
                "types": p.get("types"),
                "ids": p.get("ids"),
                "sources": p.get("sources"),
                "type": p.get("type")
            })

df = pd.DataFrame(all_records)
print("Raw data shape:", df.shape)

# 2.DATA INSPECTION

print(df.head())
print(df.dtypes)

#  Column types and missing values
numerical_col = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
categorical_col = df.select_dtypes(include="object").columns.tolist()

null_check = df.isnull().sum()
null_num = null_check[numerical_col]
null_cat = null_check[categorical_col]
print("numerical_col:")
print(null_num)   # nst, dmin, rms, gap (numerical)
print("categorical_col:")
print(null_cat)   # magError, depthError, magNst, locationSource, magSource 

# Duplicate check
check_col = df.duplicated().tolist()
res_t = []
res_f = []
for i in check_col:
    if i == True:
        res_t.append(i)

    else:
        res_f.append(i)

print("no. of true:", len(res_t))
print("no. of false:", len(res_f))
# NO duplicate in this df


# CLEANING - NUMERIC COLUMNS

df_1 = df.copy()
num_col = ["mag", "depth_km", "nst", "dmin", "rms", "gap", "sig"]

# Reason:Why median and not mean: before filling
for col in num_col:
    print(col, "→ mean:", df[col].mean(), "| median:", df[col].median(), "| missing:", df[col].isnull().sum())

#Convert to numbers and fillna(median)
for col in num_col:
    df_1[col] = pd.to_numeric(df_1[col], errors="coerce")
    df_1[col] = df_1[col].fillna(df_1[col].median())
print(df_1[num_col].isnull().sum())

# felt 
df_1["felt"] = pd.to_numeric(df_1["felt"], errors="coerce").fillna(0).astype(int)

# CLEANING - TEXT COLUMNS

text_col = ["magType", "status", "type", "net", "sources", "types", "alert"]
for col in text_col:
    df_1[col] = df_1[col].str.strip().str.lower()

df_1["alert"] = df_1["alert"].fillna("unknown")

# REGEX - EXTRACT INFORMATION FROM plac(col)

#Distance, direction, locality and country

df_1["distance_km"] = df_1["place"].str.extract(r"^(\d+)\s*km")[0].astype(float)
df_1["direction"] = df_1["place"].str.extract(r"km\s+([NSEW]+)\s+of")[0]
df_1["locality"] = df_1["place"].str.extract(r"of\s+(.+?),")[0]

df_1["country"] = df_1["place"].str.extract(r",\s*([^,]+)$")[0]
df_1["country"] = df_1["country"].fillna(df_1["place"])

# Country cleanup: " region", direction prefixes, Fiji Islands
df_1["country"] = df_1["country"].str.replace(" region", "", regex=False)

df_1["country"] = df_1["country"].str.replace(
    r"^(north|south|east|west|northeast|northwest|southeast|southwest) of (the )?",
    "", regex=True, case=False)

df_1["country"] = df_1["country"].replace("Fiji Islands", "Fiji")

# Remove "earthquake" / "earthquake sequence"
df_1["country"] = df_1["country"].str.replace(
    r"\bearthquake( sequence)?\b", "", regex=True, case=False
).str.strip()

# US states and state codes -> United States
us = ["Alaska", "Hawaii", "California", "Nevada", "Oklahoma", "Texas", "Washington", "Oregon",
      "CA", "NV", "AK", "HI", "OK", "TX", "WA", "OR"]
df_1["country"] = df_1["country"].replace(us, "United States")

print(df_1["country"].nunique())
print(df_1["country"].value_counts().head(30))

# Oceans, ridges and seas are not countries -> Ocean/Other (Replaced)
ocean = df_1["country"].str.contains("Ridge|Rise|Ocean|Sea|Trench|Fracture|Rift|Plateau|Basin", case=False)
df_1.loc[ocean, "country"] = "Ocean/Other"

print(df_1["country"].nunique())

# DATA PREPARATION - DERIVED COLUMNS (as mentioned in DOC)

# Date-based columns
df_1["year"] = df_1["time"].dt.year
df_1["month"] = df_1["time"].dt.month
df_1["day"] = df_1["time"].dt.day
df_1["day_of_week"] = df_1["time"].dt.day_name()


# Shallow / deep earthquake flag (based on depth_km)
def depth_category(depth):
    if depth < 70:
        return "Shallow"
    elif depth < 300:
        return "Intermediate"
    else:
        return "Deep"

df_1["depth_category"] = df_1["depth_km"].apply(depth_category)

# Strong / destructive earthquake flag (based on magnitude)
def magnitude_category(mag):
    if mag < 5.0:
        return "Light"
    elif mag < 6.0:
        return "Moderate"
    elif mag < 7.0:
        return "Strong"
    else:
        return "Destructive"


df_1["mag_category"] = df_1["mag"].apply(magnitude_category)

# Drop columns that are 100% null 
cols_to_drop = ["magError", "depthError", "magNst", "locationSource", "magSource"]
df_1.drop(columns=cols_to_drop, inplace=True)


# FINAL CHECKS
print("Final data shape:", df_1.shape)
print(df_1.isnull().sum())
print(df_1.isnull().sum().sum())
print(df_1.duplicated(subset="id").sum())


# LOAD INTO MYSQL

# Create the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="makesh28"
)

cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS earthquake_db")
cursor.close()
connection.close()

print("Database created successfully")

# Create the table and insert the data
engine = create_engine(
    f"mysql+pymysql://root:makesh28@localhost:3306/earthquake_db"
)

df_1.to_sql(
    "earthquake",
    con=engine,
    if_exists="replace",
    index=False
)

print("Table created and data inserted successfully")