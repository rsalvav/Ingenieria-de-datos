import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_reservas

st.set_page_config(page_title="Reporte 4 · Cancelaciones por agencia", page_icon="🧾", layout="wide")

st.title("Reporte 4: Cancelaciones por agencia, por trimestre")
st.markdown(
    """
> Reporte 100% dinámico: si un trimestre no existe o no tiene movimiento para el año
> seleccionado, **se pinta en 0** en lugar de mostrar columnas vacías o `NULL`.
"""
)

df = load_reservas()

anio_param = st.selectbox("Año a auditar", sorted(df["anio"].dropna().unique().tolist(), reverse=True))

dff = df[(df["anio"] == anio_param) & (df["is_canceled"] == 1)].copy()

pivot = (
    dff.groupby(["agent_name", "trimestre"])
    .size()
    .reset_index(name="canceladas")
    .pivot(index="agent_name", columns="trimestre", values="canceladas")
)

# Asegura las 4 columnas Q1..Q4 siempre presentes, en 0 si no hay movimiento
for q in [1, 2, 3, 4]:
    if q not in pivot.columns:
        pivot[q] = 0
pivot = pivot[[1, 2, 3, 4]].fillna(0).astype(int)
pivot.columns = ["Q1_Canceladas", "Q2_Canceladas", "Q3_Canceladas", "Q4_Canceladas"]
pivot["TotalAño"] = pivot.sum(axis=1)
pivot = pivot.reset_index().rename(columns={"agent_name": "Agencia"})
pivot = pivot.sort_values("TotalAño", ascending=False)

top_n = st.slider("Mostrar top N agencias", 5, min(50, len(pivot)), 15)
tabla = pivot.head(top_n)

col1, col2 = st.columns([1.2, 1])
with col1:
    st.subheader(f"Tablero ejecutivo — {anio_param}")
    st.dataframe(tabla, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Top agencias por cancelaciones")
    melted = tabla.melt(
        id_vars="Agencia",
        value_vars=["Q1_Canceladas", "Q2_Canceladas", "Q3_Canceladas", "Q4_Canceladas"],
        var_name="Trimestre",
        value_name="Canceladas",
    )
    fig = px.bar(
        melted, x="Agencia", y="Canceladas", color="Trimestre", barmode="stack",
        color_discrete_sequence=px.colors.sequential.Sunset,
    )
    fig.update_layout(height=460, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
