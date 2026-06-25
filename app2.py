import streamlit as st
import pandas as pd
import plotly.express as px
RATE_MAP = {
    "CAR": 80,
    "AUTO/ 2 Wheeler": 0,

    "LCV": 125,

    "TRUCK 2 AXLE": 265,
    "Truck 2 AXLE": 265,
    "BUS 2 AXLE": 265,

    "TRUCK 3 AXLE": 290,
    "Truck 3 AXLE": 290,

    "MAV 4 To 6 AXLE": 415,

    "TRACTOR": 505
}
from parser2 import load_transaction

st.set_page_config(
    page_title="Toll AI Insights Prototype 2",
    layout="wide"
)

st.title("Toll Insights Prototype")
st.caption("Transaction Report → Insights → Executive Summary")

col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader(
        "Day 1 Report",
        type="xlsx",
        key="day1"
    )

with col2:
    file2 = st.file_uploader(
        "Day 2 Report",
        type="xlsx",
        key="day2"
    )


# ==========================
# LOAD DATA
# ==========================

if file1 and file2:

    txn_df = load_transaction(file1)
    txn_df2 = load_transaction(file2)

    # ==========================
    # CLEAN DATA
    # ==========================
    txn_df["Operator Class"] = (
        txn_df["Operator Class"]
        .astype(str)
        .str.strip()
    )

    txn_df2["Operator Class"] = (
        txn_df2["Operator Class"]
        .astype(str)
        .str.strip()
    )
    txn_df["Estimated Rate"] = (
        txn_df["Operator Class"]
        .map(RATE_MAP)
        .fillna(0)
    )

    txn_df2["Estimated Rate"] = (
        txn_df2["Operator Class"]
        .map(RATE_MAP)
        .fillna(0)
    )
    # ==========================
    # DAY 1 METRICS
    # ==========================

    total_day1 = len(txn_df)
    revenue_day1 = txn_df["Estimated Rate"].sum()
    vehicle_day1 = txn_df["Operator Class"].nunique()
    lanes_day1 = txn_df["Origin"].nunique()

    # ==========================
    # DAY 2 METRICS
    # ==========================

    total_day2 = len(txn_df2)
    revenue_day2 = txn_df2["Estimated Rate"].sum()
    vehicle_day2 = txn_df2["Operator Class"].nunique()
    lanes_day2 = txn_df2["Origin"].nunique()

    traffic_change = (
        (total_day2 - total_day1)
        / total_day1
    ) * 100

    # ==========================
    # EXEMPT ANALYSIS
    # ==========================

    txn_df2["Cancel"] = (
        txn_df2["Cancel"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    exempt_df = txn_df2[
        txn_df2["Cancel"] != ""
    ]

    exempt_count = len(exempt_df)

    exempt_pct = (
        exempt_count / total_day2
    ) * 100

    # ==========================
    # KPI SECTION
    # ==========================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Transactions",
        f"{total_day2:,}",
        f"{traffic_change:+.2f}%"
    )

    revenue_change = revenue_day2 - revenue_day1

    delta = (
        f"-₹{abs(revenue_change):,.0f}"
        if revenue_change < 0
        else f"+₹{revenue_change:,.0f}"
    )

    c2.metric(
        "Revenue",
        f"₹{revenue_day2:,.0f}",
        delta
    )

    c3.metric(
        "Vehicle Classes",
        vehicle_day2,
        vehicle_day2 - vehicle_day1
    )

    c4.metric(
        "Active Lanes",
        lanes_day2,
        lanes_day2 - lanes_day1
    )

    c5.metric(
        "Exempt Vehicles",
        exempt_count
    )

    c6.metric(
        "Exempt %",
        f"{exempt_pct:.2f}%"
    )

    st.divider()
    # Use Day 2 for all remaining analysis
    txn_df = txn_df2

    total_transactions = total_day2
    active_lanes = lanes_day2
    vehicle_classes = vehicle_day2
    # ==========================
    # VEHICLE ANALYSIS
    # ==========================

    vehicle_pct = (
        txn_df["Operator Class"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    top_vehicle_name = vehicle_pct.idxmax()
    top_vehicle_pct = vehicle_pct.max()

    # ==========================
    # LANE ANALYSIS
    # ==========================

    lane_pct = (
        txn_df["Origin"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    top_lane_name = lane_pct.idxmax()
    top_lane_pct = lane_pct.max()

    # ==========================
    # TIME ANALYSIS
    # ==========================

    txn_df["Date-Time (DD/MM/YYYY)"] = pd.to_datetime(
        txn_df["Date-Time (DD/MM/YYYY)"],
        dayfirst=True,
        errors="coerce"
    )

    txn_df["Hour"] = (
        txn_df["Date-Time (DD/MM/YYYY)"]
        .dt.hour
    )
    hourly_lane = (
        txn_df.groupby(
            ["Hour", "Origin"]
        )
        .size()
        .reset_index(name="Transactions")
    )

    hourly = (
        txn_df
        .groupby("Hour")
        .size()
    )

    peak_hour = hourly.idxmax()
    peak_volume = hourly.max()

    # ==========================
    # EXECUTIVE SUMMARY
    # ==========================

    st.header("📋 Executive Summary")

    st.success(
        f"""
        Analysed {total_transactions:,} transactions across
        {active_lanes} active lanes and
        {vehicle_classes} vehicle classes.
        """
    )
    # Heavy Vehicle Analysis

    heavy_vehicle_keywords = [
        "truck",
        "bus",
        "mav",
        "trailer",
        "multi axle"
    ]
    
    heavy_count = 0

    for vehicle, count in (
        txn_df["Operator Class"]
        .value_counts()
        .items()
    ):
        if any(
            keyword in str(vehicle)
            for keyword in heavy_vehicle_keywords
        ):
            heavy_count += count

    heavy_pct = (
        heavy_count / total_transactions
    ) * 100

    # ==========================
    # AI SUMMARY
    # ==========================
    st.header("🤖 AI Insights (Prototype)")

    ai_insights = []

    if top_vehicle_pct > 50:
        ai_insights.append(
            f"Traffic is primarily dominated by {top_vehicle_name} ({top_vehicle_pct:.1f}%), indicating a consistent vehicle composition."
        )

    if top_lane_pct > 25:
        ai_insights.append(
            f"{top_lane_name} carries a significantly higher traffic load than other lanes and may require operational monitoring."
        )

    if peak_volume > hourly.mean() * 2:
        ai_insights.append(
            f"Traffic peaks around {peak_hour}:00, suggesting this period may require additional staffing or lane optimization."
        )

    if heavy_pct > 25:
        ai_insights.append(
            f"Heavy commercial vehicles contribute {heavy_pct:.1f}% of total traffic, which may influence pavement wear and congestion."
        )

    if not ai_insights:
        ai_insights.append(
            "No significant operational anomalies were detected in this report."
        )

    for i, insight in enumerate(ai_insights, 1):
        st.info(f"AI Insight {i}: {insight}")

    st.caption(
        "Prototype: These insights are currently generated using analytical rules. Future versions can leverage LLMs and historical ERP data for richer explanations and predictive insights."
    )
    # ==========================
    # MANAGEMENT SUMMARY
    # ==========================

    st.subheader("🧠 Management Summary")

    summary = f"""
    • Total Transactions: {total_transactions:,}

    • Dominant Vehicle Category: {top_vehicle_name}
    ({top_vehicle_pct:.1f}% of traffic)

    • Most Utilized Lane: {top_lane_name}
    ({top_lane_pct:.1f}% of traffic)

    • Peak Traffic Hour: {peak_hour}:00

    • Active Lanes Observed: {active_lanes}

    • Vehicle Categories Observed: {vehicle_classes}
    """

    st.info(summary)

    # ==========================
    # KEY FINDINGS
    # ==========================

    st.subheader("🔍 Key Findings")

    st.write(
        f"• {top_vehicle_name} accounts for "
        f"{top_vehicle_pct:.1f}% of total traffic."
    )

    st.write(
        f"• {top_lane_name} handled "
        f"{top_lane_pct:.1f}% of all transactions."
    )

    st.write(
        f"• Peak traffic occurred around "
        f"{peak_hour}:00 with "
        f"{peak_volume:,} transactions."
    )

    st.write(
        f"• A total of {total_transactions:,} vehicles "
        f"were processed during the analysed period."
    )

    # ==========================
    # POTENTIAL OBSERVATIONS
    # ==========================

    st.subheader("⚠️ Potential Observations")

    observations = []

    if top_vehicle_pct > 50:
        observations.append(
            f"{top_vehicle_name} dominates traffic composition ({top_vehicle_pct:.1f}%)."
        )

    if top_lane_pct > 25:
        observations.append(
            f"{top_lane_name} is carrying a significant portion of traffic ({top_lane_pct:.1f}%)."
        )

    if peak_volume > hourly.mean() * 2:
        observations.append(
            "Peak hour traffic is significantly above average hourly traffic."
        )

    if heavy_pct > 25:
        observations.append(
            f"Heavy vehicles contribute {heavy_pct:.1f}% of total traffic."
        )

    if not observations:
        observations.append(
            "No major traffic concentration patterns detected."
        )

    for obs in observations:
        st.warning(obs)
    # ==========================
    # CHARTS
    # ==========================

    st.header("📊 Supporting Analysis")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        vehicle_counts = (
            txn_df["Operator Class"]
            .value_counts()
            .reset_index()
        )

        vehicle_counts.columns = [
            "Vehicle",
            "Count"
        ]
        payment_counts = (
            txn_df["Payment Mode"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        payment_counts.columns = [
            "Payment",
            "Transactions"
        ]
        st.subheader("💳 Payment Intelligence")

        fig_payment = px.pie(
            payment_counts,
            names="Payment",
            values="Transactions",
            hole=0.45,
            title="Payment Mode Distribution"
        )

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )
        fig_vehicle = px.pie(
            vehicle_counts,
            names="Vehicle",
            values="Count",
            title="Vehicle Distribution"
        )

        st.plotly_chart(
            fig_vehicle,
            use_container_width=True
        )

    with chart_col2:

        lane_counts = (
            txn_df["Origin"]
            .value_counts()
            .reset_index()
        )

        lane_counts.columns = [
            "Lane",
            "Transactions"
        ]

        fig_lane = px.bar(
            lane_counts,
            x="Lane",
            y="Transactions",
            title="Lane Performance"
        )

        st.plotly_chart(
            fig_lane,
            use_container_width=True
        )
        st.divider()
        
    payment_counts = (
        txn_df["Payment Mode"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    payment_counts.columns = [
        "Payment",
        "Transactions"
    ]
    st.subheader("💳 Payment Intelligence")

    # fig_payment = px.pie(
    #     payment_counts,
    #     names="Payment",
    #     values="Transactions",
    #     hole=0.45,
    #     title="Payment Mode Distribution"
    # )

    # st.plotly_chart(
    #     fig_payment,
    #     use_container_width=True
    # )   
    top_payment = payment_counts.iloc[0]["Payment"]

    top_payment_pct = (
        payment_counts.iloc[0]["Transactions"]
        / total_transactions
    ) * 100

    st.info(
        f"🤖 AI Insight: {top_payment} transactions account for "
        f"{top_payment_pct:.1f}% of all toll collections."
    )
    txn_df["Cancel"] = (
        txn_df["Cancel"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    exempt_df = txn_df[
        txn_df["Cancel"] != ""
    ]

    exempt_count = len(exempt_df)

    exempt_pct = (
        exempt_count / total_transactions
    ) * 100
    # ==========================
    # HOURLY LANE PERFORMANCE
    # ==========================

    st.subheader("🚦 Hourly Lane Performance")

    hourly_lane = (
        txn_df.groupby(["Hour", "Origin"])
        .size()
        .reset_index(name="Transactions")
    )

    # Create 12-hour labels
    hourly_lane["Time"] = hourly_lane["Hour"].apply(
        lambda x: pd.Timestamp(
            f"2025-01-01 {int(x)}:00"
        ).strftime("%I %p")
    )

    # Proper lane sorting
    hourly_lane["Lane_Num"] = (
        hourly_lane["Origin"]
        .astype(str)
        .str.replace("LANE", "", regex=False)
        .astype(int)
    )

    hourly_lane = hourly_lane.sort_values(
        ["Lane_Num", "Hour"]
    )

    # Proper time order
    time_order = [
        pd.Timestamp(
            f"2025-01-01 {h}:00"
        ).strftime("%I %p")
        for h in range(24)
    ]

    # Lane selector
    lane_options = ["All Lanes"] + sorted(
        txn_df["Origin"]
        .dropna()
        .astype(str)
        .unique(),
        key=lambda x: int(x.replace("LANE", ""))
    )

    selected_lane = st.selectbox(
        "Select Lane",
        lane_options
    )

    # Filter data
    if selected_lane == "All Lanes":
        chart_data = hourly_lane
    else:
        chart_data = hourly_lane[
            hourly_lane["Origin"] == selected_lane
        ]

    # Plot chart
    fig_hourly_lane = px.line(
        chart_data,
        x="Time",
        y="Transactions",
        color="Origin",
        markers=True,
        title="Hourly Lane Performance",
        category_orders={
            "Time": time_order,
            "Origin": sorted(
                chart_data["Origin"]
                .astype(str)
                .unique(),
                key=lambda x: int(x.replace("LANE", ""))
            )
        }
    )

    st.plotly_chart(
        fig_hourly_lane,
        use_container_width=True
    )
    #======================
    # TRAFFIC TREND
    # ==========================

    st.subheader("⏰ Hourly Traffic Pattern")

    hourly_df = hourly.reset_index()

    hourly_df.columns = [
        "Hour",
        "Transactions"
    ]

    fig_hourly = px.line(
        hourly_df,
        x="Hour",
        y="Transactions",
        markers=True,
        title="Hourly Traffic Distribution"
    )
    # # ==========================
    # # REPORT COMPARISON
    # # ==========================

    # if file2:

    #     st.header("📈 Report Comparison")

    #     total_day1 = len(txn_df)
    #     total_day2 = len(txn_df2)

    #     vehicle_day1 = txn_df["Operator Class"].nunique()
    #     vehicle_day2 = txn_df2["Operator Class"].nunique()

    #     lanes_day1 = txn_df["Origin"].nunique()
    #     lanes_day2 = txn_df2["Origin"].nunique()

    #     c1, c2, c3 = st.columns(3)

    #     c1.metric(
    #         "Transactions",
    #         f"{total_day2:,}",
    #         f"{total_day2-total_day1:+,}"
    #     )

    #     c2.metric(
    #         "Vehicle Classes",
    #         vehicle_day2,
    #         vehicle_day2-vehicle_day1
    #     )

    #     c3.metric(
    #         "Active Lanes",
    #         lanes_day2,
    #         lanes_day2-lanes_day1
    #     )
    # comparison = []

    # change = (
    #     (total_day2-total_day1)
    #     / total_day1
    # ) * 100

    # if change > 0:
    #     comparison.append(
    #         f"Traffic increased by {change:.1f}% compared to Day 1."
    #     )
    # else:
    #     comparison.append(
    #         f"Traffic decreased by {abs(change):.1f}% compared to Day 1."
    #     )

    # top1 = txn_df["Operator Class"].value_counts().idxmax()
    # top2 = txn_df2["Operator Class"].value_counts().idxmax()

    # if top1 == top2:
    #     comparison.append(
    #         f"{top1} remained the dominant vehicle category on both days."
    #     )
    # else:
    #     comparison.append(
    #         f"Dominant vehicle shifted from {top1} to {top2}."
    #     )

    # for msg in comparison:
    #     st.success("🤖 " + msg)
    # ==========================
    # AI COMPARATIVE ANALYSIS
    # ==========================

    if file2:

        st.divider()

        st.header("🧠 AI Comparative Analysis")

        st.success(
            "Two reports detected. AI generated a comparison automatically."
        )

        comparison = []

        if traffic_change > 0:
            comparison.append(
                f"Traffic increased by {traffic_change:.2f}% compared to Day 1."
            )
        else:
            comparison.append(
                f"Traffic decreased by {abs(traffic_change):.2f}% compared to Day 1."
            )

        top_vehicle_day1 = txn_df["Operator Class"].value_counts().idxmax()
        top_vehicle_day2 = txn_df2["Operator Class"].value_counts().idxmax()

        if top_vehicle_day1 == top_vehicle_day2:
            comparison.append(
                f"{top_vehicle_day1} remained the dominant vehicle category."
            )
        else:
            comparison.append(
                f"Dominant vehicle shifted from {top_vehicle_day1} to {top_vehicle_day2}."
            )

        top_lane_day1 = txn_df["Origin"].value_counts().idxmax()
        top_lane_day2 = txn_df2["Origin"].value_counts().idxmax()

        if top_lane_day1 == top_lane_day2:
            comparison.append(
                f"{top_lane_day1} remained the busiest lane."
            )
        else:
            comparison.append(
                f"Busiest lane shifted from {top_lane_day1} to {top_lane_day2}."
            )

        st.subheader("🤖 AI Summary")

        for msg in comparison:
            st.info(msg)
            comparison_df = pd.DataFrame({

                "Metric":[
                    "Transactions",
                    "Revenue",
                    "Active Lanes"
                ],

                "Day 1":[
                    total_day1,
                    revenue_day1,
                    lanes_day1
                ],

                "Day 2":[
                    total_day2,
                    revenue_day2,
                    lanes_day2
                ]
            })

        st.subheader("📊 Comparison Table")

        st.dataframe(
            comparison_df,
            use_container_width=True
        )

        st.divider()
    # ==========================
    # DATA PREVIEW
    # ==========================

    with st.expander("View Raw Data"):
        st.dataframe(txn_df.head(20))