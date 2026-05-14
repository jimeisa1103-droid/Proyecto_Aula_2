import pandas as pd
import duckdb
from prefect import flow, task

datos = pd.read_excel(r"/workspaces/Proyecto_Aula_2/DATOS PROYECTO (1).xlsx")
datos = datos
datos = datos.astype(str)
datos.columns = [i.replace("/", "").replace("Ó", "O").replace("É", "E").replace(" ","_") for i in datos.columns]

datos.info()
datos.describe()

[i.replace("/", "").replace("Ó", "O").replace("É", "E").replace(" ","_") for i in datos.columns]

@task
def cargar_datos():

    df = pd.read_excel("/workspaces/Proyecto_Aula_2/DATOS PROYECTO (1).xlsx")

    df.columns = [
        'FECHA',
        'EURUSD',
        'INTERES_USA',
        'INTERES_EUR',
        'INFLACION_USA',
        'INFLACION_EUR',
        'PIB_USA',
        'PIB_EUR'
    ]

    return df

@task
def crear_esquemas():

    con = duckdb.connect("proyectolassupernenas.duckdb")

    con.execute("CREATE SCHEMA IF NOT EXISTS proyectolassupernenas.bronze")
    con.execute("CREATE SCHEMA IF NOT EXISTS proyectolassupernenas.silver")
    con.execute("CREATE SCHEMA IF NOT EXISTS proyectolassupernenas.gold")

@task
def bronze(df):

    con = duckdb.connect("proyectolassupernenas.duckdb")

    con.execute("""
    CREATE OR REPLACE TABLE proyectolassupernenas.bronze.precios AS
    SELECT * FROM df
    """)

@task
def silver():

    con = duckdb.connect("/workspaces/Proyecto_Aula_2/proyectolassupernenas.duckdb")

    con.execute("""
    CREATE OR REPLACE TABLE proyectolassupernenas.silver.precios AS
    SELECT
    *,
    CAST(EURUSD AS FLOAT) AS EURUSD_F,
    CAST(INTERES_USA AS FLOAT) AS INTERES_USA_F,
    CAST(INTERES_EUR AS FLOAT) AS INTERES_EUR_F,
    CAST(INFLACION_USA AS FLOAT) AS INFLACION_USA_F,
    CAST(INFLACION_EUR AS FLOAT) AS INFLACION_EUR_F,
    CAST(PIB_USA AS FLOAT) AS PIB_USA_F,
    CAST(PIB_EUR AS FLOAT) AS PIB_EUR_F,
    CAST(FECHA AS DATE) AS FECHA_F
FROM proyectolassupernenas.bronze.precios
""")
    
@task
def gold():

    con = duckdb.connect("/workspaces/Proyecto_Aula_2/proyectolassupernenas.duckdb")

    con.execute("""
    CREATE OR REPLACE TABLE proyectolassupernenas.gold.modelo AS
    SELECT
    *,

    (INTERES_USA_F - INTERES_EUR_F) AS DIF_INTERES,

    (INFLACION_USA_F - INFLACION_EUR_F) AS DIF_INFLACION,

    (PIB_USA_F - PIB_EUR_F) AS DIF_PIB

FROM proyectolassupernenas.silver.precios
""")
    
@task
def analisis():

    con = duckdb.connect("/workspaces/Proyecto_Aula_2/proyectolassupernenas.duckdb")

    df = con.execute("""
    SELECT * FROM proyectolassupernenas.gold.modelo
    """).df()

    print(df.describe())

@task
def visualizacion():

    import matplotlib.pyplot as plt

    con = duckdb.connect("/workspaces/Proyecto_Aula_2/proyectolassupernenas.duckdb")

    df = con.execute("""
    SELECT * FROM proyectolassupernenas.gold.modelo
    """).df()

    plt.figure(figsize=(10,5))
    plt.plot(df["FECHA_F"], df["EURUSD_F"])
    plt.title("Comportamiento EUR/USD")
    plt.xticks(rotation=45)
    plt.show()

@flow
def flujo_de_tareas():

    crear_esquemas()

    df = cargar_datos()

    bronze(df)

    silver()

    gold()

    analisis()

    visualizacion()

flujo_de_tareas()

#Hasta aquí va el codigo bien de las capas y el prefect

import duckdb

con = duckdb.connect("/workspaces/Proyecto_Aula_2/proyectolassupernenas.duckdb")

df = con.execute("""
SELECT * 
FROM proyectolassupernenas.gold.modelo
""").df()

df.head()

df[['EURUSD_F','DIF_INTERES','DIF_INFLACION','DIF_PIB']].corr()

print(df.columns)