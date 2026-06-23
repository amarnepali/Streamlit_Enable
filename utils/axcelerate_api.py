import pandas as pd
import requests
import streamlit as st

# API_URL = "https://enablecollege.stg.axcelerate.com/api/report/saved/run"

API_URL = "https://enablecollege.axcelerate.com/api/report/saved/run"


@st.cache_data(ttl=3600)
def load_axcelerate_report(report_id: str) -> pd.DataFrame:
    headers = {
        "apitoken": st.secrets["AXCELERATE_API_TOKEN"],
        "wstoken": st.secrets["AXCELERATE_WS_TOKEN"],
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "reportID": report_id
    }

    response = requests.post(API_URL, headers=headers, data=payload, timeout=60)

    if response.status_code != 200:
        st.error(f"API failed. Status code: {response.status_code}")
        st.text(response.text)
        return pd.DataFrame()

    result = response.json()

    if "DATA" in result:
        data = result["DATA"]
    elif "data" in result:
        data = result["data"]
    elif "rows" in result:
        data = result["rows"]
    else:
        st.warning("Could not find DATA/data/rows in API response.")
        st.json(result)
        return pd.DataFrame()

    return pd.DataFrame(data)