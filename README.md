Geographic Behavioral Heatmap Analytics
A compact analytics pipeline that generates synthetic geolocated user and behavioral event data, performs basic geographic and temporal analyses, clusters events into geographic hotspots, and produces an interactive Folium map and CSV outputs.

This repository contains a single main script:

location_insights_pipeline.py — generates mock users/events, computes usage heatmaps and DBSCAN clusters, and saves CSV and HTML outputs.
I created this README based on the contents of location_insights_pipeline.py to explain purpose, setup, usage, outputs, and customization options.

Features
Synthetic dataset generation of users distributed across a set of cities (India by default).
Event generation biased toward evenings and weekends.
Temporal analyses: hourly x weekday heatmap, peak hour, weekend vs weekday counts.
Geographic analyses: users per city and DBSCAN-based hotspot clustering.
Interactive Folium map showing city markers, heatmap of events, and hotspot circles.
Outputs saved as CSVs and an HTML map for quick inspection.
Files
location_insights_pipeline.py
The main Python script. When run it:
Generates users_geo.csv (generated users with lat/lon, city, match success).
Generates events_geo.csv (per-user events with timestamp and location jitter).
Saves an interactive map user_distribution_map.html.
Prints console summaries for users per city, hourly heatmap, cluster summary, and top-5 recommended event zones.
Requirements
Python 3.8+ recommended.

Python packages (install via pip; note some packages may require system dependencies):

numpy
pandas
geopandas
shapely
scikit-learn
folium
Example (may require system packages for geopandas/shapely):

pip install numpy pandas geopandas shapely scikit-learn folium

If geopandas installation fails, follow OS-specific install instructions (conda is usually easiest: conda install -c conda-forge geopandas).

Quickstart
Clone or download this repository (or place location_insights_pipeline.py in a working directory).
Create a Python virtualenv and install the dependencies.
Run the script:
python location_insights_pipeline.py

After running you'll find:
users_geo.csv — generated user locations and metadata.
events_geo.csv — generated event-level rows (timestamp, lat, lon, user).
user_distribution_map.html — interactive map with city markers, heatmap, and clusters.
Open user_distribution_map.html in a browser to explore.

What the script does (high level)
Sets random seeds for reproducibility.
Defines a list of cities (default list contains 20 Indian cities) and constants like NUM_USERS.
Generates synthetic users (users_geo.csv) with a small jitter around city centroids and a per-user "match success" score.
Generates events per user between START_DATE and TODAY, biased toward evening hours and weekends, producing events_geo.csv.
Computes:
Users per city (counts and average match success).
Hour × weekday pivot table and peak usage hour.
Weekend vs weekday event counts.
Performs DBSCAN clustering over event coordinates to identify geographic hotspots and produces a cluster_summary.
Builds a Folium map:
Circle markers at mean city locations sized by user count.
HeatMap representing event density.
Circles marking cluster centers.
Scores cities using a normalized combination of users, events, and avg_user_match_success to recommend top 5 event launch zones.
Configurable constants (top of script)
NUM_USERS — total number of users to synthesize (default 500).
CITIES — list of tuples (name, lat, lon) — change to target different regions/cities.
TIMEZONE — timezone label (not used for timezone-aware datetimes, but stored).
START_DATE — derived from TODAY - timedelta(days=60) by default; adjust to change event window.
DBSCAN parameters: eps and min_samples (set in the DBSCAN constructor).
HeatMap parameters: radius and blur (configured where HeatMap is added).
Random seeds: random.seed(42) and np.random.seed(42) for reproducibility.
Understanding outputs
users_geo.csv

Columns: user_id, city, lat, lon, timezone, user_match_success
user_match_success is synthetic (0..1) and can be used as a quality metric in scoring.
events_geo.csv

Columns: user_id, city, lat, lon, event_time, hour, weekday, is_weekend
Contains event-level timestamps and jittered lat/lon around the user city.
Console outputs

Users per city and average match success.
Hourly usage pivot table (hour × weekday).
Peak hour and weekend vs weekday counts.
DBSCAN cluster_summary listing cluster id, events count, average lat/lon.
Top-5 recommended cities with computed event_zone_score.
user_distribution_map.html

Interactive map centered on India by default.
Circle markers for cities (size proportional to user count).
Density heatmap of events.
Circles marking DBSCAN cluster centers.
Customization ideas
Replace CITIES with another country's cities or custom coordinates.
Replace synthetic event generator with real event data by reading an events CSV and skipping generation steps.
Tune DBSCAN parameters or try other clustering algorithms (e.g., HDBSCAN, KMeans with spatial weighting).
Add timezone-aware timestamps if integrating real data across timezones.
Add additional behavioral attributes (event type, duration) to the synthetic generator for richer analysis.
Export cluster polygons (convex hulls) instead of center circles for more precise hotspot shapes.
Troubleshooting
Folium map appears blank: ensure user_distribution_map.html is opened via a browser (not as raw text) and that the event coordinates are valid lat/lon pairs.
Geopandas import/installation issues: prefer installing via conda-forge (conda install -c conda-forge geopandas) or ensure system libs (GEOS, GDAL) are installed.
DBSCAN returning only -1 (noise): try increasing eps or lowering min_samples.
Extending to real data
If you replace synthetic generation with real users/events:

Ensure events_df has columns: user_id, city, lat, lon, event_time (datetime).
Ensure users_df has user_id, city, lat, lon, user_match_success (or similar metric).
Adjust timezone handling and data validation (dropping NaNs, coordinate ranges).
License
MIT License — feel free to reuse and adapt.
