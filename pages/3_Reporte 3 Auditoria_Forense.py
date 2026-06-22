import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

from utils.data_loader import load_reservas

st.set_page_config(page_title=" Reporte 3 · Auditoría forense", page_icon="🕵️", layout="wide")

st.title("Reporte 3: Auditoría forense del primer trimestre 2017")
st.markdown(
    """
> Un fondo de inversión hotelero audita el rendimiento del turismo internacional tras
> una crisis económica menor a inicios de 2017. Corte de análisis: **10 de marzo de
> 2017**. El simulador permite ver qué hubiera pasado si el país hubiese modificado sus
> tarifas en el primer trimestre en un % dado.
"""
)

df = load_reservas()

col_a, col_b = st.columns(2)
with col_a:
    fecha_corte = st.date_input("Fecha de corte", datetime.date(2017, 3, 10))
with col_b:
    pct_simulado = st.slider("Porcentaje de tarifa simulado (%)", -20.0, 20.0, 3.0, 0.5)

fecha_corte = pd.Timestamp(fecha_corte)
anio = fecha_corte.year
inicio_ytd = pd.Timestamp(year=anio, month=1, day=1)
inicio_mtd = pd.Timestamp(year=anio, month=fecha_corte.month, day=1)
quarter = (fecha_corte.month - 1) // 3 + 1
inicio_qtd = pd.Timestamp(year=anio, month=3 * (quarter - 1) + 1, day=1)

dff = df.dropna(subset=["Fecha_llegada"]).copy()

def ingreso_en_rango(data, inicio, fin, factor=1.0):
    m = (data["Fecha_llegada"] >= inicio) & (data["Fecha_llegada"] <= fin)
    sub = data.loc[m]
    return (sub["adr"] * factor * sub["noches_totales"]).sum()

resultados = []
for pais, g in dff.groupby("pais"):
    ytd = ingreso_en_rango(g, inicio_ytd, fecha_corte)
    mtd = ingreso_en_rango(g, inicio_mtd, fecha_corte)
    qtd_sim = ingreso_en_rango(g, inicio_qtd, fecha_corte, factor=1 + pct_simulado / 100)
    if ytd > 0:
        resultados.append(
            dict(Pais=pais, IngresoYTD=ytd, IngresoMTD=mtd, IngresoQTD_Simulado=qtd_sim)
        )

res = pd.DataFrame(resultados).sort_values("IngresoYTD", ascending=False).head(10)
res = res.round(2)

col1, col2 = st.columns([1, 1.2])
with col1:
    st.subheader(f"Top 10 países — ingreso al {fecha_corte.date()}")
    st.dataframe(res, use_container_width=True, hide_index=True)

with col2:
    st.subheader(f"Impacto del escenario simulado ({pct_simulado:+.1f}%)")
    melted = res.melt(id_vars="Pais", value_vars=["IngresoYTD", "IngresoQTD_Simulado"], 
                      var_name="Métrica", value_name="Ingreso")
    
    # Cambiamos orientación a 'h' (horizontal)
    fig = px.bar(
        melted, x="Ingreso", y="Pais", color="Métrica", barmode="group",
        orientation='h', # <-- Esto hace la magia
        color_discrete_sequence=["#0E4D64", "#E07A5F"],
    )
    fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)


st.caption(
    "El escenario simulado aplica el % indicado sobre el ADR únicamente dentro del "
    "trimestre de corte (QTD), para evaluar sensibilidad de ingresos ante cambios "
    "tarifarios — sin modificar los datos históricos reales."
)

