# from io import BytesIO

# import pandas as pd
# import streamlit as st

# from utils.axcelerate_api import load_axcelerate_report


# st.set_page_config(
#     page_title="Follow-up Mobile Merge",
#     layout="wide"
# )

# st.title("Follow-up File Mobile Phone Merge")

# st.write(
#     "Upload a follow-up CSV or Excel file, pull contact details from "
#     "aXcelerate report 93013, then add the mobile phone column."
# )


# def read_uploaded_file(uploaded_file) -> pd.DataFrame:
#     if uploaded_file.name.lower().endswith(".csv"):
#         return pd.read_csv(uploaded_file)

#     return pd.read_excel(uploaded_file)


# def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
#     output = BytesIO()

#     with pd.ExcelWriter(output, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Followup_With_Mobile")

#     return output.getvalue()


# uploaded_file = st.file_uploader(
#     "Upload follow-up file",
#     type=["csv", "xlsx"]
# )

# if uploaded_file is None:
#     st.info("Please upload a follow-up CSV or Excel file.")
#     st.stop()

# followup_df = read_uploaded_file(uploaded_file)

# st.subheader("Uploaded Follow-up File Preview")
# st.dataframe(followup_df.head(20), use_container_width=True)

# with st.spinner("Loading contact details from aXcelerate report 93013..."):
#     contact_df = load_axcelerate_report("93013")

# if contact_df.empty:
#     st.error("No contact details were loaded from aXcelerate.")
#     st.stop()

# st.subheader("aXcelerate Contact Details Preview")
# st.dataframe(contact_df.head(20), use_container_width=True)

# st.subheader("Select Matching Fields")

# col0, col1, col2, col3 = st.columns(4)
# with col0:
#     followup_match_col = st.selectbox(
#         "Follow-up file Whose Task",
#         followup_df.columns)

# with col1:
#     followup_match_col = st.selectbox(
#         "Follow-up file matching column",
#         followup_df.columns
#     )

# with col2:
#     contact_match_col = st.selectbox(
#         "aXcelerate contact matching column",
#         contact_df.columns
#     )

# with col3:
#     mobile_col = st.selectbox(
#         "Mobile phone column from aXcelerate",
#         contact_df.columns
#     )

# if st.button("Generate Follow-up File with Mobile Phone"):
#     temp_followup = followup_df.copy()
#     temp_contact = contact_df.copy()

#     temp_followup[followup_match_col] = (
#         temp_followup[followup_match_col]
#         .astype(str)
#         .str.strip()
#         .str.lower()
#     )

#     temp_contact[contact_match_col] = (
#         temp_contact[contact_match_col]
#         .astype(str)
#         .str.strip()
#         .str.lower()
#     )

#     mobile_lookup = temp_contact[[contact_match_col, mobile_col]].drop_duplicates(
#         subset=[contact_match_col]
#     )

#     final_df = temp_followup.merge(
#         mobile_lookup,
#         how="left",
#         left_on=followup_match_col,
#         right_on=contact_match_col
#     )

#     if contact_match_col != followup_match_col:
#         final_df = final_df.drop(columns=[contact_match_col])

#     final_df = final_df.rename(columns={mobile_col: "Mobile Phone"})

#     matched_count = final_df["Mobile Phone"].notna().sum()
#     total_count = len(final_df)

#     st.success(f"Mobile phone added. Matched {matched_count} out of {total_count} records.")

#     st.subheader("Final Follow-up File Preview")
#     st.dataframe(final_df, use_container_width=True)

#     excel_bytes = dataframe_to_excel_bytes(final_df)

#     st.download_button(
#         label="Download Follow-up File with Mobile Phone",
#         data=excel_bytes,
#         file_name="followup_with_mobile.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     ) 


from io import BytesIO

import pandas as pd
import streamlit as st

from utils.axcelerate_api import load_axcelerate_report


st.set_page_config(
    page_title="Follow-up Mobile Merge",
    layout="wide"
)

st.title("Follow-up Mobile Phone Integration")

st.write(
    """
    Upload follow-up CSV/XLSX file,
    automatically match contact details from aXcelerate report 93228 Report_id_contact,
    add mobile phone numbers,
    filter by task owner,
    and download final follow-up file.
    """
)


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Followup")

    return output.getvalue()


uploaded_file = st.file_uploader(
    "Upload Follow-up File",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("Please upload a follow-up file.")
    st.stop()

followup_df = read_uploaded_file(uploaded_file)

st.subheader("Uploaded Follow-up File")
st.dataframe(followup_df.head(20), use_container_width=True)

required_columns = ["Email", "Whose Task"]

missing_columns = [c for c in required_columns if c not in followup_df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

with st.spinner("Loading contact details report from aXcelerate..."):
    contact_df = load_axcelerate_report(REPORT_ID_CONTACT)

if contact_df.empty:
    st.error("No contact details loaded from aXcelerate.")
    st.stop()

st.subheader("aXcelerate Contact Details Preview")
st.dataframe(contact_df.head(20), use_container_width=True)

contact_email_col = "EMAILADDRESS"
contact_mobile_col = "MOBILEPHONE"

if contact_email_col not in contact_df.columns:
    st.error(f"{contact_email_col} column not found in contact report.")
    st.stop()

if contact_mobile_col not in contact_df.columns:
    st.error(f"{contact_mobile_col} column not found in contact report.")
    st.stop()

st.success(f"Using Email Column: {contact_email_col}")
st.success(f"Using Mobile Column: {contact_mobile_col}")

# Standardize emails
followup_df["Email"] = (
    followup_df["Email"]
    .astype(str)
    .str.strip()
    .str.lower()
)

contact_df[contact_email_col] = (
    contact_df[contact_email_col]
    .astype(str)
    .str.strip()
    .str.lower()
)

mobile_lookup = contact_df[
    [contact_email_col, contact_mobile_col]
].drop_duplicates(
    subset=[contact_email_col]
)

# Merge mobile phone
final_df = followup_df.merge(
    mobile_lookup,
    how="left",
    left_on="Email",
    right_on=contact_email_col
)

if contact_email_col != "Email":
    final_df = final_df.drop(columns=[contact_email_col])

final_df = final_df.rename(
    columns={
        contact_mobile_col: "Mobile Phone"
    }
)

matched_count = final_df["Mobile Phone"].notna().sum()

st.success(
    f"Successfully matched mobile phones for "
    f"{matched_count} out of {len(final_df)} records."
)

st.subheader("Task Owner Filter")

task_owners = sorted(
    final_df["Whose Task"]
    .dropna()
    .astype(str)
    .unique()
)

selected_owner = st.selectbox(
    "Select whose tasks to download",
    options=["All"] + task_owners
)

if selected_owner != "All":
    filtered_df = final_df[
        final_df["Whose Task"].astype(str) == selected_owner
    ]
else:
    filtered_df = final_df

st.subheader("Filtered Follow-up File")
st.dataframe(filtered_df, use_container_width=True)

excel_bytes = dataframe_to_excel_bytes(filtered_df)

download_name = (
    f"{selected_owner.lower().replace(' ', '_')}_followup.xlsx"
    if selected_owner != "All"
    else "all_followup.xlsx"
)

st.download_button(
    label="Download Filtered Follow-up File",
    data=excel_bytes,
    file_name=download_name,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)