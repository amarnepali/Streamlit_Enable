import streamlit as st
import pandas as pd
# import requests
import plotly.express as px

from utils.axcelerate_api import load_axcelerate_report

st.set_page_config(page_title="aXcelerate Dashboard", layout="wide")


# API_URL = "https://enablecollege.stg.axcelerate.com/api/report/saved/run"

# @st.cache_data(ttl=3600)
# def load_axcelerate_report():
#     headers = {
#         "apitoken": st.secrets["AXCELERATE_API_TOKEN"],
#         "wstoken": st.secrets["AXCELERATE_WS_TOKEN"],
#         "Accept": "application/json",
#         "Content-Type": "application/x-www-form-urlencoded",
#     }

#     payload = {
#         "reportID": st.secrets["REPORT_ID"]
#     }

#     response = requests.post(API_URL, headers=headers, data=payload, timeout=60)

#     if response.status_code != 200:
#         st.error(f"API failed. Status code: {response.status_code}")
#         st.text(response.text)
#         return pd.DataFrame()

#     result = response.json()

#     # Try common aXcelerate response keys
#     if "DATA" in result:
#         data = result["DATA"]
#     elif "data" in result:
#         data = result["data"]
#     elif "rows" in result:
#         data = result["rows"]
#     else:
#         st.warning("Could not find DATA/data/rows in API response.")
#         st.json(result)
#         return pd.DataFrame()

#     return pd.DataFrame(data)


st.title("aXcelerate Enrolment Dashboard")

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
    ascending = True
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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Records", len(df))

with col2:
    st.metric("Total Columns", len(df.columns))

with col3:
    st.metric("Last Refresh", pd.Timestamp.now().strftime("%d %b %Y %I:%M %p"))

# Automatically detect useful columns
status_cols = [c for c in df.columns if "status" in c.lower()]
trainer_cols = [c for c in df.columns if "trainer" in c.lower()]
org_cols = [c for c in df.columns if "organisation" in c.lower() or "organization" in c.lower()]
course_cols = [c for c in df.columns if "course" in c.lower() or "program" in c.lower()]

if status_cols:
    st.subheader("Completion / Status Summary")
    status_col = status_cols[0]
    status_count = df[status_col].value_counts().reset_index()
    status_count.columns = [status_col, "Count"]
    fig = px.bar(status_count, x=status_col, y="Count", title=f"Records by {status_col}")
    st.plotly_chart(fig, use_container_width=True)

if trainer_cols:
    st.subheader("Trainer Summary")
    trainer_col = trainer_cols[0]
    trainer_count = df[trainer_col].value_counts().head(20).reset_index()
    trainer_count.columns = [trainer_col, "Count"]
    fig = px.bar(trainer_count, x=trainer_col, y="Count", title=f"Top Trainers by Records")
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




# @st.cache_data(ttl=3600)
# def load_contact_details_report():
#     headers = {
#         "apitoken": st.secrets["AXCELERATE_API_TOKEN"],
#         "wstoken": st.secrets["AXCELERATE_WS_TOKEN"],
#         "Accept": "application/json",
#         "Content-Type": "application/x-www-form-urlencoded",
#     }

#     payload = {
#         "reportID": "93013"
#     }

#     response = requests.post(API_URL, headers=headers, data=payload, timeout=60)

#     if response.status_code != 200:
#         st.error(f"Contact API failed. Status code: {response.status_code}")
#         st.text(response.text)
#         return pd.DataFrame()

#     result = response.json()

#     if "DATA" in result:
#         data = result["DATA"]
#     elif "data" in result:
#         data = result["data"]
#     elif "rows" in result:
#         data = result["rows"]
#     else:
#         st.warning("Could not find contact data in response.")
#         st.json(result)
#         return pd.DataFrame()

#     return pd.DataFrame(data)


# st.header("Follow-up File Mobile Phone Integration")

# uploaded_file = st.file_uploader(
#     "Upload follow-up file CSV or Excel",
#     type=["csv", "xlsx"]
# )

# if uploaded_file is not None:
#     if uploaded_file.name.endswith(".csv"):
#         followup_df = pd.read_csv(uploaded_file)
#     else:
#         followup_df = pd.read_excel(uploaded_file)

#     st.subheader("Uploaded Follow-up File")
#     st.dataframe(followup_df, use_container_width=True)

#     contact_df = load_contact_details_report()

#     st.subheader("aXcelerate Contact Details Report")
#     st.dataframe(contact_df, use_container_width=True)

# if uploaded_file is not None and not contact_df.empty:

#     st.subheader("Select Matching Columns")

#     followup_match_col = st.selectbox(
#         "Column in follow-up file",
#         followup_df.columns
#     )

#     contact_match_col = st.selectbox(
#         "Matching column in aXcelerate contact report",
#         contact_df.columns
#     )

#     mobile_col = st.selectbox(
#         "Mobile phone column in aXcelerate contact report",
#         contact_df.columns
#     )

#     if st.button("Add Mobile Phone to Follow-up File"):
#         temp_followup = followup_df.copy()
#         temp_contact = contact_df.copy()

#         temp_followup[followup_match_col] = temp_followup[followup_match_col].astype(str).str.strip()
#         temp_contact[contact_match_col] = temp_contact[contact_match_col].astype(str).str.strip()

#         mobile_lookup = temp_contact[[contact_match_col, mobile_col]].drop_duplicates(
#             subset=[contact_match_col]
#         )

#         final_df = temp_followup.merge(
#             mobile_lookup,
#             how="left",
#             left_on=followup_match_col,
#             right_on=contact_match_col
#         )

#         final_df = final_df.drop(columns=[contact_match_col])

#         final_df = final_df.rename(columns={
#             mobile_col: "Mobile Phone"
#         })

#         st.success("Mobile phone column added successfully.")
#         st.dataframe(final_df, use_container_width=True)

# from io import BytesIO

# output = BytesIO()

# with pd.ExcelWriter(output, engine="openpyxl") as writer:
#     final_df.to_excel(writer, index=False, sheet_name="Followup_With_Mobile")

# st.download_button(
#     label="Download Updated Follow-up Excel File",
#     data=output.getvalue(),
#     file_name="followup_with_mobile.xlsx",
#     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
# )


"""
Create DNS record

Type: A
Name: app
Value: YOUR_SERVER_PUBLIC_IP
TTL: default

"""