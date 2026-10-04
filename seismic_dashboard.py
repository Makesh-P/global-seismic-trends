import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Global Seismic Trends",
    layout="wide"
)

# Database connection

engine = create_engine(
    f"mysql+pymysql://root:makesh28@localhost:3306/earthquake_db"
)

queries = {

    "1. Top 10 strongest earthquakes (magnitude)": """
        SELECT id, country, mag, mag_category, time
        FROM earthquake
        ORDER BY mag DESC
        LIMIT 10
    """,

    "2. Top 10 deepest earthquakes (depth)": """
        SELECT id, country, depth_km, depth_category, time
        FROM earthquake
        ORDER BY depth_km DESC
        LIMIT 10
    """,

    "3. Shallow earthquakes (<50 km) with magnitude >7.5": """
        SELECT id, depth_km, mag, country, time
        FROM earthquake
        WHERE depth_km < 50 AND mag > 7.5
        ORDER BY mag DESC
    """,

    "4. Average depth per continent":
        "Not available: the dataset has no continent column.",

    "5. Average magnitude per magnitude type": """
        SELECT magType, AVG(mag) AS Avg_mag
        FROM earthquake
        GROUP BY magType
    """,

    "6. Year with the most earthquakes": """
        SELECT year, COUNT(type) AS Earthquake
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY year
        ORDER BY Earthquake DESC
        LIMIT 1
    """,

    "7. Month with the highest number of earthquakes": """
        SELECT month, COUNT(type) AS Earthquake
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY month
        ORDER BY Earthquake DESC
        LIMIT 1
    """,

    "8. Day of the week with the most earthquakes": """
        SELECT day_of_week AS Day, COUNT(type) AS Earthquake
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY day_of_week
        ORDER BY Earthquake DESC
        LIMIT 1
    """,

    "9. Number of earthquakes per hour": """
        SELECT HOUR(time) AS per_hour, COUNT(*) AS Count
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY per_hour
        ORDER BY per_hour
    """,

    "10. Most active reporting network": """
        SELECT net, COUNT(*) AS no_of_network
        FROM earthquake
        GROUP BY net
        ORDER BY no_of_network DESC
        LIMIT 5
    """,

    "11. Top 5 places with highest casualties": """
        SELECT country, MAX(felt) AS casualties
        FROM earthquake
        GROUP BY country
        ORDER BY casualties DESC
        LIMIT 5
    """,

    "12. Total estimated economic loss per continent":
        "Not available: the dataset has no economic loss or continent column.",

    "13. Average economic loss by alert level": """
        SELECT alert, COUNT(*) AS Count
        FROM earthquake
        GROUP BY alert
    """,

    "14. Reviewed vs automatic earthquakes": """
        SELECT status, COUNT(*) AS Count
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY status
    """,

    "15. Number of earthquakes by earthquake type": """
        SELECT type, COUNT(*) AS Events_count
        FROM earthquake
        GROUP BY type
        ORDER BY Events_count DESC
    """,

    "16. Number of earthquakes by data type": """
        SELECT types, COUNT(*) AS Count
        FROM earthquake
        GROUP BY types
        ORDER BY Count DESC
    """,

    "17. Average RMS and gap per continent":
        "Not available: the dataset has no continent column.",

    "18. Events with high station coverage (nst > threshold)": """
        SELECT *
        FROM earthquake
        WHERE nst > 50
    """,

    "19. Number of tsunamis triggered per year": """
        SELECT year, COUNT(*) AS Tsunami_Count
        FROM earthquake
        WHERE tsunami = 1
        GROUP BY year
        ORDER BY year
    """,

    "20. Number of earthquakes by alert level": """
        SELECT alert, COUNT(*) AS earthquake_counts
        FROM earthquake
        GROUP BY alert
        ORDER BY earthquake_counts DESC
    """,

    "21. Top 5 countries with the highest avg magnitude of earthquakes": """
        SELECT country, COUNT(*) AS events, ROUND(AVG(mag), 2) AS avg_magnitude
        FROM earthquake
        WHERE type = 'earthquake'
          AND time >= (SELECT MAX(time) FROM earthquake) - INTERVAL 5 YEAR
        GROUP BY country
        HAVING COUNT(*) >= 20
        ORDER BY avg_magnitude DESC
        LIMIT 5
    """,

    "22. Countries with shallow and deep earthquakes in the same month": """
        SELECT country, year, month
        FROM earthquake
        GROUP BY country, year, month
        HAVING
            SUM(depth_category = 'Shallow') > 0
            AND SUM(depth_category = 'Deep') > 0
    """,

    "23. Year-over-year earthquake growth rate": """
        SELECT year, earthquake_count,
               LAG(earthquake_count) OVER (ORDER BY year) AS previous_year,
               ROUND(
                   (
                       (earthquake_count -
                        LAG(earthquake_count) OVER (ORDER BY year))
                       / LAG(earthquake_count) OVER (ORDER BY year)
                   ) * 100, 2
               ) AS growth_pct
        FROM (
            SELECT year, COUNT(*) AS earthquake_count
            FROM earthquake
            WHERE type = "earthquake"
            GROUP BY year
        ) AS yearly
        ORDER BY year
    """,

    "24. Top 3 seismically active regions": """
        SELECT country, COUNT(*) AS freq, AVG(mag) AS avg_mag,
               (COUNT(*) * AVG(mag)) AS Score
        FROM earthquake
        GROUP BY country
        ORDER BY Score DESC
        LIMIT 3
    """,

    "25. Average earthquake depth within ± 5° of the equator": """
        SELECT country, AVG(depth_km) AS avg_depth_km
        FROM earthquake
        WHERE latitude BETWEEN -5 AND 5
        GROUP BY country
    """,

    "26. Countries with the highest shallow-to-deep earthquake ratio": """
        SELECT country , 
                SUM(depth_category = 'Shallow') as Shallow_count,
                SUM(depth_category = 'Deep') as Deep_count,
                ROUND(SUM(depth_category='Shallow') / NULLIF(SUM(depth_category='Deep'),0), 2) AS ratio
        from earthquake
        group by country
        HAVING Deep_count > 0 
        order by Ratio DESC
        LIMIT 10;
    """,

    "27. Average magnitude difference: tsunami vs non-tsunami": """
        SELECT
            AVG(CASE WHEN tsunami = 1 THEN mag END) AS with_tsunami,
            AVG(CASE WHEN tsunami = 0 THEN mag END) AS without_tsunami,
            AVG(CASE WHEN tsunami = 1 THEN mag END) -
            AVG(CASE WHEN tsunami = 0 THEN mag END) AS Difference
        FROM earthquake
    """,

    "28. Events with the lowest data reliability": """
        SELECT id, country, mag, gap, rms
        FROM earthquake
        ORDER BY gap DESC, rms DESC
        LIMIT 10
    """,

    "29. Consecutive earthquakes within 50 km and 1 hour":
        """Not available : it needs a pairwise time-and-distance comparison between events.""",

    "30. Regions with the highest frequency of deep earthquakes": """
        SELECT country, COUNT(*) AS Deep_events
        FROM earthquake
        WHERE depth_category = "Deep"
        GROUP BY country
        ORDER BY Deep_events DESC
        LIMIT 10
    """
}

