# utils/chart_utils.py

import pandas as pd
import plotly.express as px

def pie_chart(df: pd.DataFrame, kategori: str):
    df_kategori = df[df["kategori"] == kategori]
    if df_kategori.empty:
        return None
    fig = px.pie(df_kategori, names="sub_kategori", values="jumlah", title=f"Distribusi {kategori}")
    return fig

def line_chart(df: pd.DataFrame):
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df_grouped = df.groupby(["tanggal", "kategori"])["jumlah"].sum().reset_index()
    fig = px.line(df_grouped, x="tanggal", y="jumlah", color="kategori", title="Tren Keuangan Harian")
    return fig

def bar_chart_bulanan(df: pd.DataFrame):
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["bulan"] = df["tanggal"].dt.to_period("M").astype(str)
    df_grouped = df.groupby(["bulan", "kategori"])["jumlah"].sum().reset_index()
    fig = px.bar(df_grouped, x="bulan", y="jumlah", color="kategori", barmode="group", title="Rekap Bulanan")
    return fig
