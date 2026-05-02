"""Regresie multiplă (statsmodels OLS) pe Usage_kWh."""

import numpy as np
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import streamlit as st
from statsmodels.stats.outliers_influence import variance_inflation_factor

from utils.data_loader import load_data
from utils.economics import kwh_to_eur

st.set_page_config(page_title="Regresie Multiplă", page_icon="📈", layout="wide")
st.title("📈 Regresie multiplă (statsmodels OLS) — drivers ai consumului")

df = load_data()

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

X = df_m[FEATURES]
y = df_m["Usage_kWh"]
X = sm.add_constant(X)

model = sm.OLS(y, X).fit()

st.subheader("Sumar OLS")

# ── Row 1: goodness-of-fit ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("R²",                 f"{model.rsquared:.4f}")
c2.metric("R²-ajustat",         f"{model.rsquared_adj:.4f}")
c3.metric("F-statistic",        f"{model.fvalue:,.2f}",
          help=f"Prob (F-stat): {model.f_pvalue:.2e}")
c4.metric("Prob (F-statistic)", f"{model.f_pvalue:.2e}")

# ── Row 2: information criteria & sample info ─────────────────────────────
c5, c6, c7, c8 = st.columns(4)
c5.metric("AIC",                f"{model.aic:,.2f}")
c6.metric("BIC",                f"{model.bic:,.2f}")
c7.metric("Log-Likelihood",     f"{model.llf:,.2f}")
c8.metric("Nr. observații",     f"{int(model.nobs):,}")

# ── Row 3: degrees of freedom & residual variance ─────────────────────────
c9, c10, c11, c12 = st.columns(4)
c9.metric("Grade lib. model",   f"{int(model.df_model)}")
c10.metric("Grade lib. rezid.", f"{int(model.df_resid)}")
c11.metric("MSE reziduuri",     f"{model.mse_resid:.4f}")
c12.metric("√MSE (Std. Err. of regr.)", f"{model.mse_resid ** 0.5:.4f}")

# ── Compact model-stats table ─────────────────────────────────────────────
stats_df = pd.DataFrame(
    {
        "Indicator": [
            "R²", "R²-ajustat", "F-statistic", "Prob (F-stat)",
            "Log-Likelihood", "AIC", "BIC",
            "Nr. observații", "Grade lib. model", "Grade lib. reziduuri",
            "MSE model", "MSE reziduuri",
        ],
        "Valoare": [
            f"{model.rsquared:.6f}",
            f"{model.rsquared_adj:.6f}",
            f"{model.fvalue:.4f}",
            f"{model.f_pvalue:.4e}",
            f"{model.llf:.4f}",
            f"{model.aic:.4f}",
            f"{model.bic:.4f}",
            f"{int(model.nobs)}",
            f"{int(model.df_model)}",
            f"{int(model.df_resid)}",
            f"{model.mse_model:.4f}",
            f"{model.mse_resid:.4f}",
        ],
    }
).set_index("Indicator")

with st.expander("📋 Tabel complet statistici model", expanded=False):
    st.dataframe(stats_df, use_container_width=True)

st.subheader("Coeficienți & semnificație")
coef_df = pd.DataFrame({
    "coef": model.params,
    "std_err": model.bse,
    "t": model.tvalues,
    "p_value": model.pvalues,
    "CI_2.5": model.conf_int()[0],
    "CI_97.5": model.conf_int()[1],
}).round(4)
st.dataframe(coef_df, width="stretch")

st.subheader("Variance Inflation Factor (multicolinearitate)")
vif = pd.DataFrame({
    "feature": X.columns,
    "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
}).round(2)
st.dataframe(vif, width="stretch")
st.caption("VIF > 10 indică multicolinearitate problematică.")

st.subheader("Diagnostic reziduuri")
resid = model.resid
fitted = model.fittedvalues
sample_idx = np.random.default_rng(0).choice(len(resid), size=min(3000, len(resid)),
                                              replace=False)
plot_df = pd.DataFrame({"fitted": fitted.iloc[sample_idx],
                        "rezidual": resid.iloc[sample_idx]})
fig = px.scatter(plot_df, x="fitted", y="rezidual", opacity=0.4,
                 title="Reziduuri vs valori prezise")
fig.add_hline(y=0, line_dash="dash")
st.plotly_chart(fig, width="stretch")

fig2 = px.histogram(resid, nbins=80, title="Distribuția reziduurilor")
st.plotly_chart(fig2, width="stretch")

st.subheader("Traducere economică a coeficienților")
econ = coef_df.copy()
econ["impact_eur_per_unitate"] = kwh_to_eur(econ["coef"]).round(4)
st.dataframe(econ[["coef", "p_value", "impact_eur_per_unitate"]], width="stretch")

st.markdown(
    f"""
    **Interpretare:** R² = {model.rsquared:.3f}, R²-ajustat = {model.rsquared_adj:.3f}.
    Modelul explică cea mai mare parte din variația consumului activ cu ajutorul
    puterii reactive și al factorilor de putere. Fiecare coeficient spune, în
    **EUR / unitate tehnică**, cât costă o unitate suplimentară din variabila
    respectivă — ceea ce transformă modelul într-un instrument de evaluare a
    investițiilor (ex. cât economisesc cu 0.01 ameliorare la `Lagging_PF`?).
    """
)