# Cached database helpers

@st.cache_data(ttl=300)
def read_sql(query):
    return pd.read_sql(query, engine)


@st.cache_data(ttl=300)
def get_overview_data():
    total = pd.read_sql(
        "SELECT COUNT(*) AS total FROM earthquake", engine
    ).iloc[0, 0]

    avg_mag = pd.read_sql(
        "SELECT AVG(mag) AS value FROM earthquake", engine
    ).iloc[0, 0]

    max_mag = pd.read_sql(
        "SELECT MAX(mag) AS value FROM earthquake", engine
    ).iloc[0, 0]

    max_depth = pd.read_sql(
        "SELECT MAX(depth_km) AS value FROM earthquake", engine
    ).iloc[0, 0]

    yearly = pd.read_sql("""
        SELECT year, COUNT(*) AS earthquakes
        FROM earthquake
        WHERE type = "earthquake"
        GROUP BY year
        ORDER BY year
    """, engine)

    magnitude = pd.read_sql("""
        SELECT mag_category, COUNT(*) AS earthquakes
        FROM earthquake
        GROUP BY mag_category
        ORDER BY earthquakes DESC
    """, engine)

    depth = pd.read_sql("""
        SELECT depth_category, COUNT(*) AS earthquakes
        FROM earthquake
        GROUP BY depth_category
        ORDER BY earthquakes DESC
    """, engine)

    tsunami = pd.read_sql("""
        SELECT year, COUNT(*) AS tsunami_events
        FROM earthquake
        WHERE tsunami = 1
        GROUP BY year
        ORDER BY year
    """, engine)

    map_data = pd.read_sql("""
        SELECT latitude, longitude, mag
        FROM earthquake
        WHERE type = 'earthquake' AND mag >= 5
    """, engine)
    map_data["size"] = map_data["mag"] ** 3 * 300

    return total, avg_mag, max_mag, max_depth, yearly, magnitude, depth, tsunami, map_data

