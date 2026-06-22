# Aura Travel — Dashboard de Inteligencia Hotelera (Streamlit)

Dashboard interactivo + reportes de las consultas 20, 21, 22, 23 y 25, construido
sobre el modelo de datos RESERVA + catálogos (HOTEL, PAIS, SEGMENTO, CANAL, etc.)

## Estructura del proyecto

```
aura_dashboard/
├── app.py                     # Página principal: KPIs y dashboard general
├── pages/
│   ├── 1_📉_Consulta_20_Cancelaciones.py
│   ├── 2_🧭_Consulta_21_Canales.py
│   ├── 3_🕵️_Consulta_22_Auditoria_Forense.py
│   ├── 4_🧾_Consulta_23_Agencias.py
│   └── 5_🛏️_Consulta_25_Habitaciones.py
├── utils/
│   └── data_loader.py         # Carga, limpieza y joins de todos los CSV
├── data/                      # Tus 11 archivos .csv (ya incluidos)
├── requirements.txt
└── README.md
```

Streamlit detecta automáticamente la carpeta `pages/` y crea el menú de
navegación lateral con una entrada por reporte, además de la página principal.

## Cómo correrlo en VS Code

1. **Abre la carpeta** `aura_dashboard` en VS Code (`File → Open Folder…`).

2. **Crea un entorno virtual** (recomendado) desde la terminal integrada
   (``Ctrl+` `` o `Cmd+J`):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # En Windows: .venv\Scripts\activate
   ```

3. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Corre la app:**

   ```bash
   streamlit run app.py
   ```

   Streamlit abrirá automáticamente `http://localhost:8501` en tu navegador.
   Si no se abre solo, copia esa URL manualmente.

5. **Tip de VS Code:** instala la extensión oficial *Python* (Microsoft) y,
   opcionalmente, *Even Better TOML*. Selecciona el intérprete del `.venv`
   con `Ctrl+Shift+P → Python: Select Interpreter`.

## Notas sobre los datos

- Los CSV no traen encabezado; `utils/data_loader.py` define los nombres de
  columna según el modelo entidad-relación (tabla `RESERVA` + catálogos).
- Todo el procesamiento está cacheado con `@st.cache_data`, así que la primera
  carga tarda unos segundos y las siguientes son instantáneas — si cambias
  algún CSV, usa el botón **"Rerun"** (tecla `R`) o el menú ⋮ → *Clear cache*.
- Si agregas nuevas columnas o catálogos, edita `RESERVA_COLUMNS` y la sección
  de `merge()` en `data_loader.py`.

## Cómo extender el dashboard

- **Nuevo reporte:** crea un archivo `pages/6_📊_MiReporte.py` siguiendo la
  misma estructura (importa `load_reservas`, filtra con pandas, grafica con
  Plotly). Aparecerá solo en el menú lateral.
- **Nuevos filtros globales:** agrégalos en `app.py`, dentro de la sección
  `st.sidebar`.
- **Despliegue:** puedes publicar gratis en [Streamlit Community Cloud](
  https://streamlit.io/cloud) conectando este mismo repo — no requiere
  cambios de código.
