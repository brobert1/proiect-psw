"""Regresie logistică — predicția intervalelor de sarcină maximă."""

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from utils.data_loader import load_data

st.set_page_config(page_title="Regresie Logistică", page_icon="🎯", layout="wide")
st.title("🎯 Regresie logistică — detecția regimurilor de sarcină maximă")

df = load_data()
df["High_Load"] = (df["Load_Type"] == "Maximum_Load").astype(int)

FEATURES = [
    "Lagging_Reactive_kVarh",
    "Leading_Reactive_kVarh",
    "Lagging_PF",
    "Leading_PF",
    "NSM",
    "hour",
    "weekday_num",
]

X = df[FEATURES].values
y = df["High_Load"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

model = LogisticRegression(max_iter=500, class_weight="balanced")
model.fit(X_train_s, y_train)
proba = model.predict_proba(X_test_s)[:, 1]
y_pred = model.predict(X_test_s)

c1, c2, c3 = st.columns(3)
c1.metric("Prevalență sarcină maximă", f"{y.mean():.1%}")
c2.metric("Acuratețe test", f"{(y_pred == y_test).mean():.3f}")
c3.metric("ROC-AUC", f"{roc_auc_score(y_test, proba):.3f}")

st.subheader("Matricea de confuzie")
cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(cm, index=["Real: Non-Max", "Real: Max"],
                     columns=["Pred: Non-Max", "Pred: Max"])
st.dataframe(cm_df, width="stretch")

st.subheader("Raport de clasificare")
report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
st.dataframe(pd.DataFrame(report).T.round(3), width="stretch")

st.subheader("Curba ROC")
fpr, tpr, _ = roc_curve(y_test, proba)
roc_df = pd.DataFrame({"FPR": fpr, "TPR": tpr})
fig = px.line(roc_df, x="FPR", y="TPR",
              title=f"ROC (AUC = {roc_auc_score(y_test, proba):.3f})")
fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line=dict(dash="dash"))
st.plotly_chart(fig, width="stretch")

st.subheader("Coeficienți — impact per variabilă")
coef_df = pd.DataFrame({
    "feature": FEATURES,
    "coef": model.coef_[0],
    "odds_ratio": np.exp(model.coef_[0]),
}).sort_values("coef", key=abs, ascending=False)
st.dataframe(coef_df.round(4), width="stretch")

st.markdown(
    """
    **Interpretare economică:** un model care prezice corect perioadele de
    sarcină maximă permite:
    - *peak-shaving* — redistribuirea operațiunilor non-critice în afara vârfurilor,
      cu economii directe la tariful pe oră de vârf;
    - achiziția anticipată pe piața energiei (intra-day / day-ahead) la preț mai bun;
    - **coeficienții** arată că puterea reactivă și ora zilei sunt driverii dominanți —
      investiția în baterii de condensatori și planificarea schimburilor sunt
      pârghiile operaționale concrete.
    """
)