# Header

st.title("Global Seismic Trends")

overview_tab, sql_tab= st.tabs(
    ["Overview", "SQL Analysis"]
)

# Overview

with overview_tab:

    try:
        (
            total,
            avg_mag,
            max_mag,
            max_depth,
            yearly,
            magnitude,
            depth,
            tsunami,
            map_data
        ) = get_overview_data()

        st.subheader("Key Metrics")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Total Earthquakes", f"{int(total):,}")
        c2.metric("Average Magnitude", f"{avg_mag:.2f}")
        c3.metric("Maximum Magnitude", f"{max_mag:.2f}")
        c4.metric("Maximum Depth", f"{max_depth:.2f} km")
        c5.metric("Tsunami Events", f"{tsunami['tsunami_events'].sum():,}")

        st.divider()

        st.subheader("Earthquake Locations")

        if not map_data.empty:
            st.map(
                map_data,
                latitude="latitude",
                longitude="longitude",
                size="mag"
            )
        else:
            st.info("No location data available for the map.")

        st.divider()

        chart_tab1, chart_tab2, chart_tab3 = st.tabs(
            ["Trends", "Magnitude", "Depth & Hazard"]
        )

        with chart_tab1:
            st.subheader("Earthquakes by Year")
            st.write(
                        "Shows how the number of recorded earthquakes changes by year."
                        )
            st.bar_chart(
                yearly.set_index("year")["earthquakes"]
            )

            

        with chart_tab2:
            st.subheader("Earthquakes by Magnitude Category")
            st.write(
                        "Shows the distribution of earthquakes across magnitude categories."
                        )
            st.bar_chart(
                magnitude.set_index("mag_category")["earthquakes"]
            )


        with chart_tab3:
            st.subheader("Earthquakes by Depth Category")
            st.write("Shows how many earthquakes are shallow, intermediate or deep.")
            st.bar_chart(
                depth.set_index("depth_category")["earthquakes"]
            )

            st.subheader("Tsunami Events by Year")
            st.write("Shows earthquakes by depth and yearly tsunami-flagged events.")
            if not tsunami.empty:
                st.bar_chart(
                    tsunami.set_index("year")["tsunami_events"]
                )
            else:
                st.info("No tsunami events found.")

    except Exception as e:
        st.error("Could not load the overview data.")
        st.exception(e)

# SQL Analysis

with sql_tab:

    st.subheader("Database Queries")

    task = st.selectbox("Select a question", list(queries.keys()))

    sql = queries[task]

    if sql.startswith("Not available"):
        st.info(sql)
    elif st.button("▶ Run Query", type="primary"):
        st.dataframe(read_sql(sql), use_container_width=True, hide_index=True)
