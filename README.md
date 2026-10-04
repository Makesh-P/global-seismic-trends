# Global Seismic Trends

Data-driven earthquake insights built from USGS data: an end-to-end pipeline that collects, cleans and stores earthquake records in MySQL, answers analytical questions with SQL, and presents the results in an interactive Streamlit dashboard.

## Overview

The project collects about five years of global earthquake records from the USGS Earthquake Catalog API, cleans and enriches them with Pandas and regular expressions, and loads them into a MySQL database. A Streamlit dashboard then shows an overview of the data and runs 26 SQL analyses on demand.

## Features

- Automated monthly data retrieval from the USGS API
- Data cleaning: type conversion, missing-value handling and text standardisation
- Regex extraction of distance, direction, locality and country from the raw `place` field
- Derived columns: year, month, day, day of week, depth category and magnitude category
- 26 SQL analyses covering magnitude, depth, time patterns, tsunami flags, alert levels and regional trends
- Streamlit dashboard with key metrics, an earthquake map and charts

## Tech Stack

| Area | Tools |
|---|---|
| Language | Python |
| Data processing | Pandas, Regex |
| Database | MySQL, SQLAlchemy, PyMySQL |
| Dashboard | Streamlit |
| Data source | USGS Earthquake Catalog API (GeoJSON) |

## Project Structure

```
global-seismic-trends/
├── seismic_etl.py          # Extract, transform and load: API to MySQL
├── seismic_dashboard.py    # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- MySQL Server 8.0 or later (the analyses use window functions)

### Installation

```bash
git clone https://github.com/Makesh-P/global-seismic-trends.git
cd global-seismic-trends
pip install -r requirements.txt
```

### Configure the database connection

Both scripts connect to a local MySQL server. Open `seismic_etl.py` and `seismic_dashboard.py` and set the host, user and password to match your setup. The scripts use a database named `earthquake_db` and a table named `earthquake`.

### Run

1. Build the database. This downloads the data, cleans it and loads it into MySQL. It makes one API request per month, so it takes a few minutes.

   ```bash
   python seismic_etl.py
   ```

2. Start the dashboard.

   ```bash
   streamlit run seismic_dashboard.py
   ```

## Data

- **Source:** USGS Earthquake Catalog API
- **Period:** January 2021 to the collection date
- **Filter:** magnitude 4.0 and above
- **Time zone:** all timestamps are UTC

### Cleaning

- Numeric fields (`mag`, `depth_km`, `nst`, `dmin`, `rms`, `gap`, `sig`) are converted to numbers and missing values are filled with the median
- `felt` (the number of "Did You Feel It?" reports) is filled with 0 where no reports exist
- Text fields are trimmed and lower-cased; a missing `alert` is set to `unknown`
- Five fields that the GeoJSON feed does not provide (`magError`, `depthError`, `magNst`, `locationSource`, `magSource`) are dropped as entirely empty
- `place` is split into `distance_km`, `direction`, `locality` and `country`
- Country names are standardised: US states become United States, and oceans, ridges and seas are grouped as Ocean/Other

### Derived columns

| Column | Definition |
|---|---|
| `year`, `month`, `day`, `day_of_week` | Parts of the event time |
| `depth_category` | Shallow (under 70 km), Intermediate (70 to 300 km), Deep (300 km and above) |
| `mag_category` | Light (under 5), Moderate (5 to 6), Strong (6 to 7), Destructive (7 and above) |

## Dashboard

- **Overview:** five key metrics, a map of earthquake locations, and charts by year, magnitude category, depth category and tsunami-flagged events
- **SQL Analysis:** choose a question from the list and run its query against the database


## Author

**Makesh P**
[LinkedIn](https://www.linkedin.com/in/makesh-p-54759b2a9?utm_source=share_via&utm_content=profile&utm_medium=member_android) | [GitHub](https://github.com/Makesh-P)

## Acknowledgements

Earthquake data provided by the [U.S. Geological Survey](https://earthquake.usgs.gov/).
