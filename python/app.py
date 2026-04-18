"""Pagină Home — prezentare generală Daewoo Steel energy consumption."""

import streamlit as st

from utils.data_loader import load_data
from utils.economics import EUR_PER_KWH, RON_PER_TCO2, kwh_to_eur, co2_to_ron

st.set_page_config(
    page_title="Daewoo Steel — Analiză energetică",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Daewoo Steel Co. — Eficiență energetică & optimizare de cost")
st.caption(
    "Proiect Pachete Software | CSIE an III | echipă: <NUME_1>, <NUME_2> — grupa <GRUPA>"
)

df = load_data()

st.markdown(
    """
    ### Contextul economic

    Daewoo Steel Co. este un producător sud-coreean de oțel laminat. Consumul
    energetic al fabricii a fost monitorizat la interval de **15 minute** pe
    durata anului **2018**, rezultând un set de **35.040 de observații**.

    Obiectivul proiectului este de a identifica **pârghiile de reducere a
    costurilor energetice și a emisiilor de CO2** prin:
    - segmentarea regimurilor de funcționare (clusterizare);
    - predicția perioadelor de sarcină maximă (regresie logistică);
    - cuantificarea factorilor care influențează consumul activ (regresie multiplă).
    """
)

st.subheader("Indicatori cheie pe întreg anul 2018")

total_kwh = df["Usage_kWh"].sum()
total_co2 = df["CO2_tCO2"].sum()
avg_pf = df["Lagging_PF"].mean()
n_days = df["day"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Consum activ total", f"{total_kwh:,.0f} kWh")
c2.metric("Cost energie estimat", f"{kwh_to_eur(total_kwh):,.0f} EUR")
c3.metric("Emisii CO2 (tone)", f"{total_co2:,.2f} t")
c4.metric("Factor putere mediu", f"{avg_pf:.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Cost ecologic CO2", f"{co2_to_ron(total_co2):,.0f} RON")
c6.metric("Zile monitorizate", f"{n_days}")
c7.metric("Tarif utilizat", f"{EUR_PER_KWH} EUR/kWh")
c8.metric("Taxă CO2 utilizată", f"{RON_PER_TCO2:.0f} RON/t")

st.subheader("Primele 10 înregistrări")
st.dataframe(df.head(10), width="stretch")

st.subheader("Navigare")
st.markdown(
    """
    Folosiți meniul din stânga pentru a parcurge analizele:
    1. **EDA** — explorare & statistică descriptivă
    2. **Preprocesare** — valori lipsă, outlieri, codificare, scalare
    3. **Agregări Pandas** — groupby, funcții de grup, rolling windows
    4. **Clusterizare** — KMeans pe profile zilnice
    5. **Regresie Logistică** — detectarea perioadelor de sarcină maximă
    6. **Regresie Multiplă** — cuantificarea driverilor de consum
    """
)
