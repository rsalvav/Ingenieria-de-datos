"""
Aura Travel - Capa de datos
---------------------------
Lee todos los CSV de /data, les pone nombres de columna correctos
(no traen encabezado) y construye un DataFrame de reservas ya
enriquecido con las descripciones de cada catálogo (hotel, país,
canal, segmento, agente, etc.)

Todo queda cacheado con st.cache_data para que la app no vuelva a
leer/parsear los CSV en cada interacción del usuario.
"""

import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _read(name, columns):
    path = os.path.join(DATA_DIR, name)
    df = pd.read_csv(
        path,
        sep=";",
        header=None,
        names=columns,
        encoding="utf-8-sig",
        na_values=["NULL", "null", ""],
    )
    return df


@st.cache_data(show_spinner="Cargando catálogos...")
def load_catalogs():
    hotel = _read("HOTEL.csv", ["ID_hotel", "hotel"])
    pais = _read("PAIS.csv", ["ID_pais", "pais"])
    segmento = _read("SEGMENTO.csv", ["ID_segmento", "market_segment"])
    canal = _read("CANAL.csv", ["Id_canal", "distribution_channel"])
    comida = _read("COMIDA.csv", ["meal", "meal_plan"])
    deposito = _read("TIPO_DEPOSITO.csv", ["Id_Deposito", "deposit_type"])
    agente = _read("AGENTE.csv", ["agent", "agent_name"])
    compania = _read("COMPANIA.csv", ["company", "company_name"])
    tipo_cliente = _read("TIPO_CLIENTE.csv", ["ID_customer", "customer_type"])
    habitacion = _read("HABITACION.csv", ["tipo_habitacion", "descripcion"])

    return dict(
        hotel=hotel,
        pais=pais,
        segmento=segmento,
        canal=canal,
        comida=comida,
        deposito=deposito,
        agente=agente,
        compania=compania,
        tipo_cliente=tipo_cliente,
        habitacion=habitacion,
    )


RESERVA_COLUMNS = [
    "id_reserva",
    "ID_hotel",
    "Fecha_llegada",
    "lead_time",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "meal",
    "ID_pais",
    "ID_segmento",
    "Id_canal",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "reserved_room_type",
    "assigned_room_type",
    "booking_changes",
    "Id_Deposito",
    "agent",
    "company",
    "days_in_waiting_list",
    "ID_customer",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests",
    "reservation_status",
    "reservation_status_date",
]


@st.cache_data(show_spinner="Cargando y uniendo reservas (puede tardar unos segundos)...")
def load_reservas():
    cat = load_catalogs()

    r = _read("RESERVA.csv", RESERVA_COLUMNS)

    r["Fecha_llegada"] = pd.to_datetime(r["Fecha_llegada"], errors="coerce")
    r["reservation_status_date"] = pd.to_datetime(
        r["reservation_status_date"], errors="coerce"
    )

    r["anio"] = r["Fecha_llegada"].dt.year
    r["mes"] = r["Fecha_llegada"].dt.month
    r["trimestre"] = r["Fecha_llegada"].dt.quarter
    r["nombre_mes"] = r["Fecha_llegada"].dt.strftime("%b")

    r["noches_totales"] = r["stays_in_weekend_nights"].fillna(0) + r[
        "stays_in_week_nights"
    ].fillna(0)
    r["is_canceled"] = (r["reservation_status"] == "Canceled").astype(int)
    r["ingreso"] = r["adr"].fillna(0) * r["noches_totales"]

    # joins con catálogos (left, para no perder filas con códigos huérfanos)
    r = r.merge(cat["hotel"], on="ID_hotel", how="left")
    r = r.merge(cat["pais"], on="ID_pais", how="left")
    r = r.merge(cat["segmento"], on="ID_segmento", how="left")
    r = r.merge(cat["canal"], on="Id_canal", how="left")
    r = r.merge(cat["comida"], on="meal", how="left")
    r = r.merge(cat["deposito"], on="Id_Deposito", how="left")
    r = r.merge(cat["tipo_cliente"], on="ID_customer", how="left")
    r = r.merge(
        cat["agente"], on="agent", how="left"
    )
    r = r.merge(
        cat["compania"], on="company", how="left"
    )
    r = r.merge(
        cat["habitacion"].rename(
            columns={"tipo_habitacion": "reserved_room_type", "descripcion": "descripcion_habitacion"}
        ),
        on="reserved_room_type",
        how="left",
    )

    # rellenos amigables para mostrar en UI
    r["pais"] = r["pais"].fillna("Desconocido")
    r["hotel"] = r["hotel"].fillna("Desconocido")
    r["market_segment"] = r["market_segment"].fillna("Desconocido")
    r["distribution_channel"] = r["distribution_channel"].fillna("Desconocido")
    r["agent_name"] = r["agent_name"].fillna("Sin agencia")
    r["company_name"] = r["company_name"].fillna("Sin compañía")
    r["descripcion_habitacion"] = r["descripcion_habitacion"].fillna(
        r["reserved_room_type"]
    )

    return r


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    canceladas = int(df["is_canceled"].sum())
    tasa_cancel = (canceladas / total * 100) if total else 0
    adr_prom = df.loc[df["is_canceled"] == 0, "adr"].mean() if total else 0
    ingreso_total = df.loc[df["is_canceled"] == 0, "ingreso"].sum()
    noches_prom = df["noches_totales"].mean() if total else 0
    lead_time_prom = df["lead_time"].mean() if total else 0

    return dict(
        total_reservas=total,
        canceladas=canceladas,
        tasa_cancelacion=tasa_cancel,
        adr_promedio=adr_prom if pd.notna(adr_prom) else 0,
        ingreso_total=ingreso_total,
        noches_promedio=noches_prom if pd.notna(noches_prom) else 0,
        lead_time_promedio=lead_time_prom if pd.notna(lead_time_prom) else 0,
    )
