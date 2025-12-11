# Geographic Behavioral Heatmap Analytics

A compact analytics pipeline that generates synthetic geolocated users and behavioral events, performs basic geographic and temporal analyses, identifies geographic hotspots via clustering, and produces CSV and interactive HTML outputs for quick inspection.

This README documents purpose, requirements, usage, outputs, configuration, and customization notes for the repository's main script: `location_insights_pipeline.py`.

---

## Features

- Synthetic generation of users distributed across configurable cities (India by default).
- Event generation biased toward evenings and weekends.
- Temporal analyses: hour × weekday heatmap, peak hour, weekend vs weekday counts.
- Geographic analyses: users per city and DBSCAN-based hotspot clustering.
- Interactive Folium map with city markers, event heatmap, and hotspot circles.
- CSV and HTML outputs for downstream analysis or visualization.

---

## Requirements

- Python 3.8+ recommended
- Python packages (install with pip or prefer conda for geopandas/shapely):
  - numpy
  - pandas
  - geopandas
  - shapely
  - scikit-learn
  - folium

Install (pip):
```bash
pip install numpy pandas geopandas shapely scikit-learn folium
```

Note: geopandas and shapely can require system libraries (GEOS, GDAL). If pip installation fails, conda is usually easier:

```bash
conda install -c conda-forge geopandas
```

---

## Quickstart

1. Clone or download the repository (or place `location_insights_pipeline.py` in your working directory).
2. Create a Python virtual environment and install dependencies.
3. Run the script:

```bash
python location_insights_pipeline.py
```

---

## Outputs

After running the script you will find:

- `users_geo.csv` — generated user locations and metadata.
  - Columns: `user_id`, `city`, `lat`, `lon`, `timezone`, `user_match_success`
- `events_geo.csv` — generated event-level rows (timestamp, lat, lon, user).
  - Columns: `user_id`, `city`, `lat`, `lon`, `event_time`, `hour`, `weekday`, `is_weekend`
- `user_distribution_map.html` — interactive Folium map with:
  - Circle markers at mean city locations sized by user count
  - A heatmap layer of events density
  - Circles marking DBSCAN cluster centers

Console outputs:
- Users per city and average match success
- Hourly usage pivot table (hour × weekday)
- Peak hour and weekend vs weekday counts
- DBSCAN cluster summary (cluster id, events count, average lat/lon)
- Top-5 recommended cities based on a combined event zone score

---

## What the script does (high level)

- Sets random seeds (`random.seed(42)` and `np.random.seed(42)`) for reproducibility.
- Defines a list of cities (20 Indian cities by default) and configurable constants such as `NUM_USERS`.
- Generates synthetic users (saved to `users_geo.csv`) with small jitter around city centroids and a `user_match_success` score (0..1).
- Generates events per user across a time window (default: last ~60 days) biased toward evening hours and weekends (saved to `events_geo.csv`).
- Computes:
  - Users per city (count and average match success)
  - Hour × weekday pivot table and peak hour
  - Weekend vs weekday event counts
- Performs DBSCAN clustering over event coordinates to identify geographic hotspots and produce a `cluster_summary`.
- Builds a Folium map (`user_distribution_map.html`) with city markers, an event density HeatMap, and cluster centers.
- Ranks cities by a normalized combination of users, events, and average user match success to recommend top event launch zones.

---

## Configurable constants

Top of `location_insights_pipeline.py` contains constants you can adjust:

- `NUM_USERS` — total number of synthetic users (default: 500)
- `CITIES` — list of tuples `(name, lat, lon)` — replace with target regions/cities
- `TIMEZONE` — timezone label stored with users (not timezone-aware datetimes by default)
- `START_DATE` — derived from TODAY - timedelta(days=60) by default; adjust to change event window
- DBSCAN parameters: `eps` and `min_samples` (set where DBSCAN is constructed)
- HeatMap parameters: `radius` and `blur` (configured in Folium HeatMap)
- Random seeds: change seeds or remove for non-deterministic synthetic data

---

## Customization ideas

- Replace `CITIES` with a different country's cities or use custom coordinates.
- Replace the synthetic generator with real event data:
  - Provide `events_df` with columns `user_id`, `city`, `lat`, `lon`, `event_time` and skip generation.
  - Ensure `users_df` has `user_id`, `city`, `lat`, `lon`, and an optional quality metric like `user_match_success`.
- Tune DBSCAN parameters or try other clustering algorithms (HDBSCAN, spatial KMeans).
- Produce cluster polygons (convex hulls) instead of center circles for precise hotspot shapes.
- Add timezone-aware timestamps when working with users across multiple timezones.
- Add richer behavioral attributes (event type, duration) in the synthetic generator.

---

## Troubleshooting

- Folium map appears blank: open `user_distribution_map.html` in a browser (not as raw text). Verify event coordinates are valid lat/lon pairs.
- Geopandas import/installation issues: prefer conda-forge installation or ensure system libs (GEOS, GDAL) are installed.
- DBSCAN returns only `-1` (noise): try increasing `eps` or reducing `min_samples`.

---

## Extending to real data

If replacing synthetic generation with real users/events:
- Ensure `events_df` columns: `user_id`, `city`, `lat`, `lon`, `event_time` (datetime)
- Ensure `users_df` columns: `user_id`, `city`, `lat`, `lon`, `user_match_success` (or similar)
- Handle timezone-aware datetimes, validate coordinates, drop NaNs as needed

---

## License

MIT License — feel free to reuse and adapt.
