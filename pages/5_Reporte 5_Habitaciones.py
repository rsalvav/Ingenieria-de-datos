import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_reservas

st.set_page_config(page_title="Reporte 5 · Inventario de habitaciones", page_icon="🛏️", layout="wide")

st.title("Reporte 5: Cancelaciones por tipo de habitación, por trimestre")
st.markdown(
    """
> Control absoluto e interactivo sobre el inventario de habitaciones: comportamiento
> de cada categoría de cuarto a lo largo del año (nombre comercial, no código técnico),
> con celdas en **0** cuando no hay registros — nunca `NULL`.
"""
)

df = load_reservas()

anio_param = st.selectbox("Año a auditar", sorted(df["anio"].dropna().unique().tolist(), reverse=True), key="anio25")
status_param = st.selectbox("Estado a evaluar", ["Canceled", "Check-Out", "No-Show"], index=0)

dff = df[(df["anio"] == anio_param) & (df["reservation_status"] == status_param)].copy()

pivot = (
    dff.groupby(["descripcion_habitacion", "trimestre"])
    .size()
    .reset_index(name="conteo")
    .pivot(index="descripcion_habitacion", columns="trimestre", values="conteo")
)

for q in [1, 2, 3, 4]:
    if q not in pivot.columns:
        pivot[q] = 0
pivot = pivot[[1, 2, 3, 4]].fillna(0).astype(int)
pivot.columns = ["Q1", "Q2", "Q3", "Q4"]
pivot["Total_Año"] = pivot.sum(axis=1)
pivot = pivot.reset_index().rename(columns={"descripcion_habitacion": "TipoHabitacion"})
pivot = pivot.sort_values("Total_Año", ascending=False)

col1, col2 = st.columns([1, 1.2])
with col1:
    st.subheader(f"Tablero de inventario — {anio_param}")
    st.dataframe(pivot, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Distribución trimestral por categoría")
    melted = pivot.melt(id_vars="TipoHabitacion", value_vars=["Q1", "Q2", "Q3", "Q4"], var_name="Trimestre", value_name="Conteo")
    fig = px.bar(
        melted, x="TipoHabitacion", y="Conteo", color="Trimestre", barmode="group",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(height=460, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

