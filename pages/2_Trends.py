# import streamlit as st
# import plotly.express as px
# from utils.dashboard_helpers import load_enrolment_data, apply_common_filters

# st.title("📈 Enrolment and Completion Trends")

# df = load_enrolment_data()
# df = apply_common_filters(df)

# if "Enrolment Month" in df.columns:
#     monthly = (
#         df.groupby("Enrolment Month")
#         .size()
#         .reset_index(name="Enrolments")
#         .sort_values("Enrolment Month")
#     )

#     fig = px.line(
#         monthly,
#         x="Enrolment Month",
#         y="Enrolments",
#         markers=True,
#         title="Monthly Enrolments"
#     )

#     st.plotly_chart(fig, use_container_width=True)

# if "Completed Month" in df.columns:
#     completed = (
#         df[df["DATECOMPLETED"].notna()]
#         .groupby("Completed Month")
#         .size()
#         .reset_index(name="Completions")
#         .sort_values("Completed Month")
#     )

#     fig = px.line(
#         completed,
#         x="Completed Month",
#         y="Completions",
#         markers=True,
#         title="Monthly Completions"
#     )

#     st.plotly_chart(fig, use_container_width=True)



import streamlit as st
import plotly.express as px

from utils.dashboard_helpers import load_enrolment_data, apply_common_filters


st.title("📈 Enrolment and Completion Trends")

df = load_enrolment_data()
df = apply_common_filters(df)

if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# Weekly enrolment trend
if "DATEENROLLED" in df.columns:
    enrolment_df = df[df["DATEENROLLED"].notna()].copy()

    if enrolment_df.empty:
        st.info("No enrolment records available for the selected filters.")
    else:
        enrolment_df["Enrolment Week"] = (
            enrolment_df["DATEENROLLED"]
            .dt.to_period("W")
            .apply(lambda r: r.start_time)
        )

        weekly_enrolments = (
            enrolment_df
            .groupby("Enrolment Week")
            .size()
            .reset_index(name="Enrolments")
            .sort_values("Enrolment Week")
        )

        fig = px.line(
            weekly_enrolments,
            x="Enrolment Week",
            y="Enrolments",
            markers=True,
            title="Weekly Enrolments"
        )

        st.plotly_chart(fig, use_container_width=True)


# Weekly completion trend
if "DATECOMPLETED" in df.columns:
    completed_df = df[df["DATECOMPLETED"].notna()].copy()

    if completed_df.empty:
        st.info("No completion records available for the selected filters.")
    else:
        completed_df["Completed Week"] = (
            completed_df["DATECOMPLETED"]
            .dt.to_period("W")
            .apply(lambda r: r.start_time)
        )

        weekly_completions = (
            completed_df
            .groupby("Completed Week")
            .size()
            .reset_index(name="Completions")
            .sort_values("Completed Week")
        )

        fig = px.line(
            weekly_completions,
            x="Completed Week",
            y="Completions",
            markers=True,
            title="Weekly Completions"
        )

        st.plotly_chart(fig, use_container_width=True)