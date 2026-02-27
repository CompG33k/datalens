import json
from typing import Any, Dict, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------
# DataLens — Intelligent Dataset Explorer
# ----------------------------
st.set_page_config(page_title="DataLens", layout="wide")
st.title("🔎 DataLens — Intelligent Dataset Explorer")
st.caption("Upload JSON/CSV → auto-detect table(s) → recommend an appropriate chart → filter interactively.")

# ---------- JSON table extraction ----------
COMMON_LIST_KEYS = ["data", "series", "results", "observations", "items", "rows", "records"]

def _is_list_of_dicts(x: Any) -> bool:
    return isinstance(x, list) and len(x) > 0 and all(isinstance(i, dict) for i in x)

def _json_tables(obj: Any, prefix: str = "") -> List[Tuple[str, pd.DataFrame]]:
    """Recursively find list[dict] tables inside JSON."""
    tables: List[Tuple[str, pd.DataFrame]] = []

    if _is_list_of_dicts(obj):
        tables.append((prefix or "table", pd.DataFrame(obj)))
        return tables

    if isinstance(obj, dict):
        # 1) direct list-of-dicts under keys
        for k, v in obj.items():
            if _is_list_of_dicts(v):
                name = f"{prefix}{k}" if prefix else k
                tables.append((name, pd.DataFrame(v)))

        # 2) common container keys
        for k in COMMON_LIST_KEYS:
            if k in obj and _is_list_of_dicts(obj[k]):
                name = f"{prefix}{k}" if prefix else k
                tables.append((name, pd.DataFrame(obj[k])))

        # 3) recursive
        for k, v in obj.items():
            if isinstance(v, dict):
                new_prefix = f"{prefix}{k}." if prefix else f"{k}."
                tables.extend(_json_tables(v, new_prefix))

    return tables

def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Attempt datetime parsing
    for c in out.columns:
        if out[c].dtype == "object":
            parsed = pd.to_datetime(out[c], errors="coerce", infer_datetime_format=True)
            if len(out) > 0 and parsed.notna().mean() >= 0.6:
                out[c] = parsed

    # Attempt numeric parsing on remaining object cols
    for c in out.columns:
        if out[c].dtype == "object":
            s = out[c].astype(str).str.replace(",", "", regex=False)
            num = pd.to_numeric(s, errors="coerce")
            if len(out) > 0 and num.notna().mean() >= 0.6:
                out[c] = num

    return out

def _detect_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    types = {"datetime": [], "numeric": [], "categorical": []}
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            types["datetime"].append(c)
        elif pd.api.types.is_numeric_dtype(df[c]):
            types["numeric"].append(c)
        else:
            types["categorical"].append(c)
    return types

def _recommend_chart(df: pd.DataFrame, types: Dict[str, List[str]]) -> Dict[str, Any]:
    """Heuristic chart recommender."""
    dt = types["datetime"]
    num = types["numeric"]
    cat = types["categorical"]

    # Time series
    if dt and num:
        return {"kind": "line", "x": dt[0], "y": num[0], "color": None}

    # Category + numeric
    if cat and num:
        # pick lowest-cardinality categorical as default x
        best_cat = min(cat, key=lambda c: df[c].nunique(dropna=True))
        orientation = "h" if df[best_cat].nunique(dropna=True) <= 40 else "v"
        return {"kind": "bar", "x": best_cat, "y": num[0], "color": None, "orientation": orientation}

    # Scatter
    if len(num) >= 2:
        return {"kind": "scatter", "x": num[0], "y": num[1], "color": None}

    return {"kind": "table"}

