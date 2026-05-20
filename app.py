import streamlit as st
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error

# ---------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------

st.set_page_config(
    page_title="Proyecto EUR/USD",
    page_icon="📈",
    layout="wide"
)

st.title("Análisis Macroeconómico EUR/USD")
st.markdown("Proyecto de ingeniería de datos con DuckDB, Prefect y Streamlit")

# ---------------------------
# CONEXIÓN A DUCKDB
# ---------------------------

con = duckdb.connect("proyectolassupernenas.duckdb")

# ---------------------------
# CARGAR DATOS GOLD
# ---------------------------

df = con.execute("""
SELECT *
FROM proyectolassupernenas.gold.modelo
""").df()

pred = con.execute("""
SELECT *
FROM proyectolassupernenas.gold.predicciones
""").df()

# ---------------------------
# CARGAR DATOS YFINANCE
# ---------------------------

df_api = con.execute("""
SELECT *
FROM proyectolassupernenas.gold.eurusd_api
""").df()

st.subheader("EUR/USD desde Yahoo Finance")

st.dataframe(df_api)

# ---------------------------
# TABLA LIMPIA PARA MOSTRAR
# ---------------------------

df_mostrar = df[
    [
        "FECHA_F",
        "EURUSD_F",
        "INTERES_USA_F",
        "INTERES_EUR_F",
        "INFLACION_USA_F",
        "INFLACION_EUR_F",
        "PIB_USA_F",
        "PIB_EUR_F",
        "DIF_INTERES",
        "DIF_INFLACION",
        "DIF_PIB"
    ]
]

df_mostrar.columns = [
    "Fecha",
    "EUR/USD",
    "Interés USA",
    "Interés EUR",
    "Inflación USA",
    "Inflación EUR",
    "PIB USA",
    "PIB EUR",
    "Dif. Tasas",
    "Dif. Inflación",
    "Dif. PIB"
]

# ---------------------------
# MÉTRICAS PRINCIPALES
# ---------------------------

st.subheader("Indicadores Principales")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Promedio EUR/USD",
    round(df["EURUSD_F"].mean(), 2)
)

col2.metric(
    "Promedio Dif. Tasas",
    round(df["DIF_INTERES"].mean(), 2)
)

col3.metric(
    "Promedio Dif. Inflación",
    round(df["DIF_INFLACION"].mean(), 2)
)

# ---------------------------
# TABLA DE DATOS
# ---------------------------

st.subheader("Datos Procesados")

st.dataframe(df_mostrar, use_container_width=True)

# ---------------------------
# CALCULAR METRICAS
# ---------------------------

r2 = r2_score(
    pred["REAL"],
    pred["PREDICCION"]
)

mse = mean_squared_error(
    pred["REAL"],
    pred["PREDICCION"]
)

st.subheader("Modelo de Regresión")

col1, col2 = st.columns(2)

col1.metric(
    "R²",
    round(r2, 3)
)

col2.metric(
    "ECM",
    round(mse, 3)
)

# ---------------------------
# GRÁFICA EUR/USD
# ---------------------------

st.subheader("Evolución EUR/USD")

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(df["FECHA_F"], df["EURUSD_F"])

ax.set_title("Comportamiento del EUR/USD")
ax.set_xlabel("Fecha")
ax.set_ylabel("EUR/USD")

plt.xticks(rotation=45)

st.pyplot(fig)

# ---------------------------
# GRÁFICA REAL VS PREDICCION
# ---------------------------

st.subheader("Valores Reales vs Predicciones")

fig2, ax2 = plt.subplots(figsize=(10,5))

ax2.plot(
    pred["REAL"].values,
    label="Real"
)

ax2.plot(
    pred["PREDICCION"].values,
    label="Predicción"
)

ax2.legend()

st.pyplot(fig2)

# ---------------------------
# MATRIZ DE CORRELACIÓN
# ---------------------------

st.subheader("Correlación de Variables")

corr = df[
    [
        "EURUSD_F",
        "DIF_INTERES",
        "DIF_INFLACION",
        "DIF_PIB"
    ]
].corr()

st.dataframe(corr)

# ---------------------------
# TABLA DE METRICAS
# ---------------------------

reg = con.execute("""
SELECT *
FROM proyectolassupernenas.gold.regresion_resumen
""").df()

st.subheader("Resultados de la Regresión")

st.dataframe(reg)