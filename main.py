import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import os


if not os.path.exists("usage_logs.csv"):
    with open("usage_logs.csv", "w") as f:
        f.write("timestamp,api_key,employee_name,department,model,question,tokens_used,cost_usd\n") 

        
# ── PAGE CONFIG ──
st.set_page_config(
    page_title="API Usage Tracker",
    page_icon="📊",
    layout="wide"
)

# ── GREEN THEME ──
st.markdown("""
    <style>
    .main {background-color: #f0fff4;}
    .stMetric {background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 4px solid #38a169;}
    .stDataFrame {background-color: #ffffff;}
    h1, h2, h3 {color: #276749;}
    .stSidebar {background-color: #c6f6d5;}
    </style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──
def load_data():
    if not os.path.exists("usage_logs.csv"):
        return pd.DataFrame()
    df = pd.read_csv("usage_logs.csv")
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def load_api_keys():
    with open("api_keys.json", "r") as f:
        return json.load(f)

# ── FILTER DATA ──
def filter_data(df, period):
    if df.empty:
        return df
    now = datetime.now()
    if period == "Today":
        return df[df["timestamp"].dt.date == now.date()]
    elif period == "This Week":
        week_ago = now - timedelta(days=7)
        return df[df["timestamp"] >= week_ago]
    elif period == "This Month":
        month_ago = now - timedelta(days=30)
        return df[df["timestamp"] >= month_ago]
    return df

# ── SIDEBAR NAVIGATION ──
st.sidebar.title("📊 API Tracker")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "👥 Employee Usage", "🏆 Leaderboard", "🚨 Security Alerts", "📊 Analytics"]
)

st.sidebar.markdown("---")
period = st.sidebar.selectbox(
    "Time Period",
    ["Today", "This Week", "This Month"]
)

# load data
df = load_data()
filtered_df = filter_data(df, period)
api_keys = load_api_keys()



# ── PAGE 1 — HOME ──
if page == "🏠 Home":
    st.title("📊 API Usage Tracker Dashboard")
    st.markdown(f"**Time Period: {period}**")
    st.markdown("---")

    if filtered_df.empty:
        st.info("No data found for this period!")
    else:
        # ── TOP METRICS ──
        total_calls = len(filtered_df)
        total_tokens = filtered_df["tokens_used"].sum()
        total_cost = filtered_df["cost_usd"].astype(float).sum()
        unknown_attempts = len(filtered_df[filtered_df["employee_name"] == "Unknown"])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📞 Total API Calls", total_calls)
        with col2:
            st.metric("🔤 Total Tokens Used", f"{total_tokens:,}")
        with col3:
            st.metric("💰 Total Cost", f"${total_cost:.6f}")
        with col4:
            st.metric("🚨 Unknown Attempts", unknown_attempts)

        st.markdown("---")

        # ── SPENDING LIMIT WARNINGS ──
        st.subheader("⚠️ Spending Limit Warnings")

        warnings_found = False
        for emp_key, emp_data in api_keys.items():
            emp_df = filtered_df[filtered_df["api_key"] == emp_key]
            if emp_df.empty:
                continue
            spent = emp_df["cost_usd"].astype(float).sum()
            limit = emp_data["monthly_limit_usd"]
            percentage = (spent / limit) * 100

            if percentage >= 80:
                warnings_found = True
                st.warning(f"⚠️ **{emp_data['name']}** has used **{percentage:.1f}%** of their monthly limit (${spent:.6f} / ${limit})")

        if not warnings_found:
            st.success("✅ All employees are within their spending limits!")

        st.markdown("---")

        # ── RECENT ACTIVITY ──
        st.subheader("🕐 Recent Activity")
        recent = filtered_df.sort_values("timestamp", ascending=False).head(5)
        st.dataframe(
            recent[["timestamp", "employee_name", "department", "tokens_used", "cost_usd"]],
            use_container_width=True
        )




# ── PAGE 2 — EMPLOYEE USAGE ──
elif page == "👥 Employee Usage":
    st.title("👥 Employee Usage")
    st.markdown(f"**Time Period: {period}**")
    st.markdown("---")

    if filtered_df.empty:
        st.info("No data found for this period!")
    else:
        # filter out unknown
        known_df = filtered_df[filtered_df["employee_name"] != "Unknown"]

        # group by employee
        employee_summary = known_df.groupby(
            ["employee_name", "department"]
        ).agg(
            total_calls=("tokens_used", "count"),
            total_tokens=("tokens_used", "sum"),
            total_cost=("cost_usd", "sum")
        ).reset_index()

        employee_summary["total_cost"] = employee_summary["total_cost"].apply(
            lambda x: f"${float(x):.6f}"
        )

        st.subheader("📋 Employee Summary Table")
        st.dataframe(
            employee_summary.rename(columns={
                "employee_name": "Employee Name",
                "department": "Department",
                "total_calls": "Total Calls",
                "total_tokens": "Total Tokens",
                "total_cost": "Total Cost"
            }),
            use_container_width=True
        )

        st.markdown("---")

        # individual employee detail
        st.subheader("🔍 Individual Employee Detail")
        selected_employee = st.selectbox(
            "Select Employee",
            known_df["employee_name"].unique()
        )

        emp_detail = filtered_df[
            filtered_df["employee_name"] == selected_employee
        ].sort_values("timestamp", ascending=False)

        st.dataframe(
            emp_detail[["timestamp", "question", "tokens_used", "cost_usd"]].rename(columns={
                "timestamp": "Time",
                "question": "Question Asked",
                "tokens_used": "Tokens",
                "cost_usd": "Cost"
            }),
            use_container_width=True
        )

        # spending limit check
        for emp_key, emp_data in api_keys.items():
            if emp_data["name"] == selected_employee:
                spent = emp_detail["cost_usd"].astype(float).sum()
                limit = emp_data["monthly_limit_usd"]
                percentage = (spent / limit) * 100
                st.markdown("---")
                st.subheader("💰 Spending Limit")
                st.progress(min(percentage / 100, 1.0))
                st.write(f"Used: ${spent:.6f} / Limit: ${limit} ({percentage:.1f}%)")
                if percentage >= 80:
                    st.warning(f"⚠️ {selected_employee} is close to their spending limit!")
                else:
                    st.success(f"✅ {selected_employee} is within limits!")





# ── PAGE 3 — LEADERBOARD ──
elif page == "🏆 Leaderboard":
    st.title("🏆 Leaderboard")
    st.markdown(f"**Time Period: {period}**")
    st.markdown("---")

    if filtered_df.empty:
        st.info("No data found for this period!")
    else:
        known_df = filtered_df[filtered_df["employee_name"] != "Unknown"]

        if known_df.empty:
            st.info("No known employee data found!")
        else:
            # leaderboard by calls
            st.subheader("📞 Most API Calls")
            calls_board = known_df.groupby("employee_name").agg(
                total_calls=("tokens_used", "count"),
                department=("department", "first")
            ).sort_values("total_calls", ascending=False).reset_index()

            # add rank
            calls_board.insert(0, "Rank", range(1, len(calls_board) + 1))

            st.dataframe(
                calls_board.rename(columns={
                    "employee_name": "Employee",
                    "department": "Department",
                    "total_calls": "Total Calls"
                }),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            # leaderboard by tokens
            st.subheader("🔤 Most Tokens Used")
            tokens_board = known_df.groupby("employee_name").agg(
                total_tokens=("tokens_used", "sum"),
                department=("department", "first")
            ).sort_values("total_tokens", ascending=False).reset_index()

            tokens_board.insert(0, "Rank", range(1, len(tokens_board) + 1))

            st.dataframe(
                tokens_board.rename(columns={
                    "employee_name": "Employee",
                    "department": "Department",
                    "total_tokens": "Total Tokens"
                }),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            # leaderboard by cost
            st.subheader("💰 Highest Spenders")
            cost_board = known_df.groupby("employee_name").agg(
                total_cost=("cost_usd", "sum"),
                department=("department", "first")
            ).sort_values("total_cost", ascending=False).reset_index()

            cost_board["total_cost"] = cost_board["total_cost"].apply(
                lambda x: f"${float(x):.6f}"
            )
            cost_board.insert(0, "Rank", range(1, len(cost_board) + 1))

            st.dataframe(
                cost_board.rename(columns={
                    "employee_name": "Employee",
                    "department": "Department",
                    "total_cost": "Total Cost"
                }),
                use_container_width=True,
                hide_index=True
            )



# ── PAGE 4 — SECURITY ALERTS ──
elif page == "🚨 Security Alerts":
    st.title("🚨 Security Alerts")
    st.markdown(f"**Time Period: {period}**")
    st.markdown("---")

    if filtered_df.empty:
        st.info("No data found for this period!")
    else:
        unknown_df = filtered_df[filtered_df["employee_name"] == "Unknown"]

        if unknown_df.empty:
            st.success("✅ No security threats detected in this period!")
        else:
            st.error(f"🚨 {len(unknown_df)} unauthorized API call(s) detected!")
            st.markdown("---")

            # unknown attempts table
            st.subheader("⚠️ Unauthorized Access Attempts")
            st.dataframe(
                unknown_df[["timestamp", "api_key", "question", "tokens_used", "cost_usd"]].rename(columns={
                    "timestamp": "Time",
                    "api_key": "Unknown Key Used",
                    "question": "Question Asked",
                    "tokens_used": "Tokens",
                    "cost_usd": "Cost"
                }).sort_values("Time", ascending=False),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            # summary stats
            st.subheader("📊 Threat Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🔑 Unknown Keys",
                    unknown_df["api_key"].nunique()
                )
            with col2:
                st.metric(
                    "📞 Total Unauthorized Calls",
                    len(unknown_df)
                )
            with col3:
                total_cost = unknown_df["cost_usd"].astype(float).sum()
                st.metric(
                    "💸 Cost from Unknown",
                    f"${total_cost:.6f}"
                )

            st.markdown("---")

            # which unknown keys were used
            st.subheader("🔑 Unknown Keys Detail")
            key_summary = unknown_df.groupby("api_key").agg(
                total_calls=("tokens_used", "count"),
                total_tokens=("tokens_used", "sum"),
                first_seen=("timestamp", "min"),
                last_seen=("timestamp", "max")
            ).reset_index()

            st.dataframe(
                key_summary.rename(columns={
                    "api_key": "Unknown Key",
                    "total_calls": "Total Calls",
                    "total_tokens": "Total Tokens",
                    "first_seen": "First Seen",
                    "last_seen": "Last Seen"
                }),
                use_container_width=True,
                hide_index=True
            )


# ── PAGE 5 — ANALYTICS ──
elif page == "📊 Analytics":
    st.title("📊 Analytics")
    st.markdown(f"**Time Period: {period}**")
    st.markdown("---")

    if filtered_df.empty:
        st.info("No data found for this period!")
    else:
        import plotly.express as px

        # ── CHART 1 — API calls per employee ──
        st.subheader("📞 API Calls per Employee")
        known_df = filtered_df[filtered_df["employee_name"] != "Unknown"]

        calls_per_emp = known_df.groupby("employee_name").agg(
            total_calls=("tokens_used", "count")
        ).reset_index()

        fig1 = px.bar(
            calls_per_emp,
            x="employee_name",
            y="total_calls",
            color="employee_name",
            color_discrete_sequence=px.colors.sequential.Greens,
            labels={"employee_name": "Employee", "total_calls": "Total Calls"},
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        # ── CHART 2 — Cost per department ──
        st.subheader("💰 Cost per Department")
        dept_cost = known_df.groupby("department").agg(
            total_cost=("cost_usd", "sum")
        ).reset_index()

        dept_cost["total_cost"] = dept_cost["total_cost"].astype(float)

        fig2 = px.pie(
            dept_cost,
            names="department",
            values="total_cost",
            color_discrete_sequence=px.colors.sequential.Greens,
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # ── CHART 3 — Tokens used over time ──
        st.subheader("📈 Tokens Used Over Time")
        time_df = filtered_df.copy()
        time_df["hour"] = time_df["timestamp"].dt.strftime("%H:%M")

        tokens_time = time_df.groupby("hour").agg(
            total_tokens=("tokens_used", "sum")
        ).reset_index()

        fig3 = px.line(
            tokens_time,
            x="hour",
            y="total_tokens",
            labels={"hour": "Time", "total_tokens": "Total Tokens"},
            color_discrete_sequence=["#38a169"]
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")

        # ── CHART 4 — Known vs Unknown calls ──
        st.subheader("🔐 Authorized vs Unauthorized Calls")
        auth_data = pd.DataFrame({
            "Type": ["Authorized", "Unauthorized"],
            "Calls": [
                len(filtered_df[filtered_df["employee_name"] != "Unknown"]),
                len(filtered_df[filtered_df["employee_name"] == "Unknown"])
            ]
        })

        fig4 = px.pie(
            auth_data,
            names="Type",
            values="Calls",
            color_discrete_sequence=["#38a169", "#fc8181"]
        )
        st.plotly_chart(fig4, use_container_width=True)                                                    