def _apply_filters(df: pd.DataFrame, types: Dict[str, List[str]]) -> pd.DataFrame:
    out = df.copy()
    st.sidebar.subheader("Filters")

    # Datetime filter (one column)
    if types["datetime"]:
        dt_col = st.sidebar.selectbox("Date column", types["datetime"], index=0)
        if out[dt_col].notna().any():
            dmin = out[dt_col].min()
            dmax = out[dt_col].max()
            start, end = st.sidebar.date_input(
                "Date range",
                value=(dmin.date(), dmax.date()),
                min_value=dmin.date(),
                max_value=dmax.date(),
            )
            start_ts = pd.to_datetime(start)
            end_ts = pd.to_datetime(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            out = out[(out[dt_col] >= start_ts) & (out[dt_col] <= end_ts)]

    # Categorical filters (avoid very high-cardinality)
    for c in types["categorical"]:
        nunique = out[c].nunique(dropna=True)
        if nunique == 0 or nunique > 200:
            continue
        values = sorted(out[c].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect(f"{c} ({nunique})", values, default=[])
        if selected:
            out = out[out[c].astype(str).isin(selected)]

    return out

def _render_chart(df: pd.DataFrame, rec: Dict[str, Any]) -> None:
    kind = rec.get("kind", "table")

    if kind == "table":
        st.info("Not enough structure to recommend a chart. Showing the table.")
        return

    if kind == "line":
        x, y = rec["x"], rec["y"]
        if pd.api.types.is_datetime64_any_dtype(df[x]):
            df = df.sort_values(x)
        fig = px.line(df, x=x, y=y, markers=True, title=f"{y} over {x}")
        st.plotly_chart(fig, use_container_width=True)
        return

    if kind == "bar":
        x, y = rec["x"], rec["y"]
        orientation = rec.get("orientation", "v")

        top_n = st.slider("Top N categories", 5, 50, 15)
        agg = df.groupby(x, dropna=True)[y].sum().reset_index()
        agg = agg.sort_values(y, ascending=False).head(top_n)

        fig = px.bar(
            agg,
            x=y if orientation == "h" else x,
            y=x if orientation == "h" else y,
            orientation=orientation,
            title=f"Top {top_n}: {y} by {x}",
            text=y if orientation == "v" else None,
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    if kind == "scatter":
        x, y = rec["x"], rec["y"]
        fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
        st.plotly_chart(fig, use_container_width=True)
        return

    st.info("Unknown chart recommendation. Showing table.")

# ---------- UI ----------
st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload a JSON or CSV", type=["json", "csv"])
st.sidebar.caption("Tip: upload your layoffs JSON file to see multiple auto-detected tables.")

if not uploaded:
    st.info("Upload a file to start. Supported: JSON (nested OK) and CSV.")
    st.stop()

filename = uploaded.name.lower()

if filename.endswith(".csv"):
    df = pd.read_csv(uploaded)
    tables = [("csv", df)]
else:
    raw = uploaded.read()
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception:
        st.error("Could not parse JSON. Make sure the file is valid UTF-8 JSON.")
        st.stop()

    tables = _json_tables(obj)

    # If JSON is a dict[str/int]->number, convert to a table
    if not tables and isinstance(obj, dict):
        flat = [(k, v) for k, v in obj.items() if isinstance(v, (int, float))]
        if flat:
            tables = [("dict", pd.DataFrame(flat, columns=["key", "value"]))]

    if not tables:
        st.warning("No list-of-records tables found in this JSON.")
        if isinstance(obj, dict):
            st.write(list(obj.keys()))
        st.stop()

# Select a table inside JSON
table_names = [t[0] for t in tables]
selected_name = st.sidebar.selectbox("Select table", table_names, index=0)
df = next(d for (n, d) in tables if n == selected_name)

df = _coerce_types(df)

# Preview
st.subheader(f"Table: {selected_name}")
st.write(f"Rows: {len(df):,} | Columns: {len(df.columns):,}")
st.dataframe(df, use_container_width=True, height=380)

# Types + filters
types = _detect_types(df)
filtered = _apply_filters(df, types)

st.subheader("Visualization")
st.write(f"Filtered rows: {len(filtered):,}")

# Recommend + allow override
rec = _recommend_chart(filtered, types)
st.sidebar.subheader("Chart")
chart_kind = st.sidebar.selectbox("Chart type", ["auto", "line", "bar", "scatter", "table"], index=0)

if chart_kind != "auto":
    rec["kind"] = chart_kind
    if chart_kind in ["line", "bar"]:
        x_options = types["datetime"] + types["categorical"] + types["numeric"]
        y_options = types["numeric"]
        if x_options:
            rec["x"] = st.sidebar.selectbox("X axis", x_options, index=0)
        if y_options:
            rec["y"] = st.sidebar.selectbox("Y axis", y_options, index=0)
    elif chart_kind == "scatter":
        y_options = types["numeric"]
        if len(y_options) >= 2:
            rec["x"] = st.sidebar.selectbox("X axis", y_options, index=0)
            rec["y"] = st.sidebar.selectbox("Y axis", y_options, index=1)

_render_chart(filtered, rec)

st.markdown("---")
st.caption("DataLens is open-source. Extend recommenders, transforms, and connectors as you grow.")
