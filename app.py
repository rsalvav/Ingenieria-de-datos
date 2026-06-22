"""
Aura Travel · Dashboard de Inteligencia Hotelera
=================================================
Punto de entrada de la app multipágina de Streamlit.

Ejecutar con:
    streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import load_reservas, kpis

st.set_page_config(
    page_title="Aura Travel · Dashboard",
    page_icon="🧭",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Estilo
# ---------------------------------------------------------------------------
PRIMARY = "#0E4D64"
ACCENT = "#E07A5F"
BG_CARD = "#1C2029"

st.markdown(
    f"""
    <style>
        .block-container {{ padding-top: 1.5rem; }}
        div[data-testid="stMetric"] {{
            background-color: {BG_CARD};
            border: 1px solid #E4DFD3;
            border-radius: 10px;
            padding: 14px 16px;
        }}
        div[data-testid="stMetricLabel"] {{ font-weight: 600; color: {PRIMARY}; }}
        h1, h2, h3 {{ color: {PRIMARY}; }}
    </style>
    """,
    unsafe_allow_html=True,
)



# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
df = load_reservas()

st.title("Aura Travel — Centro de Control Hotelero")
st.caption(
    "Benchmarking de mercado, demanda y rendimiento para hoteles, inversionistas "
    "y agencias. Datos de reservas 2015–2017."
)

# ---------------------------------------------------------------------------
# Filtros (sidebar)
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros")

hoteles = sorted(df["hotel"].dropna().unique().tolist())
anios = sorted(df["anio"].dropna().astype(int).unique().tolist())
segmentos = sorted(df["market_segment"].dropna().unique().tolist())
canales = sorted(df["distribution_channel"].dropna().unique().tolist())
paises_top = df["pais"].value_counts().head(30).index.tolist()

f_hotel = st.sidebar.multiselect("Hotel", hoteles, default=hoteles)
f_anio = st.sidebar.multiselect("Año", anios, default=anios)
f_segmento = st.sidebar.multiselect("Segmento de mercado", segmentos, default=segmentos)
f_canal = st.sidebar.multiselect("Canal de distribución", canales, default=canales)
f_pais = st.sidebar.multiselect(
    "País de origen (top 30)", paises_top, default=[]
)
f_status = st.sidebar.radio(
    "Estado de la reserva", ["Todas", "Solo canceladas", "Solo no canceladas"], index=0
)

mask = (
    df["hotel"].isin(f_hotel)
    & df["anio"].isin(f_anio)
    & df["market_segment"].isin(f_segmento)
    & df["distribution_channel"].isin(f_canal)
)
if f_pais:
    mask &= df["pais"].isin(f_pais)
if f_status == "Solo canceladas":
    mask &= df["is_canceled"] == 1
elif f_status == "Solo no canceladas":
    mask &= df["is_canceled"] == 0

dff = df.loc[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"Reservas filtradas: **{len(dff):,}** de {len(df):,}")

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
k = kpis(dff)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Reservas", f"{k['total_reservas']:,}")
c2.metric("Tasa de cancelación", f"{k['tasa_cancelacion']:.1f}%")
c3.metric("ADR promedio", f"€{k['adr_promedio']:.2f}")
c4.metric("Ingreso estimado", f"€{k['ingreso_total']:,.0f}")
c5.metric("Lead time promedio", f"{k['lead_time_promedio']:.0f} días")

st.markdown("---")

# ---------------------------------------------------------------------------
# Fila 1: evolución temporal + cancelaciones
# ---------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Evolución mensual de reservas")
    evol = (
        dff.dropna(subset=["Fecha_llegada"])
        .groupby(pd.Grouper(key="Fecha_llegada", freq="MS"))
        .agg(reservas=("id_reserva", "count"), canceladas=("is_canceled", "sum"))
        .reset_index()
    )
    fig = px.line(
        evol,
        x="Fecha_llegada",
        y=["reservas", "canceladas"],
        color_discrete_sequence=[PRIMARY, ACCENT],
        labels={"value": "Reservas", "Fecha_llegada": "Mes", "variable": ""},
    )
    fig.update_layout(legend=dict(orientation="h", y=1.1), height=380)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Estado de reservas")
    estado = dff["reservation_status"].value_counts().reset_index()
    estado.columns = ["estado", "reservas"]
    fig2 = px.pie(
        estado,
        names="estado",
        values="reservas",
        hole=0.55,
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )
    fig2.update_layout(height=380, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 2: canales / segmentos + países
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Reservas por canal de distribución")
    canal_df = dff["distribution_channel"].value_counts().reset_index()
    canal_df.columns = ["canal", "reservas"]
    fig3 = px.bar(
        canal_df.sort_values("reservas"),
        x="reservas",
        y="canal",
        orientation="h",
        color="reservas",
        color_continuous_scale="Tealgrn",
    )
    fig3.update_layout(height=350, coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Top 10 países de origen")
    pais_df = dff["pais"].value_counts().head(10).reset_index()
    pais_df.columns = ["pais", "reservas"]
    fig4 = px.bar(
        pais_df.sort_values("reservas"),
        x="reservas",
        y="pais",
        orientation="h",
        color="reservas",
        color_continuous_scale="Oranges",
    )
    fig4.update_layout(height=350, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 3: tipos de habitación + ADR por segmento
# ---------------------------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("Cancelaciones por tipo de habitación")
    hab = (
        dff.groupby("descripcion_habitacion")["is_canceled"]
        .agg(reservas="count", canceladas="sum")
        .reset_index()
    )
    hab["tasa_%"] = (hab["canceladas"] / hab["reservas"] * 100).round(1)
    fig5 = px.bar(
        hab.sort_values("reservas", ascending=False),
        x="descripcion_habitacion",
        y="reservas",
        color="tasa_%",
        color_continuous_scale="Reds",
        labels={"descripcion_habitacion": "Tipo de habitación"},
    )
    fig5.update_layout(height=350)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("ADR promedio por segmento de mercado")
    adr_seg = (
        dff[dff["is_canceled"] == 0]
        .groupby("market_segment")["adr"]
        .mean()
        .reset_index()
        .sort_values("adr", ascending=False)
    )
    fig6 = px.bar(
        adr_seg,
        x="market_segment",
        y="adr",
        color="adr",
        color_continuous_scale="Tealgrn",
        labels={"market_segment": "Segmento", "adr": "ADR (€)"},
    )
    fig6.update_layout(height=350, coloraxis_showscale=False)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(
    "👈 Usa el menú lateral para navegar a los **reportes de consultas** "
    "(análisis de cancelaciones, canales, auditoría forense, etc.)."
)
