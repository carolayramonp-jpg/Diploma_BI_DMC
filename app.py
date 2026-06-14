# Importamos Streamlit para crear la aplicación web
import streamlit as st

# Importamos Pandas para leer y manipular los datos
import pandas as pd

# Importamos NumPy para operaciones numéricas auxiliares
import numpy as np

# Importamos Matplotlib y Seaborn para gráficos estáticos
import matplotlib.pyplot as plt
import seaborn as sns

# Importamos Plotly Express para gráficos interactivos
import plotly.express as px

# Importamos os para verificar si existen los datasets de ejemplo del proyecto
import os


# ==============================
# CONFIGURACIÓN DE SESSION STATE
# ==============================

# Guardamos el dataset cargado
if "data" not in st.session_state:
    st.session_state.data = None

# Guardamos el nombre del archivo cargado
if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = None

# ==============================
# TÍTULO E IMÁGENES
# ==============================

# Creamos el título principal de la aplicación
st.title("Proyecto Final Diploma BI")

# Creamos un título en la barra lateral
st.sidebar.title("Parámetros")

# Mostramos una imagen en la página principal con un ancho de 500 píxeles
st.image("Python_logo.png", width=500)

# Mostramos una imagen en la barra lateral con un ancho de 100 píxeles
st.sidebar.image("DMC.png", width=100)

# Mostramos un texto indicando el autor del proyecto
st.write("Elaborado por: Carolay Ramon Palacin")


# ==============================
# MENÚ DE MÓDULOS
# ==============================

modulos = st.sidebar.selectbox( "Seleccione un módulo",
                               ["Home","Carga y perfil del dataset","Procesamiento de datos", "Análisis visual"])

# ==============================
# FUNCIONES AUXILIARES
# ==============================
# Estas funciones se usan en varios módulos de la app, por lo que se
# definen una sola vez y se reutilizan donde sea necesario.

@st.cache_data
def cargar_csv(archivo):
    """Lee un archivo CSV cargado por el usuario."""
    return pd.read_csv(archivo)


@st.cache_data
def cargar_excel(archivo):
    """Lee un archivo Excel cargado por el usuario."""
    return pd.read_excel(archivo)


@st.cache_data
def cargar_csv_local(ruta):
    """Lee un archivo CSV que ya viene incluido en el proyecto (carpeta data/)."""
    return pd.read_csv(ruta)


