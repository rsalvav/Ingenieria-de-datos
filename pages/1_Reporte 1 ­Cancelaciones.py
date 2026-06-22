import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_reservas

st.set_page_config(page_title="Reporte 1 · Cancelaciones mensuales", page_icon="📉", layout="wide")

st.title("Reporte 1: Variación absoluta de cancelaciones mes a mes")
st.markdown(
    """
> **Contexto:** Tras detectar un ciberataque simulado o caídas en la pasarela de pagos,
> Control de Riesgos necesita evaluar si las cancelaciones se dispararon de un período a
> otro, usando análisis de series temporales con funciones de ventana, para identificar
> picos de abandono masivo.
"""
)

df = load_reservas()

hoteles = sorted(df["hotel"].dropna().unique().tolist())
f_hotel = st.multiselect("Hotel", hoteles, default=hoteles)
dff = df[df["hotel"].isin(f_hotel)]

mensual = (
    dff.dropna(subset=["Fecha_llegada"])
    .assign(anio=lambda d: d["Fecha_llegada"].dt.year, mes=lambda d: d["Fecha_llegada"].dt.month)
    .groupby(["hotel", "anio", "mes"])["is_canceled"]
    .sum()
    .reset_index()
    .rename(columns={"is_canceled": "total_cancelaciones"})
    .sort_values(["anio", "mes"])
)

# equivalente a LAG(...) OVER (ORDER BY anio, mes)
mensual["cancelaciones_mes_anterior"] = mensual["total_cancelaciones"].shift(1).fillna(0).astype(int)
mensual["variacion_absoluta"] = mensual["total_cancelaciones"] - mensual["cancelaciones_mes_anterior"]
mensual["periodo"] = mensual["anio"].astype(str) + "-" + mensual["mes"].astype(str).str.zfill(2)

col1, col2 = st.columns([2, 1])
with col1:
    fig = px.bar(
        mensual,
        x="periodo",
        y="variacion_absoluta",
        color="variacion_absoluta",
        color_continuous_scale="RdYlGn_r",
        labels={"periodo": "Periodo (Año-Mes)", "variacion_absoluta": "Variación absoluta"},
    )
    fig.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pico = mensual.loc[mensual["variacion_absoluta"].idxmax()]
    caida = mensual.loc[mensual["variacion_absoluta"].idxmin()]
    st.metric("📈 Mayor pico de abandono", pico["periodo"], f"+{int(pico['variacion_absoluta'])}")
    st.metric("📉 Mayor caída", caida["periodo"], f"{int(caida['variacion_absoluta'])}")
    st.metric("Promedio cancelaciones/mes", f"{mensual['total_cancelaciones'].mean():.0f}")

st.subheader("Detalle (equivalente a la consulta SQL con LAG / OVER)")
st.dataframe(
    mensual.rename(
        columns={
            "anio": "Anio",
            "mes": "Mes",
            "total_cancelaciones": "Total_Cancelaciones",
            "cancelaciones_mes_anterior": "Cancelaciones_Mes_Anterior",
            "variacion_absoluta": "Variacion_Absoluta",
        }
    )[["Anio", "Mes", "Total_Cancelaciones", "Cancelaciones_Mes_Anterior", "Variacion_Absoluta"]],
    use_container_width=True,
    hide_index=True,
)
