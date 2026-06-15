import streamlit as st
import pandas as pd
from io import BytesIO
from utils.axcelerate_api import load_axcelerate_report

DATE_COLS = [
    "DATEENROLLED",
    "DATECOMMENCED",
    "DATECOMPLETIONEXPECTED",
    "DATECOMPLETED"
]

def clean_text(series):
    return (
        series.astype("string")
        .fillna("Not recorded")
        .str.strip()
        .replace({
            "": "Not recorded",
            "nan": "Not recorded",
            "None": "Not recorded"
        })
    )

@st.cache_data(ttl=3600)
def load_enrolment_data():
    report_id = st.secrets["REPORT_ID_ENROLLMENT"]
    df = load_axcelerate_report(report_id)
    return prepare_data(df)

def prepare_data(df):
    df = df.copy()

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    text_cols = [
        "DIPLOMACODE",
        "DIPLOMA",
        "CLASSDESCRIPTOR",
        "FULLNAME",
        "USI",
        "ORGANISATIONNAME",
        "TRAINERFULLNAME"
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = clean_text(df[col])

    today = pd.Timestamp.today().normalize()

    if "DATECOMPLETED" in df.columns:
        df["Completion Status"] = df["DATECOMPLETED"].notna().map({
            True: "Completed",
            False: "Active / Not Completed"
        })
    else:
        df["Completion Status"] = "Unknown"

    if "DATECOMPLETIONEXPECTED" in df.columns:
        df["Days Until Expected Completion"] = (
            df["DATECOMPLETIONEXPECTED"] - today
        ).dt.days

        df["Overdue"] = (
            df["DATECOMPLETIONEXPECTED"].notna()
            & df["DATECOMPLETED"].isna()
            & (df["DATECOMPLETIONEXPECTED"] < today)
        )

        df["Due in 30 Days"] = (
            df["DATECOMPLETIONEXPECTED"].notna()
            & df["DATECOMPLETED"].isna()
            & (df["DATECOMPLETIONEXPECTED"] >= today)
            & (df["DATECOMPLETIONEXPECTED"] <= today + pd.Timedelta(days=30))
        )
    else:
        df["Overdue"] = False
        df["Due in 30 Days"] = False

    df["Missing USI"] = df["USI"].eq("Not recorded") if "USI" in df.columns else False
    df["No Trainer Assigned"] = df["TRAINERFULLNAME"].eq("Not recorded") if "TRAINERFULLNAME" in df.columns else False

    def risk_label(row):
        if row["Overdue"]:
            return "High Risk - Overdue"
        if row["Due in 30 Days"]:
            return "Medium Risk - Due Soon"
        if row["Missing USI"]:
            return "Admin Risk - Missing USI"
        # if row["No Trainer Assigned"]:
        #     return "Admin Risk - No Trainer"
        if row["Completion Status"] == "Completed":
            return "Completed"
        return "On Track"

    df["Follow-up Priority"] = df.apply(risk_label, axis=1)

    if "DATEENROLLED" in df.columns:
        df["Enrolment Month"] = df["DATEENROLLED"].dt.to_period("M").astype(str)

    if "DATECOMPLETED" in df.columns:
        df["Completed Month"] = df["DATECOMPLETED"].dt.to_period("M").astype(str)

    return df

def apply_common_filters(df):
    with st.sidebar:
        st.header("Filters")

        courses = st.multiselect(
            "Course",
            sorted(df["DIPLOMA"].dropna().unique())
        ) if "DIPLOMA" in df.columns else []

        trainers = st.multiselect(
            "Trainer",
            sorted(df["TRAINERFULLNAME"].dropna().unique())
        ) if "TRAINERFULLNAME" in df.columns else []

        status = st.multiselect(
            "Completion Status",
            sorted(df["Completion Status"].dropna().unique())
        )

        priority = st.multiselect(
            "Follow-up Priority",
            sorted(df["Follow-up Priority"].dropna().unique())
        )
        st.subheader("Date Filter")

        available_date_cols = [
            col for col in DATE_COLS
            if col in df.columns and df[col].notna().any()
        ]

        selected_date_col = st.selectbox(
            "Select date field",
            available_date_cols,
            index=0
        )

        min_date = df[selected_date_col].min().date()
        max_date = df[selected_date_col].max().date()

        selected_date_range = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # analysis_period = st.selectbox(
        #     "Analysis period",
        #     ["Daily", "Weekly", "Monthly"]
        # )

    filtered = df.copy()

    if courses:
        filtered = filtered[filtered["DIPLOMA"].isin(courses)]

    if trainers:
        filtered = filtered[filtered["TRAINERFULLNAME"].isin(trainers)]

    if status:
        filtered = filtered[filtered["Completion Status"].isin(status)]

    if priority:
        filtered = filtered[filtered["Follow-up Priority"].isin(priority)]
    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        filtered = filtered[
            (filtered[selected_date_col].dt.date >= start_date) &
            (filtered[selected_date_col].dt.date <= end_date)
        ]

    # if analysis_period == "Daily":
    #     filtered["Analysis Period"] = filtered[selected_date_col].dt.date.astype(str)

    # elif analysis_period == "Weekly":
    #     filtered["Analysis Period"] = (
    #         filtered[selected_date_col]
    #         .dt.to_period("W")
    #         .astype(str)
    #     )

    # elif analysis_period == "Monthly":
    #     filtered["Analysis Period"] = (
    #         filtered[selected_date_col]
    #         .dt.to_period("M")
    #         .astype(str)
    #     )

    filtered = filtered.sort_values(
        by=selected_date_col,
        ascending=False
    )

    return filtered

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Export")
    return output.getvalue()