# Geographic Behavioral Heatmap Analytics

A compact analytics pipeline that generates synthetic geolocated users and behavioral events, performs simple geographic and temporal analyses, clusters events into geographic hotspots using DBSCAN, and exports CSV and HTML outputs for quick inspection and demos.

## Why this project

- Useful for building demos, proofs-of-concept, or tests for location-based features when real geospatial event data is not available.

## Features

- Synthetic dataset generation of users distributed across a configurable set of cities (India by default).
- Event generation biased toward evenings and weekends to mimic typical engagement patterns.
- Temporal analyses: hour × weekday heatmap, peak hour detection, weekend vs weekday counts.
- Geographic analyses: users per city and DBSCAN-based hotspot clustering.
- Interactive Folium map with city circle markers, an event density HeatMap, and cluster center circles.
- Outputs saved as CSVs and an HTML map for easy inspection.

## Files

- **location_insights_pipeline.py** — main script. When run it:
  - Generates **users_geo.csv** (generated users with lat/lon, city, match success).
  - Generates **events_geo.csv** (per-user events with timestamp and jittered location).
  - Saves an interactive map **user_distribution_map.html**.
  - Prints console summaries for users per city, hourly heatmap, cluster summary, and top-5 recommended event zones.

## Requirements

- Python 3.8+ recommended.

**Python packages (install via pip):**

```bash
pip install numpy pandas folium scikit-learn
```

**Geopandas and Shapely (required, recommended via conda):**

```bash
# Recommended for geopandas/shapely due to native dependencies
conda install -c conda-forge geopandas shapely
```

If geopandas installation fails with pip, prefer conda-forge (`conda install -c conda-forge geopandas`). Some systems need GDAL/GEOS installed.

## Quickstart

1. Clone or download the repository.
2. Create a Python virtual environment and install dependencies.
3. Run the script:

```bash
python location_insights_pipeline.py
```

After running you'll find:

- **users_geo.csv** — generated user locations and metadata.
- **events_geo.csv** — generated event-level rows (timestamp, lat, lon, user).
- **user_distribution_map.html** — interactive map with city markers, heatmap, and clusters.

## What the script does (high level)

- Sets random seeds for reproducibility.
- Defines a list of cities (default list contains 20 Indian cities) and constants like NUM_USERS.
- Generates synthetic users (**users_geo.csv**) with small jitter around city centroids and a per-user "user_match_success" score.
- Generates events per user between START_DATE and TODAY, biased toward evening hours and weekends, producing **events_geo.csv**.
- Computes users per city, hourly × weekday pivot table, peak usage hour, and weekend vs weekday counts.
- Performs DBSCAN clustering over event coordinates to identify geographic hotspots and produces a cluster summary.
- Builds a Folium map with circle markers sized by user count, HeatMap representing event density, and circles marking cluster centers.
- Scores cities using a normalized combination of users, events, and avg_user_match_success to recommend top 5 event launch zones.

## Configurable constants (at top of location_insights_pipeline.py)

- **NUM_USERS** — total number of users to synthesize (default 500).
- **CITIES** — list of tuples (name, lat, lon) — change to target different regions/cities.
- **TIMEZONE** — timezone label (stored with users but not applied to timezone-aware datetimes by default).
- **START_DATE** — derived from TODAY - timedelta(days=60) by default; adjust to change event window.
- **DBSCAN parameters**: eps and min_samples (set in the DBSCAN constructor in the script).
- **HeatMap parameters**: radius and blur (configured where HeatMap is added).
- **Random seeds**: random.seed(42) and np.random.seed(42) for reproducibility.

## Understanding outputs

### users_geo.csv

- **Columns**: user_id, city, lat, lon, timezone, user_match_success
- user_match_success is synthetic (0..1) and can be used as a quality metric in scoring.

### events_geo.csv

- **Columns**: user_id, city, lat, lon, event_time, hour, weekday, is_weekend
- Contains event-level timestamps and jittered lat/lon around the user city.

### Console outputs

- Users per city and average match success.
- Hourly usage pivot table (hour × weekday).
- Peak hour and weekend vs weekday counts.
- DBSCAN cluster summary listing cluster id, events count, average lat/lon.
- Top-5 recommended cities with computed event_zone_score.

### user_distribution_map.html

- Interactive map centered on India by default.
- Circle markers for cities (size proportional to user count).
- Density heatmap of events.
- Circles marking DBSCAN cluster centers.

## Customization ideas

- Replace CITIES with another country's cities or custom coordinates.
- Replace synthetic event generator with real event data by reading an events CSV and skipping generation steps.
- Tune DBSCAN parameters or try other clustering algorithms (e.g., HDBSCAN, KMeans with spatial weighting).
- Add timezone-aware timestamps if integrating real data across timezones.
- Add additional behavioral attributes (event type, duration) to the synthetic generator for richer analysis.
- Export cluster polygons (convex hulls) instead of center circles for more precise hotspot shapes.

## Troubleshooting

- **Folium map appears blank**: ensure user_distribution_map.html is opened via a browser (not as raw text) and that the event coordinates are valid lat/lon pairs.
- **Geopandas import/installation issues**: prefer installing via conda-forge (`conda install -c conda-forge geopandas`) or ensure system libs (GEOS, GDAL) are installed.
- **DBSCAN returning only -1 (noise)**: try increasing eps or lowering min_samples.

## Contributing

- Contributions are welcome. Open an issue or a pull request with proposed changes.

## License

- MIT License — feel free to reuse and adapt.
