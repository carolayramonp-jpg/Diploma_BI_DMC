# Importamos Streamlit para crear la aplicación web
import streamlit as st

# Importamos Pandas para leer archivos CSV y Excel
import pandas as pd


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


# ==============================
# MÓDULO HOME
# ==============================

if modulos == "Home":

    st.write("Bienvenido a la aplicación")

    if st.session_state.data is not None:
        st.success(f"Dataset cargado: {st.session_state.nombre_archivo}")
    else:
        st.info("Aún no se ha cargado ningún dataset.")


# ==============================
# MÓDULO CARGA Y PERFIL
# ==============================

elif modulos == "Carga y perfil del dataset":

    st.subheader("Carga y perfil del dataset")

    # Creamos un cargador de archivos para subir archivos Excel o CSV
    archivo = st.file_uploader(
        "Cargue el archivo Excel o CSV",
        type=["csv", "xlsx"]
    )

    # Validamos si el usuario cargó un archivo
    if archivo is not None:

        # Guardamos el nombre del archivo en session_state
        st.session_state.nombre_archivo = archivo.name

        # Validamos si el archivo cargado tiene extensión .csv
        if archivo.name.endswith(".csv"):

            # Leemos el archivo CSV y lo guardamos en session_state
            st.session_state.data = pd.read_csv(archivo)

        # Validamos si el archivo cargado tiene extensión .xlsx
        elif archivo.name.endswith(".xlsx"):

            # Leemos el archivo Excel y lo guardamos en session_state
            st.session_state.data = pd.read_excel(archivo)

        # Si el archivo no es CSV ni Excel, mostramos un mensaje de error
        else:
            st.error("Formato no válido")

        # Confirmamos que el archivo fue cargado
        st.success("Archivo cargado correctamente")

    # Si ya existe un dataset cargado, lo mostramos
    if st.session_state.data is not None:

        st.write(f"Archivo actual: **{st.session_state.nombre_archivo}**")

        st.subheader("Vista previa del dataset")
        st.dataframe(st.session_state.data)

        st.subheader("Perfil básico del dataset")

        # Número de filas y columnas
        st.write("Filas:", st.session_state.data.shape[0])
        st.write("Columnas:", st.session_state.data.shape[1])

        # Nombres de columnas
        st.write("Columnas del dataset:")
        st.write(st.session_state.data.columns.tolist())

        # Tipos de datos
        st.write("Tipos de datos:")
        st.write(st.session_state.data.dtypes)

        # Valores nulos
        st.write("Valores nulos por columna:")
        st.write(st.session_state.data.isnull().sum())

        # Estadística descriptiva
        st.write("Estadística descriptiva:")
        st.write(st.session_state.data.describe())

        # Botón para eliminar el dataset cargado
        if st.button("Eliminar dataset cargado"):
            st.session_state.data = None
            st.session_state.nombre_archivo = None
            st.rerun()

    else:
        st.write("Por favor cargue su archivo.")


# ==============================
# MÓDULO PROCESAMIENTO DE DATOS
# ==============================

elif modulos == "Procesamiento de datos":

    st.subheader("Procesamiento de datos")

    if st.session_state.data is not None:

        data = st.session_state.data

        st.write("Dataset disponible para procesamiento:")
        st.dataframe(data)

        st.write("Valores nulos por columna:")
        st.write(data.isnull().sum())

    else:
        st.warning(
            "Primero debe cargar un dataset en el módulo "
            "'Carga y perfil del dataset'."
        )


# ==============================
# MÓDULO ANÁLISIS VISUAL
# ==============================

elif modulos == "Análisis visual":

    st.subheader("Análisis visual")

    if st.session_state.data is not None:

        data = st.session_state.data

        st.write("Dataset disponible para análisis visual:")
        st.dataframe(data)

    else:
        st.warning(
            "Primero debe cargar un dataset en el módulo "
            "'Carga y perfil del dataset'."
        )
    lista_columna_numerica = data.select_dtypes(include = "number").columns.tolist()
    variable_numerica = st.selectbox("Selecione la columna númerica",lista_columna_numerica)

    lista_columna_categorica = data.select_dtypes(include=["object", "category"]).columns.tolist()
    variable_categorica = st.selectbox("Seleccione la columna categórica",lista_columna_categorica)
