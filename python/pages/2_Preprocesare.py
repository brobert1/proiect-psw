"""Preprocesare: valori lipsă, outlieri, codificare, scalare."""

import numpy as np
import plotly.express as px
import streamlit as st

from utils.data_loader import CATEGORICAL_COLS, NUMERIC_COLS, load_data
from utils.preprocessing import (
    iqr_outliers,
    label_encode,
    one_hot,
    scale_minmax,
    scale_standard,
    summary_missing,
    winsorize,
)

st.set_page_config(page_title="Preprocesare", page_icon="🧹", layout="wide")
st.title("🧹 Preprocesarea datelor")

df = load_data()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Valori lipsă", "Outlieri (IQR)", "Codificare", "Scalare"]
)

with tab1:
    st.subheader("Detectarea valorilor lipsă")
    missing = summary_missing(df)
    st.dataframe(missing, width="stretch")

    n_missing = missing["lipsă"].sum()
    if n_missing == 0:
        st.success("Setul nu conține valori lipsă — nu este necesară imputarea.")
    else:
        st.warning(f"{n_missing} valori lipsă. Se aplică imputare cu mediana.")
        for c in NUMERIC_COLS:
            df[c] = df[c].fillna(df[c].median())

    st.markdown(
        "**Interpretare economică:** integritatea datelor garantează că facturile "
        "de energie și raportările CO2 nu sunt subdimensionate artificial."
    )

with tab2:
    col = st.selectbox("Alege variabila pentru analiza outlierilor", NUMERIC_COLS)
    mask, (lo, hi) = iqr_outliers(df[col])
    st.metric("Outlieri detectați (IQR 1.5)", f"{mask.sum():,}")
    st.write(f"Interval acceptabil: `[{lo:.2f}, {hi:.2f}]`")

    fig = px.box(df, y=col, title=f"Boxplot {col}", points="outliers")
    st.plotly_chart(fig, width="stretch")

    clipped, n_clip = winsorize(df[col])
    st.caption(
        f"După winsorizare (clipping la limitele IQR) s-au ajustat {n_clip} valori "
        "— se elimină spike-urile cauzate probabil de porniri/opriri de agregat, "
        "care altfel ar distorsiona estimarea costurilor medii."
    )

with tab3:
    st.subheader("Label encoding")
    encoded, mappings = label_encode(df, CATEGORICAL_COLS)
    st.dataframe(encoded[[c + "_le" for c in CATEGORICAL_COLS]].head(), width="stretch")
    for k, v in mappings.items():
        st.write(f"**{k}** → {v}")

    st.subheader("One-hot encoding")
    oh, names = one_hot(df, CATEGORICAL_COLS)
    st.dataframe(oh.head(), width="stretch")
    st.caption(f"S-au generat {len(names)} coloane dummy (drop='first' pentru a evita colinearitatea).")

with tab4:
    st.subheader("Standardizare (StandardScaler)")
    z, _ = scale_standard(df, NUMERIC_COLS)
    st.dataframe(z.describe().T[["mean", "std", "min", "max"]].round(3),
                 width="stretch")

    st.subheader("Normalizare (MinMaxScaler)")
    mm, _ = scale_minmax(df, NUMERIC_COLS)
    st.dataframe(mm.describe().T[["mean", "std", "min", "max"]].round(3),
                 width="stretch")
    st.caption(
        "Scalarea este necesară pentru algoritmii bazați pe distanță (KMeans) "
        "și pentru stabilizarea coeficienților regresiei logistice."
    )
