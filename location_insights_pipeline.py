import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import DBSCAN

import folium
from folium.plugins import HeatMap

# -------------------------------------------------------------------
# 1. CONFIG: Cities & Basic Parameters
# -------------------------------------------------------------------

random.seed(42)
np.random.seed(42)

NUM_USERS = 500

# 20 Indian cities with approximate coordinates
CITIES = [
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.7041, 77.1025),
    ("Bengaluru", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Chennai", 13.0827, 80.2707),
    ("Kolkata", 22.5726, 88.3639),
    ("Pune", 18.5204, 73.8567),
    ("Jaipur", 26.9124, 75.7873),
    ("Surat", 21.1702, 72.8311),
    ("Lucknow", 26.8467, 80.9462),
    ("Kanpur", 26.4499, 80.3319),
    ("Nagpur", 21.1458, 79.0882),
    ("Indore", 22.7196, 75.8577),
    ("Bhopal", 23.2599, 77.4126),
    ("Patna", 25.5941, 85.1376),
    ("Vadodara", 22.3072, 73.1812),
    ("Coimbatore", 11.0168, 76.9558),
    ("Kochi", 9.9312, 76.2673),
    ("Visakhapatnam", 17.6868, 83.2185),
]

TIMEZONE = "Asia/Kolkata"  # all India

# Synthetic date range for events (last 60 days)
TODAY = datetime.now()
START_DATE = TODAY - timedelta(days=60)

# -------------------------------------------------------------------
# 2. GENERATE MOCK USER DATA (500 users across 20 cities)
# -------------------------------------------------------------------

def generate_users(num_users=NUM_USERS):
    user_ids = [f"U{str(i).zfill(4)}" for i in range(1, num_users + 1)]

    # Assign each user to a city (roughly balanced but random)
    city_choices = np.random.choice(len(CITIES), size=num_users, replace=True)

    cities = []
    lats = []
    lons = []
    timezones = []

    for idx in city_choices:
        name, lat, lon = CITIES[idx]
        cities.append(name)
        # Add tiny random jitter so users are not exactly same point
        lats.append(lat + np.random.normal(0, 0.05))
        lons.append(lon + np.random.normal(0, 0.05))
        timezones.append(TIMEZONE)

    # Mock match success rate at user level (later aggregated by city)
    # (0–1 continuous; later we average per city)
    match_success = np.clip(np.random.normal(0.6, 0.15, size=num_users), 0, 1)

    users_df = pd.DataFrame({
        "user_id": user_ids,
        "city": cities,
        "lat": lats,
        "lon": lons,
        "timezone": timezones,
        "user_match_success": match_success,
    })

    return users_df


users_df = generate_users()

# Save for EOD submission
users_df.to_csv("users_geo.csv", index=False)
print("Saved users_geo.csv")

# -------------------------------------------------------------------
# 3. GENERATE MOCK BEHAVIORAL EVENTS
# -------------------------------------------------------------------

def generate_events(users_df, min_events=10, max_events=40):
    """
    For each user, generate [min_events, max_events] events between START_DATE and TODAY.
    Events biased toward evenings and weekends.
    """
    events = []

    for _, row in users_df.iterrows():
        user_id = row["user_id"]
        city = row["city"]
        lat = row["lat"]
        lon = row["lon"]

        num_events = random.randint(min_events, max_events)
        for _ in range(num_events):
            # Random day in range
            days_offset = random.randint(0, (TODAY - START_DATE).days)
            base_date = START_DATE + timedelta(days=days_offset)

            # Bias time-of-day to evenings (17-23h) and late afternoons
            # Draw hour from mixture: 70% evening, 30% other
            if random.random() < 0.7:
                hour = random.randint(17, 23)
            else:
                hour = random.randint(8, 23)

            minute = random.randint(0, 59)
            event_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            weekday = event_time.weekday()  # 0=Mon, 6=Sun
            is_weekend = 1 if weekday >= 5 else 0

            events.append({
                "user_id": user_id,
                "city": city,
                "lat": lat + np.random.normal(0, 0.01),  # small jitter per event
                "lon": lon + np.random.normal(0, 0.01),
                "event_time": event_time,
                "hour": hour,
                "weekday": weekday,
                "is_weekend": is_weekend,
            })

    events_df = pd.DataFrame(events)
    return events_df


events_df = generate_events(users_df)
events_df.to_csv("events_geo.csv", index=False)
print("Saved events_geo.csv")

# -------------------------------------------------------------------
# 4. GEOGRAPHIC DISTRIBUTION ANALYSIS
# -------------------------------------------------------------------

# Users per city
users_per_city = users_df.groupby("city").agg(
    users=("user_id", "nunique"),
    avg_user_match_success=("user_match_success", "mean"),
).reset_index()

print("\n=== Users per City & Avg User Match Success ===")
print(users_per_city.sort_values("users", ascending=False))

# Match success by region (here "region" == city, but you can group further by state/zone)
# For demonstration, we’ll just re-use users_per_city.

