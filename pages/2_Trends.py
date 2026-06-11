import streamlit as st
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters

st.title("📈 Enrolment and Completion Trends")

df = load_enrolment_data()
df = apply_common_filters(df)

if "Enrolment Month" in df.columns:
    monthly = (
        df.groupby("Enrolment Month")
        .size()
        .reset_index(name="Enrolments")
        .sort_values("Enrolment Month")
    )

    fig = px.line(
        monthly,
        x="Enrolment Month",
        y="Enrolments",
        markers=True,
        title="Monthly Enrolments"
    )

    st.plotly_chart(fig, use_container_width=True)

if "Completed Month" in df.columns:
    completed = (
        df[df["DATECOMPLETED"].notna()]
        .groupby("Completed Month")
        .size()
        .reset_index(name="Completions")
        .sort_values("Completed Month")
    )

    fig = px.line(
        completed,
        x="Completed Month",
        y="Completions",
        markers=True,
        title="Monthly Completions"
    )

    st.plotly_chart(fig, use_container_width=True)