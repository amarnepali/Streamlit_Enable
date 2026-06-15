import streamlit as st
import pandas as pd
# import requests
import plotly.express as px

from utils.axcelerate_api import load_axcelerate_report

st.set_page_config(page_title="aXcelerate Dashboard", layout="wide")



st.title("📊 Overview")

if st.button("Refresh data now"):
    st.cache_data.clear()

report_id_E = st.secrets["REPORT_ID_ENROLLMENT"]
df = load_axcelerate_report(report_id_E)
# df = load_axcelerate_report()

if df.empty:
    st.stop()

st.success(f"Loaded {len(df)} records")

# st.subheader("Raw Data Preview")
# st.dataframe(df, use_container_width=True)
st.subheader("Raw Data Preview")

# Enterprise-level privacy masking
# Keeps the columns visible but hides sensitive values
preview_df = df.copy()
preview_df = preview_df.sort_values(
    by = "DATEENROLLED",
    ascending = False
)

sensitive_columns = [
    "FULLNAME",
    "USI",
    "EMAIL",
    "EMAILADDRESS",
    "MOBILE",
    "PHONE",
    "DATEOFBIRTH",
    "DOB",
    "ADDRESS",
    "POSTCODE"
]

for col in sensitive_columns:
    if col in preview_df.columns:
        preview_df[col] = "*** HIDDEN ***"

st.dataframe(
    preview_df,
    use_container_width=True
)

st.subheader("Dashboard Summary")

col1, col3 = st.columns(2)

with col1:
    st.metric("Total Records", len(df))

with col3:
    st.metric("Last Refresh", pd.Timestamp.now().strftime("%d %b %Y %I:%M %p"))

# Automatically detect useful columns
status_cols = [c for c in df.columns if "status" in c.lower()]
trainer_cols = [c for c in df.columns if "trainer" in c.lower()]
org_cols = [c for c in df.columns if "organisation" in c.lower() or "organization" in c.lower()]
course_cols = [c for c in df.columns if "course" in c.lower() or "program" in c.lower()]

import streamlit as st
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters



df = load_enrolment_data()
df = apply_common_filters(df)

total = len(df)
completed = int((df["Completion Status"] == "Completed").sum())
active = int((df["Completion Status"] == "Active / Not Completed").sum())
overdue = int(df["Overdue"].sum())
due_soon = int(df["Due in 30 Days"].sum())
completion_rate = round((completed / total) * 100, 1) if total else 0

c2, c3, c4, c5 = st.columns(4)
c2.metric("Completed", completed, f"{completion_rate}%")
c3.metric("Active", active)
c4.metric("Overdue", overdue)
c5.metric("Due Soon", due_soon)

status_count = df["Completion Status"].value_counts().reset_index()
status_count.columns = ["Status", "Count"]

fig1 = px.pie(
    status_count,
    names="Status",
    values="Count",
    title="Completion Status"
)
# Course pie chart
if "DIPLOMA" in df.columns:
    course_count = (
        df["DIPLOMA"]
        .value_counts()
        .reset_index()
    )

    course_count.columns = ["Course", "Count"]

    fig = px.pie(
        course_count,
        names="Course",
        values="Count",
        title="Course Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Course column DIPLOMA not found.")

st.plotly_chart(fig1, use_container_width=True)

priority_count = df["Follow-up Priority"].value_counts().reset_index()
priority_count.columns = ["Priority", "Count"]

fig = px.bar(
    priority_count,
    x="Priority",
    y="Count",
    text="Count",
    title="Follow-up Priority"
)

st.plotly_chart(fig, use_container_width=True)

if org_cols:
    st.subheader("Organisation Summary")
    org_col = org_cols[0]
    org_count = df[org_col].value_counts().head(20).reset_index()
    org_count.columns = [org_col, "Count"]
    fig = px.bar(org_count, x=org_col, y="Count", title=f"Top Organisations")
    st.plotly_chart(fig, use_container_width=True)

if course_cols:
    st.subheader("Course Summary")
    course_col = course_cols[0]
    course_count = df[course_col].value_counts().head(20).reset_index()
    course_count.columns = [course_col, "Count"]
    fig = px.bar(course_count, x=course_col, y="Count", title=f"Top Courses")
    st.plotly_chart(fig, use_container_width=True)

