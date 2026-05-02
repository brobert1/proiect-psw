"""Diagnostice statistice OLS — R², AIC, BIC, selecție dinamică de features."""

import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st
from plotly.subplots import make_subplots

from utils.data_loader import NUMERIC_COLS, load_data

st.set_page_config(page_title="Diagnostice Model", page_icon="🔬", layout="wide")
st.title("🔬 Diagnostice statistice — calitatea modelului OLS")

df = load_data()

# ── Feature definitions ────────────────────────────────────────────────────
df_m = df.copy()
df_m["is_weekend"] = (df_m["WeekStatus"] == "Weekend").astype(int)
df_m["hour_sq"]    = df_m["hour"] ** 2  # non-linear time effect

ALL_FEATURES = {
    "Lagging_Reactive_kVarh": "Putere reactivă lagging (kVarh)",
    "Leading_Reactive_kVarh": "Putere reactivă leading (kVarh)",
    "Lagging_PF":             "Factor putere lagging",
    "Leading_PF":             "Factor putere leading",
    "NSM":                    "Secunde de la miezul nopții (NSM)",
    "is_weekend":             "Indicator weekend (0/1)",
    "hour":                   "Ora zilei (0–23)",
    "hour_sq":                "Ora zilei — pătrat (non-liniar)",
    "CO2_tCO2":               "Emisii CO₂ (tCO₂)",
}

# ── Sidebar: feature selector ─────────────────────────────────────────────
st.sidebar.header("⚙️ Selecție variabile independente")
selected = st.sidebar.multiselect(
    "Alege variabilele de intrare:",
    options=list(ALL_FEATURES.keys()),
    default=[
        "Lagging_Reactive_kVarh",
        "Leading_Reactive_kVarh",
        "Lagging_PF",
        "Leading_PF",
        "NSM",
        "is_weekend",
    ],
    format_func=lambda k: ALL_FEATURES[k],
)

target_col = "Usage_kWh"

if len(selected) == 0:
    st.warning("⚠️ Selectează cel puțin o variabilă independentă din bara laterală.")
    st.stop()

# ── Fit model ─────────────────────────────────────────────────────────────
X = sm.add_constant(df_m[selected])
y = df_m[target_col]
model = sm.OLS(y, X).fit()

# ── Section 1: Summary metrics ────────────────────────────────────────────
st.subheader("Indicatori globali de calitate ai modelului")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("R²",            f"{model.rsquared:.4f}")
c2.metric("R²-ajustat",    f"{model.rsquared_adj:.4f}")
c3.metric("AIC",           f"{model.aic:,.2f}")
c4.metric("BIC",           f"{model.bic:,.2f}")
c5.metric("F-statistic",   f"{model.fvalue:,.2f}",
          help=f"p-val F: {model.f_pvalue:.2e}")

st.divider()

# ── Section 2: Coefficient table ──────────────────────────────────────────
st.subheader("Coeficienți, erori standard și semnificație statistică")

coef_df = pd.DataFrame({
    "Variabilă":    model.params.index,
    "Coeficient":   model.params.values,
    "Std. Err.":    model.bse.values,
    "t-statistic":  model.tvalues.values,
    "p-value":      model.pvalues.values,
    "IC 2.5%":      model.conf_int()[0].values,
    "IC 97.5%":     model.conf_int()[1].values,
}).set_index("Variabilă").round(4)

# Colour-code p-values
def style_pvalue(val):
    if val < 0.01:
        return "background-color: #d4edda; color: #155724"
    elif val < 0.05:
        return "background-color: #fff3cd; color: #856404"
    else:
        return "background-color: #f8d7da; color: #721c24"

st.dataframe(
    coef_df.style.applymap(style_pvalue, subset=["p-value"]),
    use_container_width=True,
)
st.caption(
    "🟢 p < 0.01 — foarte semnificativ | 🟡 p < 0.05 — semnificativ | 🔴 p ≥ 0.05 — nesemnificativ"
)

# ── Section 3: Coefficient plot ───────────────────────────────────────────
st.subheader("Vizualizarea coeficienților cu intervale de încredere 95%")

coef_plot = coef_df.drop("const", errors="ignore").reset_index()
fig_coef = go.Figure()
fig_coef.add_trace(
    go.Scatter(
        x=coef_plot["Coeficient"],
        y=coef_plot["Variabilă"],
        mode="markers",
        marker=dict(size=10, color="#636EFA"),
        error_x=dict(
            type="data",
            symmetric=False,
            array=(coef_plot["IC 97.5%"] - coef_plot["Coeficient"]).values,
            arrayminus=(coef_plot["Coeficient"] - coef_plot["IC 2.5%"]).values,
            color="#636EFA",
        ),
        name="Coeficient ± IC95%",
    )
)
fig_coef.add_vline(x=0, line_dash="dash", line_color="gray")
fig_coef.update_layout(
    title="Coeficienți OLS cu intervale de încredere 95%",
    xaxis_title="Valoare coeficient",
    yaxis_title="",
    height=350 + len(selected) * 15,
)
st.plotly_chart(fig_coef, use_container_width=True)

