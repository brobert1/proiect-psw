"""Helpers pentru grafice Plotly reutilizabile."""

import plotly.express as px


def time_series(df, x, y, title):
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=50, b=40))
    return fig


def bar(df, x, y, title, color=None):
    fig = px.bar(df, x=x, y=y, title=title, color=color)
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=50, b=40))
    return fig


def heatmap(df, title):
    fig = px.imshow(df, title=title, aspect="auto", color_continuous_scale="RdBu_r")
    fig.update_layout(height=500, margin=dict(l=40, r=20, t=50, b=40))
    return fig


def scatter(df, x, y, color=None, title=""):
    fig = px.scatter(df, x=x, y=y, color=color, title=title, opacity=0.6)
    fig.update_layout(height=450, margin=dict(l=40, r=20, t=50, b=40))
    return fig
