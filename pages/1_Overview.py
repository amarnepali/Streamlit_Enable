import streamlit as st
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters

st.title("📊 Overview")

df = load_enrolment_data()
df = apply_common_filters(df)

total = len(df)
completed = int((df["Completion Status"] == "Completed").sum())
active = int((df["Completion Status"] == "Active / Not Completed").sum())
overdue = int(df["Overdue"].sum())
due_soon = int(df["Due in 30 Days"].sum())
completion_rate = round((completed / total) * 100, 1) if total else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Enrolments", total)
c2.metric("Completed", completed, f"{completion_rate}%")
c3.metric("Active", active)
c4.metric("Overdue", overdue)
c5.metric("Due Soon", due_soon)

status_count = df["Completion Status"].value_counts().reset_index()
status_count.columns = ["Status", "Count"]

fig = px.pie(
    status_count,
    names="Status",
    values="Count",
    title="Completion Status"
)

st.plotly_chart(fig, use_container_width=True)

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