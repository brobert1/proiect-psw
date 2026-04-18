"""Transformări reutilizabile: missing, outlieri, encoding, scaling."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    LabelEncoder,
    MinMaxScaler,
    OneHotEncoder,
    StandardScaler,
)


def summary_missing(df):
    total = df.isna().sum()
    pct = (total / len(df) * 100).round(2)
    return pd.DataFrame({"lipsă": total, "procent %": pct})


def iqr_outliers(series, k=1.5):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    mask = (series < lo) | (series > hi)
    return mask, (lo, hi)


def winsorize(series, k=1.5):
    mask, (lo, hi) = iqr_outliers(series, k)
    return series.clip(lower=lo, upper=hi), mask.sum()


def label_encode(df, cols):
    out = df.copy()
    mappings = {}
    for c in cols:
        le = LabelEncoder()
        out[c + "_le"] = le.fit_transform(out[c].astype(str))
        mappings[c] = dict(zip(le.classes_, range(len(le.classes_))))
    return out, mappings


def one_hot(df, cols):
    ohe = OneHotEncoder(sparse_output=False, drop="first")
    arr = ohe.fit_transform(df[cols].astype(str))
    names = ohe.get_feature_names_out(cols)
    return pd.DataFrame(arr, columns=names, index=df.index), list(names)


def scale_standard(df, cols):
    sc = StandardScaler()
    arr = sc.fit_transform(df[cols])
    return pd.DataFrame(arr, columns=cols, index=df.index), sc


def scale_minmax(df, cols):
    sc = MinMaxScaler()
    arr = sc.fit_transform(df[cols])
    return pd.DataFrame(arr, columns=cols, index=df.index), sc
