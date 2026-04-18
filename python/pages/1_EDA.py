"""Analiză exploratorie a datelor (EDA)."""

import plotly.express as px
import streamlit as st

from utils.data_loader import NUMERIC_COLS, load_data
from utils.plots import heatmap, time_series

st.set_page_config(page_title="EDA", page_icon="🔎", layout="wide")
st.title("🔎 Analiză exploratorie")

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Descriere", "Distribuții", "Serie de timp", "Corelații"]
)

with tab1:
    st.subheader("Statistică descriptivă (numerice)")
    st.dataframe(df[NUMERIC_COLS].describe().T.round(3), width="stretch")

    st.subheader("Distribuția categoriilor")
    c1, c2, c3 = st.columns(3)
    c1.write("**WeekStatus**")
    c1.dataframe(df["WeekStatus"].value_counts())
    c2.write("**Day_of_week**")
    c2.dataframe(df["Day_of_week"].value_counts())
    c3.write("**Load_Type**")
    c3.dataframe(df["Load_Type"].value_counts())

with tab2:
    col = st.selectbox("Alege o variabilă numerică", NUMERIC_COLS)
    fig = px.histogram(df, x=col, nbins=60, marginal="box", title=f"Distribuția {col}")
    st.plotly_chart(fig, width="stretch")

with tab3:
    daily = df.groupby("day", as_index=False).agg(
        kWh=("Usage_kWh", "sum"),
        tCO2=("CO2_tCO2", "sum"),
    )
    st.plotly_chart(time_series(daily, "day", "kWh", "Consum zilnic (kWh)"),
                    width="stretch")
    st.plotly_chart(time_series(daily, "day", "tCO2", "Emisii CO2 zilnice (t)"),
                    width="stretch")

with tab4:
    corr = df[NUMERIC_COLS].corr().round(2)
    st.plotly_chart(heatmap(corr, "Matricea de corelații (Pearson)"),
                    width="stretch")
    st.caption(
        "Interpretare economică: corelațiile puternice pozitive între `Usage_kWh`, "
        "`Lagging_Reactive_kVarh` și `CO2_tCO2` sugerează că reducerea componentei "
        "reactive (prin compensare capacitivă) va reduce simultan și costul activ, "
        "și amprenta de carbon."
    )
