import streamlit as st
import pandas as pd
from utils.dashboard_helpers import load_enrolment_data, apply_common_filters, to_excel_bytes

st.title("🔎 Student Explorer")

df = load_enrolment_data()
df = apply_common_filters(df)

search = st.text_input(
    "Search by student name, USI, course, class, trainer, or organisation"
)

filtered = df.copy()

if search:
    search_cols = [
        "FULLNAME",
        "USI",
        "DIPLOMA",
        "DIPLOMACODE",
        "CLASSDESCRIPTOR",
        "TRAINERFULLNAME",
        "ORGANISATIONNAME"
    ]

    search_cols = [c for c in search_cols if c in filtered.columns]

    mask = pd.Series(False, index=filtered.index)

    for col in search_cols:
        mask = mask | filtered[col].astype(str).str.contains(
            search,
            case=False,
            na=False
        )

    filtered = filtered[mask]

st.write(f"Showing **{len(filtered)}** records")

st.dataframe(filtered, use_container_width=True, hide_index=True)

st.download_button(
    "Download Filtered Data",
    data=to_excel_bytes(filtered),
    file_name="student_explorer_export.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)