def estandarizar_columnas(df):
    """
    Estandariza los nombres de columnas:
    - Quita espacios al inicio y al final.
    - Reemplaza espacios internos por guion bajo.
    Esto evita problemas al referenciar columnas con espacios.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
    )
    return df


def obtener_columnas_numericas(df):
    """Devuelve la lista de columnas numéricas del dataframe."""
    return df.select_dtypes(include="number").columns.tolist()


def obtener_columnas_categoricas(df):
    """Devuelve la lista de columnas categóricas (texto) del dataframe."""
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def obtener_columnas_fecha(df):
    """
    Detecta columnas de fecha de dos formas:
    1. Columnas que ya tienen tipo datetime.
    2. Columnas de texto cuyos valores tienen formato de fecha
       (contienen separadores como '-', '/' o ':') y que, al
       convertirlas con pd.to_datetime, en su mayoría son válidas.
    """
    columnas_fecha = []

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            columnas_fecha.append(col)
            continue

        if df[col].dtype == "object":
            muestra = df[col].dropna().astype(str).head(30)

            if muestra.empty:
                continue

            # Solo evaluamos columnas cuyo texto se "parece" a una fecha
            parece_fecha = muestra.str.contains(r"[-/:]").mean() > 0.7

            if parece_fecha:
                convertidos = pd.to_datetime(muestra, errors="coerce")
                if convertidos.notna().mean() > 0.7:
                    columnas_fecha.append(col)

    return columnas_fecha


def obtener_columnas_binarias(df):
    """Devuelve las columnas que tienen exactamente 2 valores únicos (sin contar nulos)."""
    columnas_binarias = []

    for col in df.columns:
        valores_unicos = df[col].dropna().unique()
        if len(valores_unicos) == 2:
            columnas_binarias.append(col)

    return columnas_binarias


def convertir_columnas_fecha(df):
    """
    Convierte a tipo datetime las columnas detectadas como fecha.
    Los valores que no se puedan convertir quedan como NaT (errors='coerce'),
    siguiendo la recomendación del PDF del proyecto.
    """
    df = df.copy()
    columnas_fecha = obtener_columnas_fecha(df)

    for col in columnas_fecha:
        if not pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def calcular_outliers_iqr(df, columna):
    """
    Calcula los límites de outliers de una columna numérica usando el
    rango intercuartílico (IQR) y devuelve:
    - la cantidad de valores atípicos
    - el límite inferior
    - el límite superior
    """
    serie = df[columna].dropna()

    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = serie[(serie < limite_inferior) | (serie > limite_superior)]

    return len(outliers), limite_inferior, limite_superior


# Datasets de ejemplo propuestos en el PDF del proyecto.
# Si el estudiante coloca estos archivos dentro de una carpeta "data/"
# (tal como sugiere la estructura del proyecto), la app podrá cargarlos
# directamente sin necesidad de subir un archivo manualmente.
DATASETS_EJEMPLO = {
    "AI Impact on Jobs 2030": "data/AI_Impact_on_Jobs_2030.csv",
    "Superstore (Ventas)": "data/sample_-_superstore.csv",
    "E-commerce Order Risk": "data/synthetic_ecommerce_order_risk_dataset.csv",
    "Teen Mental Health": "data/Teen_Mental_Health_Dataset.csv",
}

# ==============================
# MÓDULO HOME
# ==============================

if modulos == "Home":

    st.write("Bienvenido a la aplicación")

    # ---- Información general del proyecto ----
    st.markdown("## Información del proyecto")
    st.markdown(
        """
        **Proyecto:** App analizadora de datasets con Streamlit
        **Curso:** Diploma Business Analyst – Exploración y visualización de datos con Python
        **Elaborado por:** Carlos Carrillo Villavicencio
        **Año:** 2026
        """
    )

    # ---- Objetivo del proyecto ----
    st.markdown("## Objetivo del proyecto")
    st.write(
        "Esta aplicación permite cargar, explorar, procesar y visualizar de forma "
        "interactiva distintos datasets. La idea es contar con una herramienta de "
        "análisis exploratorio de datos (EDA) flexible, que se adapte a diferentes "
        "estructuras de información sin depender de un único archivo ni de columnas fijas."
    )

    # ---- Descripción de los datasets disponibles ----
    st.markdown("## Datasets contemplados en el proyecto")
    st.markdown(
        """
        - **AI Impact on Jobs 2030**: mercado laboral e impacto de la inteligencia
          artificial en empleos, salarios, habilidades y demanda futura.
        - **Superstore**: ventas de una tienda (pedidos, clientes, regiones,
          categorías, ventas, descuentos y utilidad).
        - **E-commerce Order Risk**: pedidos de comercio electrónico con variables de
          país, dispositivo, método de pago, valor de orden, entregas, devoluciones y riesgo de fraude.
        - **Teen Mental Health**: hábitos digitales, sueño, actividad física e
          interacción social en adolescentes, con fines exploratorios.
        """
    )

    # ---- Tecnologías usadas ----
    st.markdown("## Tecnologías utilizadas")
    st.markdown(
        """
        - Python
        - Pandas
        - Streamlit
        - Plotly
        - Matplotlib
        - Seaborn
        - GitHub
        """
    )

    # ---- Nota de uso responsable ----
    st.markdown("## Nota de uso responsable")
    st.info(
        "Los resultados mostrados en esta aplicación son de carácter exploratorio. "
        "No reemplazan una validación técnica, estadística o profesional."
    )

    st.markdown("---")

    # ---- Estado actual del dataset cargado ----
    if st.session_state.data is not None:
        st.success(f"Dataset cargado: {st.session_state.nombre_archivo}")
    else:
        st.info("Aún no se ha cargado ningún dataset.")
