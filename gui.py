
import io
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(
    page_title="AI Data Intelligence Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.2);
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def read_uploaded_dataset(uploaded_file):
    """Read CSV or Excel data for interactive visualizations."""
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        try:
            return pd.read_csv(io.BytesIO(file_bytes))
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

    return pd.read_excel(io.BytesIO(file_bytes))


def make_numeric(df):
    """Return numeric columns, including safely convertible text columns."""
    result = df.copy()

    for column in result.columns:
        if not pd.api.types.is_numeric_dtype(result[column]):
            cleaned = (
                result[column]
                .astype("string")
                .str.replace(r"[$,₹€£%]", "", regex=True)
                .str.strip()
            )

            converted = pd.to_numeric(cleaned, errors="coerce")

            if converted.notna().sum() > 0:
                original_nonmissing = result[column].notna().sum()
                conversion_ratio = (
                    converted.notna().sum() / original_nonmissing
                    if original_nonmissing
                    else 0
                )

                if conversion_ratio >= 0.8:
                    result[column] = converted

    return result


def show_downloads(result, df):
    """Provide downloadable analysis files."""
    st.download_button(
        "⬇️ Download analysis report (JSON)",
        data=json.dumps(result, indent=2, default=str),
        file_name="data_analysis_report.json",
        mime="application/json",
    )

    st.download_button(
        "⬇️ Download dataset preview (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="dataset.csv",
        mime="text/csv",
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("📊 Data Intelligence")
    st.caption("Automated analytics workspace")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls"],
        help="Upload a CSV or Excel file. Avoid confidential personal data.",
    )

    st.info(
        "Upload a dataset, run the analysis, "
        "and explore the results in the dashboard."
    )

    analyze_button = st.button(
        "🚀 Analyze Dataset",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None,
    )

    st.divider()
    st.caption("Built with Python, FastAPI, Pandas, Streamlit and Plotly")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("AI Data Intelligence Agent")
st.write(
    "Explore your data, discover patterns, evaluate data quality, "
    "and create interactive visualizations."
)

if uploaded_file is None:
    st.info("👈 Upload a CSV or Excel dataset using the sidebar to begin.")
    st.markdown("### What you can explore")
    c1, c2, c3 = st.columns(3)

    c1.subheader("📋 Data profiling")
    c1.write("Dataset dimensions, column types, statistics and missing values.")

    c2.subheader("📈 Visual analytics")
    c2.write("Histograms, box plots, scatter plots and correlation heatmaps.")

    c3.subheader("💡 Data insights")
    c3.write("Outliers, category distributions, relationships and downloadable reports.")

    st.stop()


# --------------------------------------------------
# LOAD DATA AND CALL FASTAPI
# --------------------------------------------------

if analyze_button:
    try:
        with st.spinner("Profiling your dataset and generating insights..."):
            df = read_uploaded_dataset(uploaded_file)

            if df.empty:
                st.error("This dataset has no rows.")
                st.stop()

            response = requests.post(
                API_URL,
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream",
                    )
                },
                timeout=180,
            )

            if not response.ok:
                st.error(
                    f"Backend error ({response.status_code}): "
                    f"{response.text}"
                )
                st.stop()

            result = response.json()

            st.session_state["analysis_result"] = result
            st.session_state["analysis_df"] = df
            st.session_state["analysis_filename"] = uploaded_file.name

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to FastAPI. Start the backend in a separate terminal "
            "using: python -m uvicorn main:app --reload"
        )
        st.stop()

    except requests.exceptions.Timeout:
        st.error("The backend took too long to respond. Try a smaller dataset.")
        st.stop()

    except Exception as error:
        st.error(f"Unable to analyze the dataset: {error}")
        st.stop()


# --------------------------------------------------
# SHOW SAVED RESULTS
# --------------------------------------------------

if "analysis_result" not in st.session_state:
    st.warning("Click **Analyze Dataset** in the sidebar to generate your report.")
    st.stop()

result = st.session_state["analysis_result"]
df = st.session_state["analysis_df"]
profile = result.get("profile", {})
analysis = result.get("analysis", {})

numeric_df = make_numeric(df)
numeric_columns = numeric_df.select_dtypes(include="number").columns.tolist()
categorical_columns = df.select_dtypes(
    include=["object", "category", "string", "bool"]
).columns.tolist()

