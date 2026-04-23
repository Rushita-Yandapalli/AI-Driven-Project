# 🌾 Food Price Volatility Analysis System — India

> A scalable Big Data analytics platform for agricultural commodity price analysis,
> built with **PySpark · Apache Hive · Streamlit · Plotly · FastAPI**

---

## 📸 Dashboard Preview

The interactive Streamlit dashboard includes:
- **6 analytical tabs**: Price Trends, Volatility, Anomalies, Seasonal, City Comparison, Raw Data
- **Dynamic filters**: Commodity, City, Date Range, Z-Score threshold
- **KPI cards** and **insight panels**
- **10+ interactive Plotly charts**

---

## 🏗️ Architecture

```
food_price_volatility/
├── data/
│   ├── agmarknet_data.csv          ← Raw dataset (50,000 records)
│   └── generate_dataset.py         ← Synthetic data generator
│
├── spark_jobs/
│   └── spark_processor.py          ← PySpark ETL pipeline
│
├── backend/
│   ├── analytics.py                ← Core analytics engine (Pandas)
│   └── api.py                      ← FastAPI REST API
│
├── frontend/
│   └── app.py                      ← Streamlit dashboard (main app)
│
├── hive_queries/
│   └── food_price_queries.hql      ← Hive DDL + analytical queries
│
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit dashboard
```bash
streamlit run frontend/app.py
```

The app opens at **http://localhost:8501**

---

## ⚙️ Tech Stack

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Big Data Engine  | Apache Spark (PySpark)              |
| Data Warehouse   | Apache Hive                         |
| Analytics Engine | Pandas, NumPy, SciPy                |
| Backend API      | FastAPI + Uvicorn                   |
| Dashboard        | Streamlit + Plotly                  |
| Anomaly Method   | Z-score (per commodity × city pair) |

---

## 📊 Dataset Schema

| Column         | Renamed From   | Type     | Description                    |
|---------------|----------------|----------|--------------------------------|
| State          | —              | string   | Indian state                   |
| District       | —              | string   | District name                  |
| city           | Market         | string   | Market/city name               |
| commodity      | Commodity      | string   | Agricultural commodity         |
| Variety        | —              | string   | Crop variety                   |
| Grade          | —              | string   | Quality grade                  |
| date           | Arrival_Date   | date     | Market arrival date            |
| Min_Price      | —              | float    | Minimum price (₹/Quintal)      |
| Max_Price      | —              | float    | Maximum price (₹/Quintal)      |
| price          | Modal_Price    | float    | Modal/most common price        |
| avg_price      | *engineered*   | float    | (Min+Max+Modal)/3              |
| year/month/day | *engineered*   | int      | Date components                |

---

## 📈 Features

### 1. Time-Series Analysis
- Daily, monthly, yearly price trends
- 7-period and 30-period moving averages
- Multi-commodity comparison charts

### 2. Price Volatility
- Standard deviation and Coefficient of Variation (CV%)
- Commodity-wise and city-wise volatility rankings
- Risk-return scatter map

### 3. Anomaly Detection (Z-Score)
- `z = (price − mean) / stddev` per (commodity, city) pair
- Configurable threshold (default: |z| > 2.0)
- Spike vs. Drop classification
- Interactive anomaly scatter plot

### 4. Seasonal Analysis
- Month-wise aggregation
- Commodity × Month price heatmap
- Polar/radar seasonal chart

### 5. City-wise Comparison
- Average price ranking by city
- Volatility comparison
- Commodity × City matrix heatmap
- Box plot distributions

---

## 🔌 REST API Endpoints

Start the API server:
```bash
uvicorn backend.api:app --reload --port 8000
```

| Endpoint              | Method | Description                          |
|-----------------------|--------|--------------------------------------|
| `/health`             | GET    | Health check                         |
| `/prices`             | GET    | Paginated price records              |
| `/trends`             | GET    | Price trend (D/M/Y frequency)        |
| `/volatility`         | GET    | Commodity or city volatility         |
| `/anomalies`          | GET    | Detected anomalies                   |
| `/cities`             | GET    | Available cities                     |
| `/city-comparison`    | GET    | City-wise aggregated stats           |
| `/seasonal`           | GET    | Monthly seasonal patterns            |

Query parameters: `commodity`, `city`, `start_date`, `end_date`, `z_threshold`

---

## ⚡ PySpark Job

Run the Spark ETL pipeline:
```bash
# With Spark installed:
spark-submit spark_jobs/spark_processor.py data/agmarknet_data.csv ./spark_output

# Without Spark (falls back to Pandas automatically):
python spark_jobs/spark_processor.py
```

Outputs:
- `spark_output/monthly_trends/` — Parquet files
- `spark_output/volatility_commodity/` — Parquet files
- `spark_output/anomalies/` — Parquet files

---

## 🐝 Hive Setup

```bash
# Start Hive shell
hive

# Run queries
hive -f hive_queries/food_price_queries.hql
```

Key Hive views created:
- `vw_monthly_trend` — Monthly aggregations
- `vw_commodity_volatility` — Volatility rankings
- `vw_city_volatility` — City-wise volatility
- `vw_anomalies` — Z-score anomaly detection
- `vw_seasonal` — Month-wise seasonal patterns

---

## 🌾 Commodities Covered

Tomato · Onion · Potato · Rice · Wheat · Maize · Garlic · Ginger ·
Cauliflower · Cabbage · Brinjal · Bitter Gourd

---

## 🏙️ Markets Covered (50 cities, 10 states)

Maharashtra · Uttar Pradesh · Karnataka · Tamil Nadu · Rajasthan ·
Punjab · Gujarat · West Bengal · Madhya Pradesh · Andhra Pradesh

---

## 📦 Performance Optimizations

- **Caching**: `@st.cache_data` for all heavy operations
- **Sampling**: Scatter plots sample 5000 points for performance
- **Spark**: Partitioning + caching (`df.cache()`)
- **Pandas**: Vectorized operations throughout

---

## 👤 Author

Built for academic/portfolio demonstration of Big Data analytics systems.
Data is synthetic (generated to mimic real Agmarknet patterns).
