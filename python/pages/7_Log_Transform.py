"""Transformarea logaritmică — justificare și impact."""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.data_loader import NUMERIC_COLS, load_data

st.set_page_config(page_title="Transformare Logaritmică", page_icon="📐", layout="wide")
st.title("📐 Transformarea logaritmică — justificare statistică")

df = load_data()

# ── Compute log transform ──────────────────────────────────────────────────
df["log_usage"] = np.log1p(df["Usage_kWh"])

skew_orig = df["Usage_kWh"].skew()
skew_log  = df["log_usage"].skew()
kurt_orig = df["Usage_kWh"].kurt()
kurt_log  = df["log_usage"].kurt()

# ── KPI row ────────────────────────────────────────────────────────────────
st.subheader("Indicatori de asimetrie și boltire")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Asimetrie (original)", f"{skew_orig:.3f}")
c2.metric("Asimetrie (log1p)", f"{skew_log:.3f}",
          delta=f"{skew_log - skew_orig:.3f}", delta_color="inverse")
c3.metric("Boltire (original)", f"{kurt_orig:.3f}")
c4.metric("Boltire (log1p)", f"{kurt_log:.3f}",
          delta=f"{kurt_log - kurt_orig:.3f}", delta_color="inverse")

st.markdown(
    """
    > **Interpretare:** O valoare absolută a asimetriei > 1 semnalează o distribuție
    puternic asimetrică. Transformarea `log1p` aduce asimetria mai aproape de 0,
    apropriind distribuția de cea normală — cerință frecventă în modelele de regresie.
    """
)
st.divider()

# ── Side-by-side histograms ────────────────────────────────────────────────
st.subheader("Distribuție: original vs. transformată logaritmic")

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=(
        "Usage_kWh (original)",
        "log1p(Usage_kWh) (transformată)",
    ),
)

fig.add_trace(
    go.Histogram(
        x=df["Usage_kWh"], nbinsx=80,
        marker_color="#636EFA", opacity=0.75,
        name="Original",
    ),
    row=1, col=1,
)
fig.add_trace(
    go.Histogram(
        x=df["log_usage"], nbinsx=80,
        marker_color="#EF553B", opacity=0.75,
        name="log1p",
    ),
    row=1, col=2,
)

fig.update_layout(
    height=420,
    showlegend=False,
    bargap=0.05,
)
fig.update_xaxes(title_text="Usage_kWh", row=1, col=1)
fig.update_xaxes(title_text="log1p(Usage_kWh)", row=1, col=2)
fig.update_yaxes(title_text="Frecvență", row=1, col=1)

st.plotly_chart(fig, use_container_width=True)

# ── Box-plot comparison ────────────────────────────────────────────────────
st.subheader("Boxplot comparativ pe tipul de sarcină")

fig2 = make_subplots(
    rows=1, cols=2,
    subplot_titles=("Usage_kWh (original)", "log1p(Usage_kWh)"),
)

for load_type, color in zip(
    df["Load_Type"].unique(), ["#636EFA", "#EF553B", "#00CC96"]
):
    sub = df[df["Load_Type"] == load_type]
    fig2.add_trace(
        go.Box(y=sub["Usage_kWh"], name=load_type, marker_color=color,
               legendgroup=load_type),
        row=1, col=1,
    )
    fig2.add_trace(
        go.Box(y=sub["log_usage"], name=load_type, marker_color=color,
               legendgroup=load_type, showlegend=False),
        row=1, col=2,
    )

fig2.update_layout(height=420, legend_title_text="Tip sarcină")
st.plotly_chart(fig2, use_container_width=True)

# ── Scatter: original vs log ───────────────────────────────────────────────
st.subheader("Relația dintre valoarea originală și cea transformată")
sample = df.sample(n=min(5000, len(df)), random_state=42)
fig3 = go.Figure(
    go.Scatter(
        x=sample["Usage_kWh"], y=sample["log_usage"],
        mode="markers", opacity=0.3,
        marker=dict(color="#AB63FA", size=4),
    )
)
fig3.update_layout(
    xaxis_title="Usage_kWh (original)",
    yaxis_title="log1p(Usage_kWh)",
    title="log1p(x) vs. x — curbă de compresie",
    height=380,
)
st.plotly_chart(fig3, use_container_width=True)

# ── Explanation ────────────────────────────────────────────────────────────
st.divider()
st.subheader("De ce aplicăm transformarea logaritmică?")

st.markdown(
    f"""
    #### 1. Reducerea asimetriei (skewness)

    Distribuția `Usage_kWh` prezintă o asimetrie pozitivă de **{skew_orig:.2f}**,
    cauzată de perioadele de sarcină maximă (spike-uri la pornirea agregatelor mari).
    Aceste valori extreme „trag" media spre dreapta și destabilizează estimatele
    modelelor liniare.

    După aplicarea `log1p(x) = ln(x + 1)`, asimetria scade la **{skew_log:.2f}**,
    distribuția devine mult mai simetrică și mai apropiată de normală.

    > **Notă:** `log1p` (în loc de `log`) se folosește pentru a evita eroarea
    `log(0)` atunci când există valori zero — adaugă 1 înainte de logaritmare.

    #### 2. Stabilizarea varianței (homoscedasticity)

    Modelele OLS presupun că varianța erorilor este **constantă** pe tot intervalul
    de valori prezise. Când consumul variază de la 0 la sute de kWh, erorile absolute
    tind să crească odată cu valorile — violând această presupunere (heteroscedasticity).

    Transformarea logaritmică **comprimă valorile mari** și **dilată valorile mici**,
    uniformizând varianța reziduurilor. Rezultatele testelor t și F din regresia OLS
    devin astfel mai fiabile.

    #### 3. Interpretare economică a coeficienților

    Într-un model `log(y) ~ β₀ + β₁x₁ + …`, coeficientul β₁ se interpretează ca:

    > „O creștere cu 1 unitate în x₁ este asociată cu o modificare multiplicativă
    de **e^β₁ − 1 ≈ β₁ × 100%** în consumul energetic."

    Aceasta permite formularea de politici procentuale: *„Reducerea puterii reactive
    cu 10 kVarh scade consumul activ cu X%"* — mai ușor de comunicat conducerii
    decât un efect absolut în kWh.

    #### 4. Impact asupra modelelor ML

    Algoritmi bazați pe distanță (KMeans, KNN) sunt sensibili la valori extreme.
    Log-transformarea reduce implicit influența outlierilor fără a-i elimina,
    îmbunătățind calitatea clusterizării și stabilizând gradienții în metodele
    iterative de optimizare.
    """
)
