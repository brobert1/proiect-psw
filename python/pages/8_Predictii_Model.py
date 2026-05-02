"""Predicții model OLS — actual vs. prezis, metrici de eroare."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from utils.data_loader import load_data
from utils.economics import kwh_to_eur

st.set_page_config(page_title="Predicții Model", page_icon="🎯", layout="wide")
st.title("🎯 Evaluarea modelului — valori actuale vs. prezise")

df = load_data()

# ── Feature engineering ────────────────────────────────────────────────────
df_m = df.copy()
df_m["is_weekend"] = (df_m["WeekStatus"] == "Weekend").astype(int)

FEATURES = [
    "Lagging_Reactive_kVarh",
    "Leading_Reactive_kVarh",
    "Lagging_PF",
    "Leading_PF",
    "NSM",
    "is_weekend",
]

X = sm.add_constant(df_m[FEATURES])
y = df_m["Usage_kWh"]

# ── Fit OLS ────────────────────────────────────────────────────────────────
model = sm.OLS(y, X).fit()
y_pred = model.fittedvalues
resid  = model.resid

# ── Metrics ────────────────────────────────────────────────────────────────
mae  = resid.abs().mean()
rmse = np.sqrt((resid ** 2).mean())
mape = (resid.abs() / y.replace(0, np.nan)).mean() * 100
r2   = model.rsquared

mae_eur  = kwh_to_eur(mae)
rmse_eur = kwh_to_eur(rmse)

# ── KPI row ────────────────────────────────────────────────────────────────
st.subheader("Metrici de performanță ale modelului")
c1, c2, c3, c4 = st.columns(4)
c1.metric("R²", f"{r2:.4f}")
c2.metric("MAE (kWh)", f"{mae:.3f}", help="Eroare medie absolută")
c3.metric("RMSE (kWh)", f"{rmse:.3f}", help="Rădăcina erorii pătratice medii")
c4.metric("MAPE (%)", f"{mape:.2f}%", help="Eroare procentuală medie absolută")

c5, c6 = st.columns(2)
c5.metric("MAE în EUR", f"{mae_eur:.4f} EUR / interval",
          help="Cost mediu al erorii de predicție per interval de 15 min")
c6.metric("RMSE în EUR", f"{rmse_eur:.4f} EUR / interval")

st.divider()

# ── Scatter: actual vs predicted ──────────────────────────────────────────
st.subheader("Valori actuale vs. valori prezise")

sample_idx = np.random.default_rng(42).choice(len(y), size=min(4000, len(y)),
                                               replace=False)
plot_df = pd.DataFrame({
    "Actual (kWh)":   y.iloc[sample_idx].values,
    "Prezis (kWh)":   y_pred.iloc[sample_idx].values,
    "Load_Type":      df_m["Load_Type"].iloc[sample_idx].values,
})

fig = px.scatter(
    plot_df, x="Actual (kWh)", y="Prezis (kWh)",
    color="Load_Type", opacity=0.45,
    title="Actual vs. Prezis — model OLS (eșantion 4 000 obs.)",
    labels={"Load_Type": "Tip sarcină"},
    color_discrete_sequence=px.colors.qualitative.Plotly,
)

# Perfect-prediction diagonal
lim_min = min(plot_df["Actual (kWh)"].min(), plot_df["Prezis (kWh)"].min())
lim_max = max(plot_df["Actual (kWh)"].max(), plot_df["Prezis (kWh)"].max())
fig.add_trace(
    go.Scatter(
        x=[lim_min, lim_max], y=[lim_min, lim_max],
        mode="lines",
        line=dict(color="black", dash="dash", width=1.5),
        name="Predicție perfectă (y = x)",
    )
)
fig.update_layout(height=500, legend_title_text="Tip sarcină")
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Punctele aflate pe diagonala neagră reprezintă predicții perfecte. "
    "Punctele **deasupra** diagonalei → modelul **supraestimează** consumul; "
    "**sub** diagonală → **subestimează**."
)

# ── Residuals vs fitted ────────────────────────────────────────────────────
st.subheader("Reziduuri vs. valori prezise (diagnostic heteroscedasticity)")

resid_df = pd.DataFrame({
    "Prezis (kWh)": y_pred.iloc[sample_idx].values,
    "Rezidual (kWh)": resid.iloc[sample_idx].values,
    "Load_Type": df_m["Load_Type"].iloc[sample_idx].values,
})

fig2 = px.scatter(
    resid_df, x="Prezis (kWh)", y="Rezidual (kWh)",
    color="Load_Type", opacity=0.4,
    title="Reziduuri vs. valori prezise",
    color_discrete_sequence=px.colors.qualitative.Plotly,
)
fig2.add_hline(y=0, line_dash="dash", line_color="black")
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# ── Residual distribution ──────────────────────────────────────────────────
st.subheader("Distribuția reziduurilor")

c1, c2 = st.columns(2)

with c1:
    fig3 = px.histogram(
        resid, nbins=100,
        title="Histogramă reziduuri",
        labels={"value": "Rezidual (kWh)", "count": "Frecvență"},
        color_discrete_sequence=["#636EFA"],
    )
    fig3.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with c2:
    # Q-Q plot approximation via sorted residuals vs normal quantiles
    sorted_resid = np.sort(resid.values)
    n = len(sorted_resid)
    theoretical_q = np.quantile(
        np.random.default_rng(0).standard_normal(100_000),
        np.linspace(0.5 / n, 1 - 0.5 / n, n),
    )
    # sample for display
    step = max(1, n // 3000)
    qq_df = pd.DataFrame({
        "Quantile teoretic (Normal)": theoretical_q[::step],
        "Quantile reziduale":         sorted_resid[::step],
    })
    fig4 = px.scatter(
        qq_df,
        x="Quantile teoretic (Normal)", y="Quantile reziduale",
        title="Q-Q plot reziduuri vs. distribuție normală",
        opacity=0.4,
        color_discrete_sequence=["#EF553B"],
    )
    # reference line
    lo, hi = theoretical_q[0], theoretical_q[-1]
    fig4.add_trace(
        go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                   line=dict(color="black", dash="dash"), name="Normală perfectă")
    )
    fig4.update_layout(height=350)
    st.plotly_chart(fig4, use_container_width=True)

# ── Error quantile table ───────────────────────────────────────────────────
st.subheader("Distribuția erorilor absolute")

abs_err = resid.abs()
quantiles = [0.50, 0.75, 0.90, 0.95, 0.99]
err_table = pd.DataFrame({
    "Percentilă": [f"P{int(q*100)}" for q in quantiles],
    "Eroare absolută (kWh)": [abs_err.quantile(q) for q in quantiles],
    "Cost eroare (EUR)":     [kwh_to_eur(abs_err.quantile(q)) for q in quantiles],
}).set_index("Percentilă")
err_table = err_table.round(4)
st.dataframe(err_table, use_container_width=True)

# ── Interpretation ────────────────────────────────────────────────────────
st.divider()
st.subheader("Interpretarea economică a erorilor de predicție")

st.markdown(
    f"""
    #### Citirea metricilor

    | Metrică | Valoare | Interpretare |
    |---|---|---|
    | **MAE** | {mae:.3f} kWh | În medie, modelul greșește cu **{mae:.3f} kWh** per interval de 15 min |
    | **RMSE** | {rmse:.3f} kWh | Penalizează mai mult erorile mari; mai sensibil la spike-uri de consum |
    | **MAPE** | {mape:.2f}% | Eroarea relativă medie față de consumul real |
    | **R²** | {r2:.4f} | Modelul explică **{r2*100:.1f}%** din variația consumului activ |

    #### Impactul economic al erorii

    - O eroare MAE de **{mae:.3f} kWh** per interval de 15 minute se traduce în
      **≈ {kwh_to_eur(mae)*24*4:.2f} EUR/zi** de incertitudine în bugetul energetic
      (dacă predicțiile sunt folosite pentru planificarea achizițiilor de energie).
    - RMSE de **{rmse:.3f} kWh** înseamnă că în situațiile cu spike-uri de sarcină
      (porniri de cuptoare, agregatele de rulare la rece), eroarea poate depăși
      semnificativ media — tocmai scenariile cu cel mai mare impact financiar.

    #### Limitele modelului OLS

    Modelul liniar capturează bine tendința medie, dar **subestimează sistematic
    perioadele de sarcină maximă** (vizibil în graficul actual vs. prezis — punctele
    `Maximum_Load` se află predominant sub diagonală la valori mari).

    Îmbunătățiri posibile:
    - **Log-transformarea** variabilei dependente (vezi pagina Log Transform);
    - Adăugarea de **interacțiuni** (ex. `hour × Lagging_PF`);
    - Modele **non-liniare** (Random Forest, Gradient Boosting) pentru a capta
      relațiile complexe dintre puterea reactivă și consumul activ.
    """
)
