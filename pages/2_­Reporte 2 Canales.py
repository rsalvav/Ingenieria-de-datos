import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_reservas

st.set_page_config(page_title="Reporte 2 · Canales YTD", page_icon="🧭", layout="wide")

st.title("Reporte 2: Evolución YTD de canales de distribución")
st.markdown(
    """
> La dirección comercial desea conocer cómo ha evolucionado la participación de los
> canales de distribución (Direct, Corporate, TA/TO, GDS) durante los últimos años

"""
)

df = load_reservas()

ref_mes = st.slider("Mes de referencia (corte YTD)", 1, 12, 10)
ref_dia = st.slider("Día de referencia", 1, 31, 3)

dff = df.dropna(subset=["Fecha_llegada"]).copy()
dff["mes"] = dff["Fecha_llegada"].dt.month
dff["dia"] = dff["Fecha_llegada"].dt.day

# replica el WHERE de la consulta SQL: mes < ref_mes  OR (mes = ref_mes AND dia <= ref_dia)
ytd_mask = (dff["mes"] < ref_mes) | ((dff["mes"] == ref_mes) & (dff["dia"] <= ref_dia))
ytd = dff[ytd_mask]

pivot = (
    ytd.groupby(["distribution_channel", "anio"])
    .size()
    .reset_index(name="reservas")
    .pivot(index="distribution_channel", columns="anio", values="reservas")
    .fillna(0)
    .astype(int)
)
pivot.columns = [f"YTD_{c}" for c in pivot.columns]
pivot = pivot.reset_index().rename(columns={"distribution_channel": "Canal"})

col1, col2 = st.columns([1, 1.3])
with col1:
    st.subheader("Tabla YTD por canal")
    st.dataframe(pivot, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Participación por canal y año")
    melted = pivot.melt(id_vars="Canal", var_name="Periodo", value_name="Reservas")
    fig = px.bar(
        melted, x="Periodo", y="Reservas", color="Canal", barmode="group",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)
