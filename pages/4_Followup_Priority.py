import streamlit as st
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters, to_excel_bytes

st.title("☎️ Follow-up Priority")

df = load_enrolment_data()
df = apply_common_filters(df)

followup = df[
    df["Follow-up Priority"].isin([
        "High Risk - Overdue",
        "Medium Risk - Due Soon",
        "Admin Risk - Missing USI",
        "Admin Risk - No Trainer"
    ])
].copy()

followup = followup.sort_values(by="DATEENROLLED", ascending=False)

st.metric("Students Requiring Follow-up", len(followup))

if followup.empty:
    st.success("No follow-up students found.")
    st.stop()

priority_count = followup["Follow-up Priority"].value_counts().reset_index()
priority_count.columns = ["Priority", "Count"]

fig = px.bar(
    priority_count,
    x="Priority",
    y="Count",
    text="Count",
    title="Follow-up Workload"
)

st.plotly_chart(fig, use_container_width=True)

display_cols = [
    "FULLNAME",
    "DIPLOMACODE",
    "DIPLOMA",
    "CLASSDESCRIPTOR",
    "TRAINERFULLNAME",
    "DATEENROLLED",
    "DATECOMPLETIONEXPECTED",
    "DATECOMPLETED",
    "Days Until Expected Completion",
    "Follow-up Priority",
    "USI",
    "ORGANISATIONNAME"
]

display_cols = [c for c in display_cols if c in followup.columns]

st.dataframe(followup[display_cols], use_container_width=True, hide_index=True)

st.download_button(
    "Download Follow-up List",
    data=to_excel_bytes(followup[display_cols]),
    file_name="followup_priority_list.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)