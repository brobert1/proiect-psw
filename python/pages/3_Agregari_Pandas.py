"""Agregări pandas: groupby, funcții de grup, rolling."""

import plotly.express as px
import streamlit as st

from utils.data_loader import load_data
from utils.economics import kwh_to_eur
from utils.plots import bar

st.set_page_config(page_title="Agregări Pandas", page_icon="📊", layout="wide")
st.title("📊 Agregări & funcții de grup (pandas)")

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Groupby + agg", "Pivot lună × zi", "Funcții de grup", "Rolling 24h"]
)

with tab1:
    st.subheader("Agregare după tipul de sarcină")
    by_load = df.groupby("Load_Type").agg(
        n_obs=("Usage_kWh", "count"),
        kwh_total=("Usage_kWh", "sum"),
        kwh_medie=("Usage_kWh", "mean"),
        pf_mediu=("Lagging_PF", "mean"),
        co2_total=("CO2_tCO2", "sum"),
    ).round(2)
    by_load["cost_eur"] = kwh_to_eur(by_load["kwh_total"]).round(0)
    st.dataframe(by_load, width="stretch")

    st.subheader("Agregare după starea săptămânii")
    by_week = df.groupby("WeekStatus").agg(
        kwh_total=("Usage_kWh", "sum"),
        kwh_medie=("Usage_kWh", "mean"),
        co2_total=("CO2_tCO2", "sum"),
    ).round(2)
    st.dataframe(by_week, width="stretch")

    st.plotly_chart(
        bar(by_load.reset_index(), "Load_Type", "cost_eur",
            "Cost total estimat per tip de sarcină (EUR)"),
        width="stretch",
    )

with tab2:
    pivot = df.pivot_table(
        index="Day_of_week", columns="month", values="Usage_kWh", aggfunc="sum"
    ).round(0)
    st.dataframe(pivot, width="stretch")
    fig = px.imshow(pivot, title="Pivot kWh: zi × lună", aspect="auto",
                    color_continuous_scale="Viridis")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Interpretare: lunile de vară prezintă consum mai ridicat la mijlocul "
        "săptămânii — oportun pentru negocierea tarifelor de vârf cu furnizorul."
    )

with tab3:
    st.subheader("transform — abatere față de media zilei")
    df["kwh_mean_day"] = df.groupby("day")["Usage_kWh"].transform("mean")
    df["kwh_dev_day"] = df["Usage_kWh"] - df["kwh_mean_day"]
    st.dataframe(df[["date", "Usage_kWh", "kwh_mean_day", "kwh_dev_day"]].head(12),
                 width="stretch")

    st.subheader("rank — topul orelor cu consum maxim")
    df["rank_hourly"] = df.groupby("day")["Usage_kWh"].rank(method="dense",
                                                            ascending=False)
    top = df[df["rank_hourly"] <= 3].groupby("hour").size().reset_index(
        name="frecvență")
    st.plotly_chart(
        bar(top, "hour", "frecvență", "Distribuția orelor de vârf (top-3 pe zi)"),
        width="stretch",
    )

with tab4:
    daily = df.groupby("day", as_index=False)["Usage_kWh"].sum()
    daily["rolling_7z"] = daily["Usage_kWh"].rolling(7, min_periods=1).mean()
    daily["rolling_30z"] = daily["Usage_kWh"].rolling(30, min_periods=1).mean()
    fig = px.line(daily, x="day", y=["Usage_kWh", "rolling_7z", "rolling_30z"],
                  title="Consum zilnic vs medii mobile")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Mediile mobile netezesc variațiile săptămânale și evidențiază sezonalitatea "
        "anuală — baza pentru planificarea bugetului energetic trimestrial."
    )
