import streamlit as st
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters
import pandas as pd
st.title("🎓 Courses and Classes")

df = load_enrolment_data()
df = apply_common_filters(df)

course_count = df["DIPLOMA"].value_counts().reset_index()
course_count.columns = ["Course", "Count"]

fig = px.bar(
    course_count,
    x="Count",
    y="Course",
    orientation="h",
    text="Count",
    title="Enrolments by Course"
)

st.plotly_chart(fig, use_container_width=True)

class_count = df["CLASSDESCRIPTOR"].value_counts().head(30).reset_index()
class_count.columns = ["Class", "Count"]

fig = px.bar(
    class_count,
    x="Count",
    y="Class",
    orientation="h",
    text="Count",
    title="Top Classes"
)

st.plotly_chart(fig, use_container_width=True)

summary = (
    df.groupby("DIPLOMA")
    .agg(
        Total=("DIPLOMA", "size"),
        Completed=("Completion Status", lambda x: (x == "Completed").sum()),
        Overdue=("Overdue", "sum"),
        DueSoon=("Due in 30 Days", "sum")
    )
    .reset_index()
)
if summary.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

summary["Completed"] = pd.to_numeric(summary["Completed"], errors="coerce").fillna(0)
summary["Total"] = pd.to_numeric(summary["Total"], errors="coerce").fillna(0)

summary["Completion Rate"] = (
    summary["Completed"]
    .div(summary["Total"].replace(0, pd.NA))
    .mul(100)
    .fillna(0)
    .round(1)
)

st.dataframe(summary, use_container_width=True, hide_index=True)