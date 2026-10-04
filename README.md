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

## Key Findings

- **Strongest events:** all ten strongest earthquakes are M7.7 or higher. The largest is M8.8 in Russia (July 2025), followed by M8.2 in the United States (July 2021) and two M8.1 events (South Sandwich Islands, August 2021; New Zealand region, March 2021).
- **Busiest year:** 2025 has the most earthquakes (18,298). The final year in the data is incomplete.
- **Time patterns are close to uniform.** Friday leads the weekdays with 13,695 events, but that is only about 14.6% of the total, against 14.3% for an even split. Hourly counts range from 3,682 (12:00 UTC) to 4,210 (03:00 UTC), so there is no meaningful daily or weekly cycle.
- **Monthly counts favour January to September,** because those months have six years of data and October to December have five. August (9,381) leads for that reason as well as any seasonal effect.
- **Most active regions:** Indonesia (9,560 events), Japan (7,275) and Russia (6,421). Their average magnitudes are nearly identical (about 4.50), so the ranking is driven by frequency, not strength.
- **Highest average magnitudes occur in remote regions** (Tristan da Cunha, Micronesia, Balleny Islands). This probably reflects sparse seismic station coverage, where only larger events are detected, and does not mean higher hazard.
- **Shallow earthquakes dominate.** Among countries with at least five deep events, New Zealand (about 144 shallow per deep event) and the Solomon Islands (about 105) have the highest shallow-to-deep ratios.
- **One network reports almost everything:** the `us` network accounts for roughly 99% of events.

## Recommendations

- **Governments and urban planners:** prioritise building codes and emergency planning in the most active and shallow-dominated regions, since shallow quakes produce stronger shaking near the epicentre.
- **Insurers:** weigh exposure by event frequency in high-activity countries, and treat average magnitude alone as a weak risk signal.
- **Researchers:** account for detection limits in remote regions, and for uneven time coverage, when comparing months or years.

## Author

**Makesh P**
[LinkedIn](https://www.linkedin.com/in/makesh-p-54759b2a9?utm_source=share_via&utm_content=profile&utm_medium=member_android) | [GitHub](https://github.com/Makesh-P)

## Acknowledgements

Earthquake data provided by the [U.S. Geological Survey](https://earthquake.usgs.gov/).
