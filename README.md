# 💧 Machine Learning for Water Safety: Potability Prediction in Bangkok’s Canals

This project focuses on predicting the **Water Quality Index (WQI)** for various canal locations in Bangkok using a machine learning model. It visualizes real water parameter data and predicts safety levels using a trained regression model. The application combines interactive dashboards, geospatial mapping, and predictive analytics.

---

## 🧪 Project Overview

This is a course project for **AT82.03 Machine Learning**, supervised by **Dr. Chaklam Silpasuwanchai** at the **Asian Institute of Technology** (AIT), Thailand.

We utilize a real-world dataset containing water quality metrics across Bangkok's canal systems and use a regression model to predict potability based on physical and chemical properties such as:

- pH
- DO (Dissolved Oxygen)
- BOD (Biochemical Oxygen Demand)
- COD (Chemical Oxygen Demand)
- Coliform levels
- TDS (Suspended Solids)
- Nitrate, Nitrite, and Ammonia levels

---

## 🔍 Features

- 📈 **Interactive Dashboard**: View trends of water quality metrics by canal and year.
- 🗺️ **Map View**: See live data points with safety indicators using color-coded markers.
- 🧠 **Prediction Page**: Input parameters and get WQI predictions with a gauge visualization.
- 📊 **Gauge Visualization**: Visually interpret the WQI and water safety category (Safe / Unsafe).

---

## ⚙️ Tech Stack

- [Dash](https://dash.plotly.com/) (Plotly + Flask) for the frontend UI
- [Pandas](https://pandas.pydata.org/) for data handling
- [Scikit-learn](https://scikit-learn.org/) for ML model (log-linear regression)
- [Dash Leaflet](https://dash-leaflet.herokuapp.com/) for the interactive map
- [Bootstrap](https://dash-bootstrap-components.opensource.faculty.ai/) styling

---

## 🚀 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/puskr99/ml-project-water-potability.git
   ```

2. **Install dependencies**
   We recommend using a virtual environment.
   ```bash
   pip install -r req.txt
   ```

4. **Run the app**
   ```bash
   python app/app.py
   ```

5. **Access the app**
   Open `http://127.0.0.1:8050/` in your browser.

---

## 📂 Project Structure

```
.
├── app.py                  # Main Dash app with routing
├── map.py                  # Map layout & logic
├── data/
│   ├── water.csv           # Water quality data
├── code/
│   ├── wpp_model_weight.pkl # Trained ML model
│   └── scaler.dump          # Feature scaler used in prediction
└── README.md
```

---

## 👩‍💻 Contributors

- **Inisha Pradhan**  
  _Information Management, AIT_  
  📧 st125563@ait.asia

- **Neha Shrestha**  
  _Information Management, AIT_  
  📧 st124963@ait.asia

- **Puskar Adhikari**  
  _Computer Science, AIT_  
  📧 st125098@ait.asia

- **Shreeyukta Pradhanang**  
  _Computer Science, AIT_  
  📧 st125168@ait.asia

---

## 📚 Acknowledgment

Special thanks to **Dr. Chaklam Silpasuwanchai** for guiding us through this project as part of the AT82.03 Machine Learning course at **Asian Institute of Technology (AIT)**.

---


## 🌐 Live Website

🔗 [https://ml-project-water-potability.onrender.com](#)  

---