import streamlit as st
import pandas as pd

st.set_page_config(page_title="Car Sharing Dashboard", layout="wide")
st.title("Car Sharing Dashboard")

# ---- Load Data ----
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# ---- Merge DataFrames ----
# Merge trips with cars (joining on car_id)
trips_merged = trips.merge(cars, left_on="car_id", right_on="id", suffixes=("", "_car"))

# Merge with cities for car's city (joining on city_id)
trips_merged = trips_merged.merge(cities, on="city_id")

# ---- Clean useless columns ----
trips_merged = trips_merged.drop(columns=["id_car", "city_id", "customer_id", "id"])

# ---- Update Trips Date Format ----
trips_merged["pickup_date"] = pd.to_datetime(trips_merged["pickup_time"]).dt.date
trips_merged["dropoff_date"] = pd.to_datetime(trips_merged["dropoff_time"]).dt.date

# Compute trip duration in hours
trips_merged["trip_duration_hours"] = (
    pd.to_datetime(trips_merged["dropoff_time"]) - pd.to_datetime(trips_merged["pickup_time"])
).dt.total_seconds() / 3600

# ---- Sidebar Filters ----
st.sidebar.header("Filters")
cars_brand = st.sidebar.multiselect(
    "Select the Car Brand",
    options=trips_merged["brand"].unique(),
    default=trips_merged["brand"].unique(),
)

if cars_brand:
    trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# ---- Business Metrics ----
st.subheader("Business Metrics")

total_trips = len(trips_merged)
total_distance = trips_merged["distance"].sum()
# Car model with the highest revenue
revenue_by_model = trips_merged.groupby("model")["revenue"].sum()
top_car = revenue_by_model.idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Trips", value=total_trips)
with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)
with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

# ---- Preview Data ----
st.subheader("Data Preview")
st.write(trips_merged.head())

# ---- Visualizations ----
st.subheader("Visualizations")

# 1. Trips Over Time
st.markdown("### Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size().reset_index(name="trips_count")
trips_over_time = trips_over_time.set_index("pickup_date")
st.line_chart(trips_over_time["trips_count"])

# 2. Revenue Per Car Model
st.markdown("### Revenue Per Car Model")
revenue_model = trips_merged.groupby("model")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(revenue_model)

# 3. Cumulative Revenue Growth Over Time
st.markdown("### Cumulative Revenue Growth Over Time")
revenue_over_time = trips_merged.groupby("pickup_date")["revenue"].sum().sort_index().cumsum()
st.area_chart(revenue_over_time)

# 4. Number of Trips Per Car Model
st.markdown("### Number of Trips Per Car Model")
trips_per_model = trips_merged.groupby("model").size().sort_values(ascending=False)
trips_per_model.name = "trips"
st.bar_chart(trips_per_model)

# 5. Average Trip Duration by City
st.markdown("### Average Trip Duration by City (hours)")
avg_duration_city = trips_merged.groupby("city_name")["trip_duration_hours"].mean()
st.bar_chart(avg_duration_city)

# 6. Revenue by City
st.markdown("### Revenue by City")
revenue_city = trips_merged.groupby("city_name")["revenue"].sum()
st.bar_chart(revenue_city)

# 7. Bonus: Average Revenue per Trip by Brand
st.markdown("### Average Revenue per Trip by Brand (Bonus)")
avg_rev_brand = trips_merged.groupby("brand")["revenue"].mean().sort_values(ascending=False)
st.bar_chart(avg_rev_brand)
