# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("kpis.csv")

    # 1) Strip common prefix
    PREFIX = "SA_20250414_L_G0_O_Tier_1_"
    df["test_name"] = df["test_name"].str.replace(PREFIX, "", regex=False)

    # 2) Rename into human-readable names
    df = df.rename(columns={
        "test_name":              "Test Name",
        "target_group":           "Target Group",
        "test_variant":           "Variant",
        "orders":                 "Orders",
        "users":                  "Users",
        "avg_df":                 "Avg DF",
        "avg_fv":                 "Avg FV",
        "avg_commission":         "Avg Commission",
        "avg_delivery_cost":      "Avg Delivery Cost",
        "avg_distance_km":        "Avg Distance (km)",
        "avg_gmv":                "Avg GMV",
        "avg_revenue":            "Avg Revenue",
        "avg_travel_time":        "Avg Travel Time",
        "avg_to_customer_time":   "Avg To Customer Time",
        "vendor_rdf_fee":         "Vendor RDF Fee",
        "trade_mktg_fee":         "Trade Marketing Fee",
        "vendor_hplus_fee":       "Vendor H+ Fee",
        "user_paid_fee":          "User Paid Fee",
        "DF_Revenue":             "DF Revenue"
    })

    return df

df = load_data()

st.title("A/B Test Metrics Dashboard")

# —— Sidebar filters ——
test = st.sidebar.selectbox("Test Name", df["Test Name"].unique())
tg   = st.sidebar.selectbox(
    "Target Group",
    df[df["Test Name"] == test]["Target Group"].unique()
)
sub = df[(df["Test Name"] == test) & (df["Target Group"] == tg)]

# automatically pick all numeric columns as metrics
numeric_cols = sub.select_dtypes("number").columns.tolist()

metric = st.sidebar.selectbox("Which metric to compare?", numeric_cols)

# —— Main chart ——
fig = px.bar(
    sub,
    x="Variant",
    y=metric,
    color="Variant",
    text_auto=True,
    title=f"{metric} by Variant"
)
st.plotly_chart(fig, use_container_width=True)

# —— Multi-metric view ——
if st.sidebar.checkbox("Show multiple metrics"):
    to_plot = st.sidebar.multiselect("Select metrics", numeric_cols, default=[metric])
    dfm = sub.melt(
        id_vars=["Variant"],
        value_vars=to_plot,
        var_name="Metric",
        value_name="Value"
    )
    fig2 = px.line(
        dfm, x="Metric", y="Value", color="Variant", markers=True,
        title="Comparison across metrics"
    )
    st.plotly_chart(fig2, use_container_width=True)

# —— Underlying data (transposed) ——
st.subheader("Underlying data (transposed)")
st.dataframe(sub.set_index("Variant").T)
