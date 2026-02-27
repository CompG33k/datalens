<div align="center">

# 🔎 DataLens  
### Intelligent Dataset Explorer

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue" />
  <img src="https://img.shields.io/badge/Streamlit-App-red" />
  <img src="https://img.shields.io/badge/Plotly-Visualization-green" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

**Upload. Explore. Understand.**

</div>

---

## 🚀 Overview

**DataLens** is an open-source intelligent dataset visualization engine.

Upload a **JSON** or **CSV** file and DataLens will:

- 🔍 Automatically detect tabular structures (even in nested JSON)
- 🧠 Profile schema (datetime, numeric, categorical columns)
- 📊 Recommend the most appropriate chart (line, bar, scatter)
- 🎛 Enable dynamic filtering and slicing
- ⚡ Support large datasets interactively
- 🛠 Allow manual chart override controls

Zero configuration required.

---

## 🛠 Tech Stack

- **Python**
- **Streamlit**
- **Plotly**
- **Pandas**

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/datalens.git
cd datalens
```

---

### 2️⃣ Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it:

**Windows (PowerShell)**

```bash
.\.venv\Scripts\Activate.ps1
```

**Mac / Linux**

```bash
source .venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run DataLens

```bash
python -m streamlit run app.py
```

Your browser will open automatically at:

```
http://localhost:8501
```

---

## 🧠 How It Works

DataLens operates in four stages:

### 1️⃣ Table Extraction
Recursively detects list-of-record tables inside nested JSON structures.

### 2️⃣ Schema Profiling
Classifies columns into:
- Datetime
- Numeric
- Categorical

### 3️⃣ Chart Recommendation Engine
Applies heuristic logic:

- Datetime + Numeric → Line chart  
- Categorical + Numeric → Bar chart (Top-N)  
- Numeric + Numeric → Scatter plot  
- Otherwise → Table fallback  

### 4️⃣ Interactive Rendering
Renders optimized visualizations with dynamic filters using Plotly.

---

## 🎯 Example Use Cases

- Exploring layoffs datasets  
- Financial data inspection  
- API response visualization  
- Rapid dataset prototyping  
- Pre-analysis data profiling  

---

## 📦 v1.0.0 Release Notes

**Initial Public Release**

- Automatic nested JSON table detection  
- Schema-aware visualization engine  
- Heuristic-based chart recommendation  
- Interactive filtering (date + category)  
- Top-N aggregation support  
- Manual chart override controls  
- Clean Streamlit interface  

---

## 🗺 Roadmap

- 🤖 AI-generated insight summaries  
- 🧮 Chart scoring model  
- 📈 Statistical summary panel  
- 📤 Export to PNG / CSV  
- ☁️ Cloud deployment version  
- ⚡ Large dataset performance optimization  

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Built as an open-source data visualization engine focused on intelligent schema-aware exploration.

---

<div align="center">

**DataLens — See Your Data Clearly.**

</div>