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