st.divider()

# ── Section 4: Model comparison across feature subsets ────────────────────
st.subheader("Compararea modelelor — AIC / BIC pentru subseturi de variabile")
st.caption(
    "Se compară modelele construite cu 1, 2, 3, … variabile (adăugate cumulativ "
    "în ordinea selectată) pentru a vedea câștigul marginal al fiecărei variabile."
)

comparison_rows = []
for k in range(1, len(selected) + 1):
    sub_feats = selected[:k]
    Xk = sm.add_constant(df_m[sub_feats])
    mk = sm.OLS(y, Xk).fit()
    comparison_rows.append({
        "Variabile incluse": " + ".join(sub_feats),
        "k": k,
        "R²":         round(mk.rsquared, 4),
        "R²-ajustat": round(mk.rsquared_adj, 4),
        "AIC":        round(mk.aic, 2),
        "BIC":        round(mk.bic, 2),
    })

comp_df = pd.DataFrame(comparison_rows).set_index("k")
st.dataframe(comp_df, use_container_width=True)

fig_cmp = make_subplots(
    rows=1, cols=2,
    subplot_titles=("AIC vs. număr variabile", "BIC vs. număr variabile"),
)
x_vals = comp_df.index.tolist()
fig_cmp.add_trace(
    go.Scatter(x=x_vals, y=comp_df["AIC"], mode="lines+markers",
               marker_color="#636EFA", name="AIC"),
    row=1, col=1,
)
fig_cmp.add_trace(
    go.Scatter(x=x_vals, y=comp_df["BIC"], mode="lines+markers",
               marker_color="#EF553B", name="BIC"),
    row=1, col=2,
)
fig_cmp.update_xaxes(title_text="Număr variabile")
fig_cmp.update_yaxes(title_text="Valoare criteriu", row=1, col=1)
fig_cmp.update_layout(height=380, showlegend=False)
st.plotly_chart(fig_cmp, use_container_width=True)

# ── Section 5: Full OLS summary text ─────────────────────────────────────
with st.expander("📄 Sumar complet OLS (statsmodels)", expanded=False):
    st.text(model.summary().as_text())

st.divider()

# ── Section 6: Explanation ────────────────────────────────────────────────
st.subheader("📖 Ce măsoară AIC și BIC — ghid de interpretare")

st.markdown(
    """
    #### R² și R²-ajustat

    **R²** (*coeficientul de determinare*) măsoară proporția din varianța variabilei
    dependente explicată de model: `R² = 1 − RSS/TSS`.

    - R² = 1 → predicție perfectă; R² = 0 → modelul nu e mai bun decât media.
    - **Problemă:** R² crește *întotdeauna* când adaugi o variabilă nouă, chiar dacă
      aceasta nu are putere explicativă reală.

    **R²-ajustat** penalizează pentru numărul de predictori:
    `R²_adj = 1 − (1−R²)(n−1)/(n−p−1)`.
    Dacă o variabilă nouă nu aduce suficientă explicație, R²-ajustat *scade*.

    ---

    #### AIC — Criteriul de Informație Akaike

    ```
    AIC = 2k − 2 ln(L̂)
    ```

    unde `k` = numărul de parametri estimați, `L̂` = valoarea maximă a funcției de
    verosimilitate.

    - **Interpretare:** AIC penalizează complexitatea (numărul de parametri) și
      recompensează ajustarea datelor (log-likelihood). Modelul cu **AIC minim**
      este preferat.
    - AIC nu are un prag absolut — are sens doar în *comparație* între modele
      pe **același set de date**.
    - AIC este optim asimptotic pentru **predicție** (generalizare pe date noi).

    ---

    #### BIC — Criteriul Informației Bayesiene (Schwarz)

    ```
    BIC = k·ln(n) − 2 ln(L̂)
    ```

    - BIC penalizează mai sever complexitatea decât AIC (factorul `ln(n)` vs. `2`),
      favorizând modele mai **parcimonioase** (cu mai puține variabile).
    - BIC este consistent: pe seturi de date mari, selectează modelul *adevărat*
      dacă acesta se află în setul candidat.
    - BIC este preferat când scopul este **inferența** (înțelegerea structurii),
      nu predicția.

    ---

    #### Cum se compară modelele

    | Situație | Acțiune recomandată |
    |---|---|
    | AIC scade la adăugarea unei variabile | Include variabila — îmbunătățește predicția |
    | BIC crește la adăugarea unei variabile | Renunță — complexitate prea mare pentru gain |
    | AIC ↓ dar BIC ↑ | Variabila ajută predicția dar nu e structural necesară |
    | Ambele scad | Include variabila — contribuție clară |

    > **Regulă practică:** diferență AIC/BIC > 10 între două modele indică suport
    > **substanțial** în favoarea modelului cu valoarea mai mică.
    """
)