missing_total = int(df.isna().sum().sum())
duplicate_total = int(df.duplicated().sum())
missing_percent = (
    missing_total / (df.shape[0] * df.shape[1]) * 100
    if df.shape[0] * df.shape[1]
    else 0
)


# --------------------------------------------------
# TOP SUMMARY CARDS
# --------------------------------------------------

st.caption(f"Current dataset: {result.get('filename', uploaded_file.name)}")

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Total rows", f"{len(df):,}")
m2.metric("Total columns", f"{len(df.columns):,}")
m3.metric("Missing cells", f"{missing_total:,}")
m4.metric("Duplicate rows", f"{duplicate_total:,}")
m5.metric("Missing data", f"{missing_percent:.1f}%")

st.divider()


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------

overview_tab, explorer_tab, charts_tab, quality_tab, insights_tab, report_tab = (
    st.tabs([
        "🏠 Overview",
        "🔎 Data Explorer",
        "📊 Visualizations",
        "🧹 Data Quality",
        "💡 Insights",
        "📥 Reports",
    ])
)


# --------------------------------------------------
# TAB 1: OVERVIEW
# --------------------------------------------------

with overview_tab:
    st.subheader("Dataset Overview")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### Column data types")
        type_counts = df.dtypes.astype(str).value_counts().reset_index()
        type_counts.columns = ["Data type", "Columns"]

        fig = px.pie(
            type_counts,
            names="Data type",
            values="Columns",
            hole=0.45,
            title="Column type distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Missing values by column")
        missing_by_column = df.isna().sum()
        missing_by_column = missing_by_column[missing_by_column > 0]

        if not missing_by_column.empty:
            missing_frame = missing_by_column.sort_values().reset_index()
            missing_frame.columns = ["Column", "Missing values"]

            fig = px.bar(
                missing_frame,
                x="Missing values",
                y="Column",
                orientation="h",
                title="Columns with missing data",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("There are no missing values.")

    st.markdown("#### Statistical summary")
    if numeric_columns:
        st.dataframe(
            numeric_df[numeric_columns].describe().T,
            use_container_width=True,
        )
    else:
        st.info("No numeric columns were detected.")

    st.markdown("#### First 10 rows")
    st.dataframe(df.head(10), use_container_width=True)


# --------------------------------------------------
# TAB 2: DATA EXPLORER
# --------------------------------------------------

with explorer_tab:
    st.subheader("Explore Your Dataset")

    search_text = st.text_input("Search column names")
    filtered_columns = [
        column for column in df.columns
        if search_text.lower() in str(column).lower()
    ]

    selected_columns = st.multiselect(
        "Choose columns to display",
        options=filtered_columns,
        default=filtered_columns,
    )

    if selected_columns:
        st.dataframe(
            df[selected_columns],
            use_container_width=True,
            height=420,
        )
    else:
        st.warning("No columns match your search.")

    st.caption(f"Showing {len(df):,} total rows in the uploaded dataset.")


# --------------------------------------------------
# TAB 3: INTERACTIVE VISUALIZATIONS
# --------------------------------------------------

with charts_tab:
    st.subheader("Interactive Chart Studio")
    st.write("Choose a chart and the columns you want to explore.")

    chart_type = st.selectbox(
        "Chart type",
        [
            "Histogram",
            "Bar chart",
            "Box plot",
            "Scatter plot",
            "Line chart",
            "Correlation heatmap",
        ],
    )

    if chart_type == "Histogram":
        if numeric_columns:
            column = st.selectbox("Numeric column", numeric_columns)
            bins = st.slider("Number of bins", 5, 60, 20)

            fig = px.histogram(
                numeric_df,
                x=column,
                nbins=bins,
                title=f"Distribution of {column}",
                marginal="box",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available.")

    elif chart_type == "Bar chart":
        available = categorical_columns or df.columns.tolist()

        if available:
            column = st.selectbox("Category column", available)
            limit = st.slider("Maximum categories", 5, 30, 10)

            counts = (
                df[column].astype("string")
                .fillna("(Missing)")
                .value_counts()
                .head(limit)
                .reset_index()
            )
            counts.columns = [column, "Count"]

            fig = px.bar(
                counts,
                x=column,
                y="Count",
                title=f"Top values in {column}",
                text="Count",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No columns available.")

    elif chart_type == "Box plot":
        if numeric_columns:
            column = st.selectbox("Numeric column", numeric_columns)
            fig = px.box(
                numeric_df,
                y=column,
                points="outliers",
                title=f"Outlier view: {column}",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available.")

    elif chart_type == "Scatter plot":
        if len(numeric_columns) >= 2:
            x_column = st.selectbox("X-axis", numeric_columns, index=0)
            y_options = [c for c in numeric_columns if c != x_column]
            y_column = st.selectbox("Y-axis", y_options)

            color_options = ["None"] + categorical_columns
            color_column = st.selectbox("Color points by (optional)", color_options)

            fig = px.scatter(
                numeric_df,
                x=x_column,
                y=y_column,
                color=None if color_column == "None" else color_column,
                hover_data=[c for c in df.columns if c not in [x_column, y_column]][:5],
                title=f"{y_column} vs {x_column}",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("At least two numeric columns are needed for a scatter plot.")

    elif chart_type == "Line chart":
        if numeric_columns:
            x_options = df.columns.tolist()
            x_column = st.selectbox("X-axis", x_options)
            y_column = st.selectbox("Numeric Y-axis", numeric_columns)

            fig = px.line(
                df,
                x=x_column,
                y=y_column,
                title=f"{y_column} by {x_column}",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns available.")

    elif chart_type == "Correlation heatmap":
        if len(numeric_columns) >= 2:
            corr = numeric_df[numeric_columns].corr(numeric_only=True)

            fig = go.Figure(
                data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.index,
                    zmin=-1,
                    zmax=1,
                    colorscale="RdBu",
                    colorbar_title="Correlation",
                    text=corr.round(2).values,
                    texttemplate="%{text}",
                )
            )
            fig.update_layout(title="Numeric feature correlations")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("At least two numeric columns are needed for a heatmap.")


# --------------------------------------------------
# TAB 4: DATA QUALITY
# --------------------------------------------------

with quality_tab:
    st.subheader("Data Quality Assessment")

    quality_table = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data type": df.dtypes.astype(str).values,
        "Missing values": df.isna().sum().values,
        "Missing %": (
            df.isna().mean().values * 100
        ).round(2),
        "Unique values": df.nunique(dropna=True).values,
    })

    st.dataframe(quality_table, use_container_width=True)

    st.markdown("#### Duplicate records")
    st.write(f"Detected duplicate rows: **{duplicate_total}**")

    if duplicate_total:
        if st.checkbox("Preview duplicate rows"):
            st.dataframe(
                df[df.duplicated(keep=False)],
                use_container_width=True,
            )

    st.markdown("#### Missing data chart")
    missing_frame = quality_table[
        quality_table["Missing values"] > 0
    ].sort_values("Missing %", ascending=False)

    if not missing_frame.empty:
        fig = px.bar(
            missing_frame,
            x="Column",
            y="Missing %",
            title="Missing data percentage by column",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("All columns are complete.")

    st.warning(
        "This page reports potential quality issues. "
        "It does not automatically modify or delete your data."
    )


# --------------------------------------------------
# TAB 5: INSIGHTS
# --------------------------------------------------

with insights_tab:
    st.subheader("Automated Analysis Results")

    st.markdown("#### Correlations")
    correlations = analysis.get("numeric_correlations", {})
    if correlations:
        st.json(correlations)
    else:
        st.info("The backend did not return correlation results.")

    st.markdown("#### Outlier counts")
    outliers = analysis.get("outlier_counts", {})
    if outliers:
        outlier_frame = pd.DataFrame(
            list(outliers.items()),
            columns=["Column", "Outlier count"],
        )
        st.dataframe(outlier_frame, use_container_width=True)

        if numeric_columns:
            fig = px.bar(
                outlier_frame,
                x="Column",
                y="Outlier count",
                title="Potential outliers by column",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No outlier counts were returned by the backend.")

    st.markdown("#### Category insights")
    categories = analysis.get("category_insights", {})
    if categories:
        st.json(categories)
    else:
        st.info("No category insights were returned by the backend.")

    st.caption(
        "Correlations and outliers indicate possible patterns, "
        "not proof of causation or errors."
    )


# --------------------------------------------------
# TAB 6: DOWNLOAD REPORTS
# --------------------------------------------------

with report_tab:
    st.subheader("Export Your Analysis")
    st.write(
        "Download the backend's complete analysis report or a CSV copy "
        "of the uploaded dataset."
    )

    show_downloads(result, df)

    with st.expander("View complete JSON result"):
        st.json(result)

st.divider()
st.caption("AI Data Intelligence Agent • Interactive analytics workspace")
