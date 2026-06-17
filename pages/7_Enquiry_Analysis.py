from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.dashboard_helpers import load_enquiry_data


st.set_page_config(
    page_title="Enquiry Analysis",
    layout="wide"
)

st.title("📞 Enquiry Analysis Dashboard")

if st.button("Refresh enquiry data now"):
    st.cache_data.clear()

df = load_enquiry_data()

if df.empty:
    st.warning("No enquiry data loaded.")
    st.stop()


DATE_COL = "ENQUIREDDATE"
COURSE_COL = "ENQUIREDCOURSES"
STATUS_COL = "Enquiry Status"
SOURCE_COL = "ENQUIRYSOURCEOFENQUIRY"
MODE_COL = "ENQUIREDMODE"
LOST_REASON_COL = "ENQUIREDSTATUSLOSTREASON"

sensitive_columns = [
    "DOB"
]


# -----------------------------
# Sidebar filters
# -----------------------------
with st.sidebar:
    st.header("Enquiry Filters")

    if DATE_COL in df.columns and df[DATE_COL].notna().any():
        min_date = df[DATE_COL].min().date()
        max_date = df[DATE_COL].max().date()

        selected_date_range = st.date_input(
            "Select enquiry date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        selected_date_range = None

    courses = st.multiselect(
        "Course",
        sorted(df[COURSE_COL].dropna().unique())
    ) if COURSE_COL in df.columns else []

    statuses = st.multiselect(
        "Enquiry Status",
        sorted(df[STATUS_COL].dropna().unique())
    ) if STATUS_COL in df.columns else []

    sources = st.multiselect(
        "Source of Enquiry",
        sorted(df[SOURCE_COL].dropna().unique())
    ) if SOURCE_COL in df.columns else []

    modes = st.multiselect(
        "Enquiry Mode",
        sorted(df[MODE_COL].dropna().unique())
    ) if MODE_COL in df.columns else []


filtered_df = df.copy()

if selected_date_range and len(selected_date_range) == 2 and DATE_COL in filtered_df.columns:
    start_date, end_date = selected_date_range

    filtered_df = filtered_df[
        (filtered_df[DATE_COL].dt.date >= start_date)
        & (filtered_df[DATE_COL].dt.date <= end_date)
    ]

if courses:
    filtered_df = filtered_df[filtered_df[COURSE_COL].isin(courses)]

if statuses:
    filtered_df = filtered_df[filtered_df[STATUS_COL].isin(statuses)]

if sources:
    filtered_df = filtered_df[filtered_df[SOURCE_COL].isin(sources)]

if modes:
    filtered_df = filtered_df[filtered_df[MODE_COL].isin(modes)]


if filtered_df.empty:
    st.warning("No enquiry records available for the selected filters.")
    st.stop()


# -----------------------------
# KPI cards
# -----------------------------
total_enquiries = len(filtered_df)
won = int((filtered_df[STATUS_COL] == "WON").sum())
lost = int((filtered_df[STATUS_COL] == "LOST").sum())
open_enquiries = total_enquiries - won - lost

conversion_rate = round((won / total_enquiries) * 100, 1) if total_enquiries else 0

total_forecast_value = filtered_df["Forecast Value"].sum()
expected_value = filtered_df["Expected Value"].sum()

st.subheader("Executive Summary")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Enquiries", total_enquiries)
c2.metric("Won", won)
c3.metric("Lost", lost)
c4.metric("Conversion Rate", f"{conversion_rate}%")
c5.metric("Expected Value", f"${expected_value:,.0f}")


# -----------------------------
# Main charts
# -----------------------------
st.subheader("Enquiry Performance Overview")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    status_count = (
        filtered_df[STATUS_COL]
        .value_counts()
        .reset_index()
    )

    status_count.columns = ["Status", "Count"]

    fig = px.pie(
        status_count,
        names="Status",
        values="Count",
        title="Enquiry Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


with chart_col2:
    if COURSE_COL in filtered_df.columns:
        course_df = filtered_df[
            filtered_df[COURSE_COL].notna()
            & (filtered_df[COURSE_COL] != "Not recorded")
            & (filtered_df[COURSE_COL].astype(str).str.strip() != "")
        ]

        course_count = (
            course_df[COURSE_COL]
            .value_counts()
            .head(10)
            .reset_index()
        )

        course_count.columns = ["Course", "Count"]

        fig = px.pie(
            course_count,
            names="Course",
            values="Count",
            title="Top Course Enquiries"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Weekly enquiry trend
# -----------------------------
if DATE_COL in filtered_df.columns:
    trend_df = filtered_df[filtered_df[DATE_COL].notna()].copy()

    if not trend_df.empty:
        trend_df["Enquiry Week"] = (
            trend_df[DATE_COL]
            .dt.to_period("W")
            .apply(lambda r: r.start_time)
        )

        weekly_enquiries = (
            trend_df
            .groupby("Enquiry Week")
            .size()
            .reset_index(name="Enquiries")
            .sort_values("Enquiry Week")
        )

        fig = px.line(
            weekly_enquiries,
            x="Enquiry Week",
            y="Enquiries",
            markers=True,
            title="Weekly Enquiry Trend"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Source and mode analysis
# -----------------------------
st.subheader("Lead Source and Contact Mode Analysis")

source_col1, source_col2 = st.columns(2)

with source_col1:
    if SOURCE_COL in filtered_df.columns:
        source_df = filtered_df[
            filtered_df[SOURCE_COL].notna()
            & (filtered_df[SOURCE_COL] != "Not recorded")
            & (filtered_df[SOURCE_COL] != "Unknown Source")
            & (filtered_df[SOURCE_COL].astype(str).str.strip() != "")
        ]

        source_count = (
            source_df[SOURCE_COL]
            .value_counts()
            .head(15)
            .reset_index()
        )

        source_count.columns = ["Source", "Count"]

        fig = px.bar(
            source_count,
            x="Source",
            y="Count",
            text="Count",
            title="Top Sources of Enquiry"
        )

        st.plotly_chart(fig, use_container_width=True)


with source_col2:
    if MODE_COL in filtered_df.columns:
        mode_df = filtered_df[
            filtered_df[MODE_COL].notna()
            & (filtered_df[MODE_COL] != "Not recorded")
            & (filtered_df[MODE_COL].astype(str).str.strip() != "")
        ]

        mode_count = (
            mode_df[MODE_COL]
            .value_counts()
            .reset_index()
        )

        mode_count.columns = ["Mode", "Count"]

        fig = px.bar(
            mode_count,
            x="Mode",
            y="Count",
            text="Count",
            title="Enquiry Mode"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Conversion by source
# -----------------------------
if SOURCE_COL in filtered_df.columns:
    st.subheader("Conversion by Source")

    conversion_source_df = filtered_df[
        filtered_df[SOURCE_COL].notna()
        & (filtered_df[SOURCE_COL] != "Not recorded")
        & (filtered_df[SOURCE_COL] != "Unknown Source")
        & (filtered_df[SOURCE_COL].astype(str).str.strip() != "")
    ].copy()

    if not conversion_source_df.empty:
        source_summary = (
            conversion_source_df
            .groupby(SOURCE_COL)
            .agg(
                Enquiries=(STATUS_COL, "count"),
                Won=(STATUS_COL, lambda x: (x == "WON").sum()),
                Lost=(STATUS_COL, lambda x: (x == "LOST").sum()),
                Forecast_Value=("Forecast Value", "sum"),
                Expected_Value=("Expected Value", "sum")
            )
            .reset_index()
        )

        source_summary["Conversion Rate"] = (
            source_summary["Won"]
            .div(source_summary["Enquiries"].replace(0, pd.NA))
            .mul(100)
            .fillna(0)
            .round(1)
        )

        source_summary = source_summary.sort_values(
            by="Enquiries",
            ascending=False
        )

        st.dataframe(
            source_summary,
            use_container_width=True
        )

        fig = px.bar(
            source_summary.head(15),
            x=SOURCE_COL,
            y="Conversion Rate",
            text="Conversion Rate",
            title="Conversion Rate by Source (%)"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Conversion by course
# -----------------------------
if COURSE_COL in filtered_df.columns:
    st.subheader("Conversion by Course")

    course_summary_df = filtered_df[
        filtered_df[COURSE_COL].notna()
        & (filtered_df[COURSE_COL] != "Not recorded")
        & (filtered_df[COURSE_COL].astype(str).str.strip() != "")
    ].copy()

    if not course_summary_df.empty:
        course_summary = (
            course_summary_df
            .groupby(COURSE_COL)
            .agg(
                Enquiries=(STATUS_COL, "count"),
                Won=(STATUS_COL, lambda x: (x == "WON").sum()),
                Lost=(STATUS_COL, lambda x: (x == "LOST").sum()),
                Forecast_Value=("Forecast Value", "sum"),
                Expected_Value=("Expected Value", "sum")
            )
            .reset_index()
        )

        course_summary["Conversion Rate"] = (
            course_summary["Won"]
            .div(course_summary["Enquiries"].replace(0, pd.NA))
            .mul(100)
            .fillna(0)
            .round(1)
        )

        course_summary = course_summary.sort_values(
            by="Enquiries",
            ascending=False
        )

        st.dataframe(
            course_summary,
            use_container_width=True
        )

        fig = px.bar(
            course_summary.head(15),
            x=COURSE_COL,
            y="Enquiries",
            text="Enquiries",
            title="Enquiries by Course"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Lost reason analysis
# -----------------------------
if LOST_REASON_COL in filtered_df.columns:
    st.subheader("Lost Enquiry Reasons")

    lost_df = filtered_df[
        (filtered_df[STATUS_COL] == "LOST")
        & (filtered_df[LOST_REASON_COL].notna())
        & (filtered_df[LOST_REASON_COL] != "Not recorded")
        & (filtered_df[LOST_REASON_COL].astype(str).str.strip() != "")
    ]

    if lost_df.empty:
        st.info("No lost reason data available for the selected filters.")
    else:
        lost_reason_count = (
            lost_df[LOST_REASON_COL]
            .value_counts()
            .head(15)
            .reset_index()
        )

        lost_reason_count.columns = ["Lost Reason", "Count"]

        fig = px.bar(
            lost_reason_count,
            x="Lost Reason",
            y="Count",
            text="Count",
            title="Top Lost Enquiry Reasons"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Forecast value analysis
# -----------------------------
st.subheader("Forecast Value Analysis")

value_col1, value_col2 = st.columns(2)

with value_col1:
    if COURSE_COL in filtered_df.columns:
        value_by_course = (
            filtered_df[
                filtered_df[COURSE_COL].notna()
                & (filtered_df[COURSE_COL] != "Not recorded")
            ]
            .groupby(COURSE_COL)["Forecast Value"]
            .sum()
            .reset_index()
            .sort_values("Forecast Value", ascending=False)
            .head(10)
        )

        fig = px.bar(
            value_by_course,
            x=COURSE_COL,
            y="Forecast Value",
            text="Forecast Value",
            title="Forecast Value by Course"
        )

        st.plotly_chart(fig, use_container_width=True)


with value_col2:
    if SOURCE_COL in filtered_df.columns:
        value_by_source = (
            filtered_df[
                filtered_df[SOURCE_COL].notna()
                & (filtered_df[SOURCE_COL] != "Not recorded")
                & (filtered_df[SOURCE_COL] != "Unknown Source")
            ]
            .groupby(SOURCE_COL)["Forecast Value"]
            .sum()
            .reset_index()
            .sort_values("Forecast Value", ascending=False)
            .head(10)
        )

        fig = px.bar(
            value_by_source,
            x=SOURCE_COL,
            y="Forecast Value",
            text="Forecast Value",
            title="Forecast Value by Source"
        )

        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Privacy-safe data preview
# -----------------------------
st.subheader("Filtered Enquiry Data Preview")

preview_df = filtered_df.copy()

for col in sensitive_columns:
    if col in preview_df.columns:
        preview_df[col] = "*** HIDDEN ***"

if DATE_COL in preview_df.columns:
    preview_df = preview_df.sort_values(
        by=DATE_COL,
        ascending=False
    )

st.dataframe(
    preview_df,
    use_container_width=True
)


# -----------------------------
# Download filtered data
# -----------------------------
def dataframe_to_excel_bytes(download_df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        download_df.to_excel(
            writer,
            index=False,
            sheet_name="Enquiry_Analysis"
        )

    return output.getvalue()


excel_bytes = dataframe_to_excel_bytes(filtered_df)

st.download_button(
    label="Download Filtered Enquiry Data",
    data=excel_bytes,
    file_name="filtered_enquiry_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)