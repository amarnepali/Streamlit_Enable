import streamlit as st
import pandas as pd
import plotly.express as px
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters

st.title("🧹 Data Quality")

df = load_enrolment_data()
df = apply_common_filters(df)

dq = pd.DataFrame({
    "Issue": [
        "Missing USI",
        "No Trainer Assigned",
        "Missing Organisation",
        "Missing Expected Completion Date",
        "Missing Completed Date"
    ],
    "Count": [
        int(df["Missing USI"].sum()),
        int(df["No Trainer Assigned"].sum()),
        int(df["ORGANISATIONNAME"].eq("Not recorded").sum()) if "ORGANISATIONNAME" in df.columns else 0,
        int(df["DATECOMPLETIONEXPECTED"].isna().sum()) if "DATECOMPLETIONEXPECTED" in df.columns else 0,
        int(df["DATECOMPLETED"].isna().sum()) if "DATECOMPLETED" in df.columns else 0
    ]
})

dq["Percent"] = (dq["Count"] / len(df) * 100).round(1)

st.dataframe(dq, use_container_width=True, hide_index=True)

fig = px.bar(
    dq,
    x="Issue",
    y="Count",
    text="Count",
    title="Data Quality Issues"
)

st.plotly_chart(fig, use_container_width=True)

if "USI" in df.columns:
    duplicate_usi = df[
        df["USI"].ne("Not recorded")
        & df.duplicated("USI", keep=False)
    ]

    st.subheader("Duplicate USI Records")
    st.write(f"Duplicate records found: **{len(duplicate_usi)}**")

    if not duplicate_usi.empty:
        st.dataframe(duplicate_usi, use_container_width=True, hide_index=True)