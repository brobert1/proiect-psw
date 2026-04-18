"""Clusterizare KMeans pe profile zilnice orare."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils.data_loader import load_data
from utils.economics import kwh_to_eur

st.set_page_config(page_title="Clusterizare", page_icon="🧩", layout="wide")
st.title("🧩 Clusterizare KMeans — regimuri de funcționare")

df = load_data()

profile = df.groupby(["day", "hour"])["Usage_kWh"].mean().unstack(fill_value=0)
profile.columns = [f"h{h:02d}" for h in profile.columns]

st.caption(
    f"Matricea zile × ore: {profile.shape[0]} zile, {profile.shape[1]} ore. "
    "Fiecare rând = profil mediu de consum într-o zi."
)

scaler = StandardScaler()
X = scaler.fit_transform(profile)

st.subheader("1) Metoda cotului (elbow)")
ks = list(range(2, 9))
inertias, sils = [], []
for k in ks:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inertias.append(km.inertia_)
    sils.append(silhouette_score(X, km.labels_))

elbow_df = pd.DataFrame({"k": ks, "inertia": inertias, "silhouette": sils})
c1, c2 = st.columns(2)
c1.plotly_chart(px.line(elbow_df, x="k", y="inertia", markers=True,
                        title="Inerția vs k"), width="stretch")
c2.plotly_chart(px.line(elbow_df, x="k", y="silhouette", markers=True,
                        title="Silhouette vs k"), width="stretch")

k = st.slider("Alege numărul de clustere", 2, 8, value=4)
km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
profile["cluster"] = km.labels_

st.subheader(f"2) Centroizii celor {k} clustere (profil orar mediu)")
centroids = pd.DataFrame(
    scaler.inverse_transform(km.cluster_centers_),
    columns=profile.columns[:-1],
)
fig = go.Figure()
for i, row in centroids.iterrows():
    fig.add_trace(go.Scatter(
        x=list(range(24)), y=row.values, mode="lines+markers",
        name=f"Cluster {i} (n={(km.labels_ == i).sum()})",
    ))
fig.update_layout(title="Profil orar mediu pe cluster",
                  xaxis_title="ora", yaxis_title="kWh mediu",
                  height=450)
st.plotly_chart(fig, width="stretch")

st.subheader("3) Caracterizarea economică a clusterelor")
summary = profile.groupby("cluster").sum().sum(axis=1).round(1).to_frame("kWh_zi_mediu")
summary["cost_eur_zi"] = kwh_to_eur(summary["kWh_zi_mediu"]).round(1)
summary["n_zile"] = profile["cluster"].value_counts().sort_index()
st.dataframe(summary, width="stretch")

silhouette_val = silhouette_score(X, km.labels_)
st.metric("Silhouette score (k selectat)", f"{silhouette_val:.3f}")

st.markdown(
    """
    **Interpretare economică:** fiecare cluster reprezintă un *regim de
    funcționare* (zi nelucrătoare, schimb de noapte, producție continuă etc.).
    Identificarea lor permite:
    - contractarea de tarife diferențiate pentru zilele cu profil scăzut;
    - programarea mentenanței în clusterele cu consum minim;
    - benchmark intern — zilele atipice dintr-un cluster indică pierderi.
    """
)
