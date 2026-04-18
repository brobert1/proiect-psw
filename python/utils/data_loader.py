"""Încărcarea și preprocesarea minimală a setului Daewoo Steel."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Steel_industry_data.csv"


@st.cache_data(show_spinner="Se încarcă setul de date...")
def load_data():
    """Citește CSV-ul și îmbogățește cu coloane derivate de timp."""
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y %H:%M")

    df["hour"] = df["date"].dt.hour
    df["day"] = df["date"].dt.date
    df["month"] = df["date"].dt.month
    df["weekday_num"] = df["date"].dt.weekday

    df = df.rename(columns={
        "Lagging_Current_Reactive.Power_kVarh": "Lagging_Reactive_kVarh",
        "Leading_Current_Reactive_Power_kVarh": "Leading_Reactive_kVarh",
        "CO2(tCO2)": "CO2_tCO2",
        "Lagging_Current_Power_Factor": "Lagging_PF",
        "Leading_Current_Power_Factor": "Leading_PF",
    })
    return df


NUMERIC_COLS = [
    "Usage_kWh",
    "Lagging_Reactive_kVarh",
    "Leading_Reactive_kVarh",
    "CO2_tCO2",
    "Lagging_PF",
    "Leading_PF",
    "NSM",
]

CATEGORICAL_COLS = ["WeekStatus", "Day_of_week", "Load_Type"]
