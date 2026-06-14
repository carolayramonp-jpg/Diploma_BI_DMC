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
st.write("Elaborado por: Carlos Carrillo")


# ==============================
# MENÚ DE MÓDULOS
# ==============================

modulos = st.sidebar.selectbox( "Seleccione un módulo",
                               ["Home","Carga y perfil del dataset","Procesamiento de datos", "Análisis visual"])