# -------------------------------------------------------------------
# 5. BEHAVIORAL HEATMAP: PEAK USAGE TIMES
# -------------------------------------------------------------------

# Hourly activity by weekday
hourly_pivot = events_df.pivot_table(
    index="hour",
    columns="weekday",
    values="user_id",
    aggfunc="count",
    fill_value=0,
)

hourly_pivot.columns = [f"weekday_{c}" for c in hourly_pivot.columns]

print("\n=== Hourly Usage Heatmap (hour x weekday) ===")
print(hourly_pivot)

# Peak hour overall
hourly_counts = events_df.groupby("hour")["user_id"].count()
peak_hour = hourly_counts.idxmax()
print(f"\nPeak usage hour (overall): {peak_hour}:00")

# Weekend vs weekday
weekend_stats = events_df.groupby("is_weekend")["user_id"].count().rename({0: "weekday", 1: "weekend"})
print("\n=== Weekend vs Weekday Events ===")
print(weekend_stats)

# -------------------------------------------------------------------
# 6. DBSCAN CLUSTERING FOR GEOGRAPHIC HOTSPOTS
# -------------------------------------------------------------------

# Use lat/lon directly with a rough eps in degrees (~0.5 degrees ~ 50km)
coords = events_df[["lat", "lon"]].values

# Adjust eps and min_samples to tune cluster granularity
dbscan = DBSCAN(eps=0.5, min_samples=30, metric="euclidean")
cluster_labels = dbscan.fit_predict(coords)

events_df["cluster"] = cluster_labels

# Summary of clusters (ignore noise label -1)
cluster_summary = (
    events_df[events_df["cluster"] >= 0]
    .groupby("cluster")
    .agg(
        events=("user_id", "count"),
        avg_lat=("lat", "mean"),
        avg_lon=("lon", "mean"),
    )
    .reset_index()
    .sort_values("events", ascending=False)
)

print("\n=== Geographic Hotspot Clusters (DBSCAN) ===")
print(cluster_summary)

# -------------------------------------------------------------------
# 7. INTERACTIVE MAP WITH FOLIUM
# -------------------------------------------------------------------

# Base map centered roughly on India
india_center = [20.5937, 78.9629]
m = folium.Map(location=india_center, zoom_start=5)

# 7.1 City-level markers sized by user count
for _, row in users_per_city.iterrows():
    city = row["city"]
    # Use the average coordinates of users in that city
    city_users = users_df[users_df["city"] == city]
    mean_lat = city_users["lat"].mean()
    mean_lon = city_users["lon"].mean()
    user_count = row["users"]

    folium.CircleMarker(
        location=[mean_lat, mean_lon],
        radius=4 + user_count / 30,  # radius scales with users
        popup=f"{city}: {user_count} users",
        tooltip=f"{city}: {user_count} users",
        fill=True,
        fill_opacity=0.7,
    ).add_to(m)

# 7.2 Heatmap of events (density)
heat_data = events_df[["lat", "lon"]].dropna().values.tolist()
HeatMap(heat_data, radius=10, blur=15).add_to(m)

# 7.3 Mark cluster centers for hotspots
for _, row in cluster_summary.iterrows():
    folium.Circle(
        location=[row["avg_lat"], row["avg_lon"]],
        radius=50000,  # 50 km radius
        popup=f"Cluster {row['cluster']} - {row['events']} events",
        tooltip=f"Hotspot Cluster {row['cluster']}",
        fill=False,
    ).add_to(m)

# Save HTML map
MAP_FILENAME = "user_distribution_map.html"
m.save(MAP_FILENAME)
print(f"\nSaved interactive map to {MAP_FILENAME}")

# -------------------------------------------------------------------
# 8. EVENT ZONE RECOMMENDATIONS (TOP 5 CITIES)
# -------------------------------------------------------------------

# We can combine:
#  - users per city
#  - aggregated events per city
#  - avg match success
events_per_city = events_df.groupby("city")["user_id"].count().rename("events")
city_metrics = users_per_city.merge(events_per_city, on="city")

# Simple score: weighted sum (tweak weights as needed)
# Normalize each metric to 0-1
for col in ["users", "events", "avg_user_match_success"]:
    col_min = city_metrics[col].min()
    col_max = city_metrics[col].max()
    if col_max == col_min:
        city_metrics[f"{col}_norm"] = 0.0
    else:
        city_metrics[f"{col}_norm"] = (city_metrics[col] - col_min) / (col_max - col_min)

# Score = 0.4 * users + 0.4 * events + 0.2 * avg_match_success
city_metrics["event_zone_score"] = (
    0.4 * city_metrics["users_norm"]
    + 0.4 * city_metrics["events_norm"]
    + 0.2 * city_metrics["avg_user_match_success_norm"]
)

top5_cities = city_metrics.sort_values("event_zone_score", ascending=False).head(5)

print("\n=== Recommended Event Launch Zones (Top 5 Cities) ===")
print(top5_cities[["city", "users", "events", "avg_user_match_success", "event_zone_score"]])
