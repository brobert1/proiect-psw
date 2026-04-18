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
st.text(model.summary().as_text())

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
