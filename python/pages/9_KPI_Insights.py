"""Dashboard KPI — indicatori cheie de performanță și insights automate."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data
from utils.economics import EUR_PER_KWH, RON_PER_TCO2, co2_to_ron, kwh_to_eur

st.set_page_config(page_title="KPI-urile Companiei", page_icon="📊", layout="wide")
st.title("📊 Dashboard KPI — Performanță energetică & insights de business")

df = load_data()

# ── Precompute aggregates ──────────────────────────────────────────────────
total_kwh   = df["Usage_kWh"].sum()
total_cost  = kwh_to_eur(total_kwh)
total_co2   = df["CO2_tCO2"].sum()
total_co2_ron = co2_to_ron(total_co2)
n_days      = df["day"].nunique()
avg_pf      = df["Lagging_PF"].mean()

daily_agg = df.groupby("day", as_index=False).agg(
    kwh=("Usage_kWh", "sum"),
    co2=("CO2_tCO2", "sum"),
)
daily_agg["cost_eur"] = kwh_to_eur(daily_agg["kwh"])
avg_daily_cost = daily_agg["cost_eur"].mean()
avg_daily_kwh  = daily_agg["kwh"].mean()

weekday_agg = (
    df.groupby("WeekStatus", as_index=False)["Usage_kWh"]
    .agg(total=("sum"), medie=("mean"))
)
wd_total  = weekday_agg.loc[weekday_agg["WeekStatus"] == "Weekday", "total"].values[0]
we_total  = weekday_agg.loc[weekday_agg["WeekStatus"] == "Weekend", "total"].values[0]
wd_mean   = weekday_agg.loc[weekday_agg["WeekStatus"] == "Weekday", "medie"].values[0]
we_mean   = weekday_agg.loc[weekday_agg["WeekStatus"] == "Weekend", "medie"].values[0]

# ── Section 1: Top-level KPIs ─────────────────────────────────────────────
st.subheader("Indicatori cheie — întreg anul 2018")

c1, c2, c3, c4 = st.columns(4)
c1.metric("⚡ Consum total", f"{total_kwh:,.0f} kWh")
c2.metric("💶 Cost energie estimat", f"{total_cost:,.0f} EUR",
          help=f"Tarif industrial: {EUR_PER_KWH} EUR/kWh")
c3.metric("🌿 Emisii CO₂", f"{total_co2:,.2f} t",
          help="Suma coloanei CO2(tCO2) din dataset")
c4.metric("💵 Cost ecologic CO₂", f"{total_co2_ron:,.0f} RON",
          help=f"Taxă carbon: {RON_PER_TCO2} RON/tCO₂")

c5, c6, c7, c8 = st.columns(4)
c5.metric("📅 Cost mediu zilnic", f"{avg_daily_cost:,.2f} EUR/zi")
c6.metric("📅 Consum mediu zilnic", f"{avg_daily_kwh:,.1f} kWh/zi")
c7.metric("🔌 Factor putere mediu", f"{avg_pf:.2f}")
c8.metric("🗓 Zile monitorizate", f"{n_days}")

st.divider()

# ── Section 2: Weekday vs Weekend ─────────────────────────────────────────
st.subheader("Consum zilele lucrătoare vs. weekend")

c1, c2 = st.columns(2)

with c1:
    diff_pct = (wd_mean - we_mean) / we_mean * 100
    c1a, c1b = st.columns(2)
    c1a.metric("Medie interval 15 min — Zi lucrătoare",
               f"{wd_mean:.2f} kWh",
               delta=f"+{diff_pct:.1f}% față de weekend",
               delta_color="inverse")
    c1b.metric("Medie interval 15 min — Weekend",
               f"{we_mean:.2f} kWh")

    comp_df = pd.DataFrame({
        "Statut": ["Zi lucrătoare", "Weekend"],
        "kWh total": [wd_total, we_total],
        "Cost EUR": [kwh_to_eur(wd_total), kwh_to_eur(we_total)],
    })
    st.dataframe(comp_df.set_index("Statut").round(0), use_container_width=True)

with c2:
    fig_pie = go.Figure(
        go.Pie(
            labels=["Zile lucrătoare", "Weekend"],
            values=[wd_total, we_total],
            hole=0.45,
            marker_colors=["#636EFA", "#EF553B"],
            textinfo="label+percent",
        )
    )
    fig_pie.update_layout(
        title="Distribuția consumului total: lucrătoare vs. weekend",
        height=320,
        showlegend=False,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Hourly profile: weekday vs weekend ────────────────────────────────────
hourly = df.groupby(["WeekStatus", "hour"], as_index=False)["Usage_kWh"].mean()
fig_hour = px.line(
    hourly, x="hour", y="Usage_kWh", color="WeekStatus",
    markers=True,
    title="Profil orar mediu: zi lucrătoare vs. weekend",
    labels={"hour": "Ora", "Usage_kWh": "Consum mediu (kWh)", "WeekStatus": "Statut"},
    color_discrete_map={"Weekday": "#636EFA", "Weekend": "#EF553B"},
)
fig_hour.update_layout(height=360)
st.plotly_chart(fig_hour, use_container_width=True)

st.divider()

# ── Section 3: Top 5 highest consumption days ─────────────────────────────
st.subheader("Top 5 zile cu cel mai mare consum energetic")

top5 = daily_agg.nlargest(5, "kwh").reset_index(drop=True)
top5.index = top5.index + 1
top5["cost_eur"]  = top5["cost_eur"].round(2)
top5["kwh"]       = top5["kwh"].round(1)
top5["co2"]       = top5["co2"].round(3)
top5 = top5.rename(columns={
    "day":      "Data",
    "kwh":      "Consum (kWh)",
    "co2":      "CO₂ (t)",
    "cost_eur": "Cost estimat (EUR)",
})
st.dataframe(top5[["Data", "Consum (kWh)", "CO₂ (t)", "Cost estimat (EUR)"]],
             use_container_width=True)

fig_top5 = px.bar(
    top5, x="Data", y="Consum (kWh)",
    text="Cost estimat (EUR)",
    color="Consum (kWh)",
    color_continuous_scale="Oranges",
    title="Top 5 zile cu consum maxim",
)
fig_top5.update_traces(texttemplate="%{text:.0f} EUR", textposition="outside")
fig_top5.update_layout(height=380, coloraxis_showscale=False)
st.plotly_chart(fig_top5, use_container_width=True)

# ── Monthly trend ──────────────────────────────────────────────────────────
st.subheader("Consum total și cost pe lună")

monthly = df.groupby("month", as_index=False).agg(
    kwh=("Usage_kWh", "sum"),
    co2=("CO2_tCO2", "sum"),
)
monthly["cost_eur"] = kwh_to_eur(monthly["kwh"]).round(0)
month_labels = {
    1: "Ian", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mai", 6: "Iun",
    7: "Iul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Noi", 12: "Dec",
}
monthly["luna"] = monthly["month"].map(month_labels)

fig_month = px.bar(
    monthly, x="luna", y="kwh",
    color="kwh",
    color_continuous_scale="Blues",
    text="cost_eur",
    title="Consum lunar total (kWh) cu cost estimat (EUR)",
    labels={"luna": "Luna", "kwh": "Consum (kWh)"},
)
fig_month.update_traces(texttemplate="%{text:,.0f} EUR", textposition="outside")
fig_month.update_layout(height=400, coloraxis_showscale=False)
st.plotly_chart(fig_month, use_container_width=True)

st.divider()

# ── Section 4: Auto-computed Key Insights ─────────────────────────────────
st.subheader("💡 Concluzii cheie — generate automat")

peak_month_idx = monthly["kwh"].idxmax()
peak_month     = monthly.loc[peak_month_idx, "luna"]
peak_month_kwh = monthly.loc[peak_month_idx, "kwh"]
peak_month_eur = monthly.loc[peak_month_idx, "cost_eur"]

low_month_idx  = monthly["kwh"].idxmin()
low_month      = monthly.loc[low_month_idx, "luna"]
low_month_kwh  = monthly.loc[low_month_idx, "kwh"]

top1 = top5.iloc[0]

high_load_pct = (df["Load_Type"] == "Maximum_Load").mean() * 100
med_load_pct  = (df["Load_Type"] == "Medium_Load").mean() * 100

reactive_corr = df["Lagging_Reactive_kVarh"].corr(df["Usage_kWh"])

weekend_saving = kwh_to_eur(wd_mean - we_mean) * 4 * 365 / 7 * 2

st.markdown(
    f"""
    - 🔴 **Luna cu consum maxim este {peak_month}**, cu **{peak_month_kwh:,.0f} kWh** consumați
      și un cost estimat de **{peak_month_eur:,.0f} EUR** — reprezentând
      {peak_month_kwh / total_kwh * 100:.1f}% din consumul anual total.
      Aceste luni justifică negocierea anticipată a energiei pe piața day-ahead.

    - 🟢 **Luna cu consum minim este {low_month}** ({low_month_kwh:,.0f} kWh) —
      o oportunitate pentru planificarea lucrărilor de mentenanță majore fără
      impact semnificativ asupra producției.

    - ⚡ **Intervalele de sarcină maximă** reprezintă **{high_load_pct:.1f}%** din
      totalul observațiilor, dar generează o parte disproporționat de mare a
      costurilor la tariful de vârf. Reducerea duratei acestor intervale prin
      *peak-shaving* poate reduce factura energetică fără a afecta producția.

    - 📉 **Puterea reactivă lagging** are o corelație Pearson de **{reactive_corr:.3f}**
      cu consumul activ — una dintre cele mai mari corelații din dataset.
      Compensarea capacitivă (baterii de condensatori) este cea mai rapidă pârghie
      de reducere a costului energetic și a penalizărilor pentru factor de putere scăzut.

    - 🗓 **Zilele lucrătoare consumă în medie cu {diff_pct:.1f}% mai mult** per interval
      față de weekend. Redistribuirea operațiunilor non-critice spre weekend poate
      genera economii estimate la **{weekend_saving:,.0f} EUR/an** la tariful curent.
    """
)
