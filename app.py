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
    """Devuelve la lista de columnas categóricas del dataframe."""
    return df.select_dtypes(include=["object", "category", "str"]).columns.tolist()


def obtener_columnas_fecha(df):
    """
    Detecta columnas de fecha de dos formas:
    Columnas que ya tienen tipo datetime y columnas de texto cuyos valores tienen formato de fecha
    """
    columnas_fecha = []

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            columnas_fecha.append(col)
            continue

        if pd.api.types.is_string_dtype(df[col]):
            muestra = df[col].dropna().astype(str).head(30)

            if muestra.empty:
                continue

            # Solo evaluamos columnas cuyo texto se parece a una fecha
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
    Los valores que no se puedan convertir quedan como NaT (errors='coerce')
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
    rango intercuartílico y devuelve:
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


# Datasets de ejemplo
DATASETS_EJEMPLO = {
    "AI Impact on Jobs 2030": "data/AI_Impact_on_Jobs_2030.csv",
    "Superstore (Ventas)": "data/sample_-_superstore.csv",
    "E-commerce Order Risk": "data/synthetic_ecommerce_order_risk_dataset.csv",
    "Teen Mental Health": "data/Teen_Mental_Health_Dataset.csv",
}


# ==============================
# TÍTULO E IMÁGENES
# ==============================

# Creamos el título principal de la aplicación
st.title("Proyecto Final Diploma BI")

# Creamos un título en la barra lateral
st.sidebar.title("Parámetros")

# Mostramos una imagen en la página principal con un ancho de 500 píxeles
st.image("assets/Python_logo.png", width=500)

# Mostramos una imagen en la barra lateral con un ancho de 100 píxeles
st.sidebar.image("assets/DMC.png", width=100)

# Mostramos un texto indicando el autor del proyecto
st.write("Elaborado por: Carolay Ramon Palacin")


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

    # ---- Información general del proyecto ----
    st.markdown("## Información del proyecto")
    st.markdown(
        """
        **Proyecto:** App analizadora de datasets con Streamlit
        **Curso:** Diploma Business Analyst – Exploración y visualización de datos con Python
        **Elaborado por:** Carolay Ramon Palacin
        **Año:** 2026
        """
    )

    # ---- Objetivo del proyecto ----
    st.markdown("## Objetivo del proyecto")
    st.write(
        "Esta aplicación permite cargar, explorar, procesar y visualizar de forma "
        "interactiva distintos datasets. La idea es contar con una herramienta de "
        "análisis exploratorio de datos flexible, que se adapte a diferentes "
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

    st.markdown("---")

    # ---- Estado actual del dataset cargado ----
    if st.session_state.data is not None:
        st.success(f"Dataset cargado: {st.session_state.nombre_archivo}")
    else:
        st.info("Aún no se ha cargado ningún dataset.")


# ==============================
# MÓDULO CARGA Y PERFIL
# ==============================

elif modulos == "Carga y perfil del dataset":

    st.subheader("Carga y perfil del dataset")

    # ---- El usuario elige cómo quiere cargar los datos ----
    origen_datos = st.radio(
        "¿Cómo desea cargar el dataset?",
        ["Subir archivo (CSV o Excel)", "Usar un dataset de ejemplo del proyecto"]
    )

    # --------------------------------------------------
    # OPCIÓN 1: Subida de archivo propio
    # --------------------------------------------------
    if origen_datos == "Subir archivo (CSV o Excel)":

        # Creamos un cargador de archivos para subir archivos Excel o CSV
        archivo = st.file_uploader(
            "Cargue el archivo Excel o CSV",
            type=["csv", "xlsx"]
        )

        # Validamos si el usuario cargó un archivo
        if archivo is not None:

            # Guardamos el nombre del archivo en session_state
            st.session_state.nombre_archivo = archivo.name

            df_cargado = None

            # Validamos si el archivo cargado tiene extensión .csv
            if archivo.name.endswith(".csv"):
                df_cargado = cargar_csv(archivo)

            # Validamos si el archivo cargado tiene extensión .xlsx
            elif archivo.name.endswith(".xlsx"):
                df_cargado = cargar_excel(archivo)

            # Si el archivo no es CSV ni Excel, mostramos un mensaje de error
            else:
                st.error("Formato no válido")

            if df_cargado is not None:
                # Estandarizamos los nombres de columnas antes de guardarlo
                st.session_state.data = estandarizar_columnas(df_cargado)

                # Confirmamos que el archivo fue cargado
                st.success("Archivo cargado correctamente")

    # --------------------------------------------------
    # OPCIÓN 2: Datasets de ejemplo del proyecto
    # --------------------------------------------------
    else:

        dataset_elegido = st.selectbox(
            "Seleccione un dataset de ejemplo",
            list(DATASETS_EJEMPLO.keys())
        )

        if st.button("Cargar dataset seleccionado"):

            ruta = DATASETS_EJEMPLO[dataset_elegido]

            # Verificamos que el archivo exista antes de intentar leerlo,
            # para que la app no se detenga si la carpeta "data/" no está disponible.
            if os.path.exists(ruta):
                df_cargado = cargar_csv_local(ruta)
                st.session_state.data = estandarizar_columnas(df_cargado)
                st.session_state.nombre_archivo = os.path.basename(ruta)
                st.success("Dataset cargado correctamente")
            else:
                st.error(
                    f"No se encontró el archivo '{ruta}'. "
                    "Verifique que los datasets de ejemplo estén dentro de la carpeta "
                    "'data/' del proyecto, o utilice la opción de subir su propio archivo."
                )

    # --------------------------------------------------
    # VISTA PREVIA Y PERFIL DEL DATASET CARGADO
    # --------------------------------------------------
    if st.session_state.data is not None:

        data = st.session_state.data

        st.write(f"Archivo actual: **{st.session_state.nombre_archivo}**")

        st.subheader("Vista previa del dataset")
        st.dataframe(data.head(10))

        st.subheader("Perfil básico del dataset")

        # Detectamos los tipos de columnas para mostrar métricas rápidas
        columnas_numericas = obtener_columnas_numericas(data)
        columnas_categoricas = obtener_columnas_categoricas(data)
        columnas_fecha = obtener_columnas_fecha(data)

        # ---- Métricas rápidas ----
        col1, col2, col3 = st.columns(3)
        col1.metric("Filas", data.shape[0])
        col2.metric("Columnas", data.shape[1])
        col3.metric("Filas duplicadas", int(data.duplicated().sum()))

        col4, col5, col6 = st.columns(3)
        col4.metric("Columnas numéricas", len(columnas_numericas))
        col5.metric("Columnas categóricas", len(columnas_categoricas))
        col6.metric("Valores nulos totales", int(data.isnull().sum().sum()))

        # Nombres de columnas
        st.write("Columnas del dataset:")
        st.write(data.columns.tolist())

        # Tipos de datos
        st.write("Tipos de datos:")
        st.write(data.dtypes)

        # Valores nulos
        st.write("Valores nulos por columna:")
        st.write(data.isnull().sum())

        # Estadística descriptiva
        st.write("Estadística descriptiva:")
        st.write(data.describe())

        # ---- Selección de columnas relevantes ----
        st.subheader("Selección de columnas relevantes")
        columnas_seleccionadas = st.multiselect(
            "Seleccione columnas para revisar en detalle (opcional)",
            data.columns.tolist()
        )

        if columnas_seleccionadas:
            st.dataframe(data[columnas_seleccionadas].head(10))

        # ---- Mensajes según los tipos de variables encontrados ----
        if not columnas_numericas:
            st.warning("El dataset no contiene columnas numéricas.")

        if not columnas_categoricas:
            st.info("El dataset no contiene columnas categóricas.")

        if not columnas_fecha:
            st.info("No se detectaron columnas de fecha en este dataset.")

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

        # Aplicamos la conversión de columnas de fecha (errors="coerce")
        data = convertir_columnas_fecha(st.session_state.data)

        st.write("Dataset disponible para procesamiento:")
        st.dataframe(data.head(10))

        # --------------------------------------------------
        # Clasificación automática de variables
        # --------------------------------------------------
        st.markdown("### Clasificación automática de variables")

        columnas_numericas = obtener_columnas_numericas(data)
        columnas_categoricas = obtener_columnas_categoricas(data)
        columnas_fecha = obtener_columnas_fecha(data)
        columnas_binarias = obtener_columnas_binarias(data)

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Columnas numéricas:**")
            st.write(columnas_numericas if columnas_numericas else "Ninguna")

            st.write("**Columnas de fecha:**")
            st.write(columnas_fecha if columnas_fecha else "Ninguna")

        with col2:
            st.write("**Columnas categóricas:**")
            st.write(columnas_categoricas if columnas_categoricas else "Ninguna")

            st.write("**Columnas binarias (2 valores únicos):**")
            st.write(columnas_binarias if columnas_binarias else "Ninguna")

        if not columnas_numericas:
            st.warning("No se detectaron columnas numéricas en este dataset.")

        if not columnas_categoricas:
            st.info("No se detectaron columnas categóricas en este dataset.")

        # --------------------------------------------------
        # Conversión de columnas de fecha
        # --------------------------------------------------
        st.markdown("### Conversión de columnas de fecha")

        if columnas_fecha:
            st.success(
                "Las siguientes columnas fueron identificadas y convertidas a "
                f"formato fecha: {', '.join(columnas_fecha)}"
            )
            # Guardamos el dataset con las fechas ya convertidas para que
            # los demás módulos (por ejemplo, Análisis visual) las reutilicen.
            st.session_state.data = data
        else:
            st.info("No se encontraron columnas que parezcan ser de tipo fecha.")

        # --------------------------------------------------
        # Valores nulos
        # --------------------------------------------------
        st.markdown("### Valores nulos por columna")

        nulos = data.isnull().sum()
        porcentaje_nulos = (nulos / len(data) * 100).round(2)

        tabla_nulos = pd.DataFrame({
            "valores_nulos": nulos,
            "porcentaje_nulos": porcentaje_nulos
        })

        st.dataframe(tabla_nulos)

        if nulos.sum() > 0:
            tabla_nulos_filtrada = tabla_nulos[tabla_nulos["valores_nulos"] > 0]

            fig_nulos = px.bar(
                tabla_nulos_filtrada,
                x=tabla_nulos_filtrada.index,
                y="valores_nulos",
                title="Cantidad de valores nulos por columna",
                labels={"x": "Columna", "valores_nulos": "Valores nulos"}
            )
            st.plotly_chart(fig_nulos, use_container_width=True)
        else:
            st.success("El dataset no presenta valores nulos.")

        # --------------------------------------------------
        # Duplicados
        # --------------------------------------------------
        st.markdown("### Filas duplicadas")

        num_duplicados = int(data.duplicated().sum())
        st.write(f"Número de filas duplicadas encontradas: **{num_duplicados}**")

        if num_duplicados > 0:
            if st.button("Eliminar filas duplicadas"):
                data_sin_duplicados = data.drop_duplicates()
                st.session_state.data = data_sin_duplicados
                st.success(f"Se eliminaron {num_duplicados} filas duplicadas.")
                st.rerun()
        else:
            st.success("No se encontraron filas duplicadas.")

        # --------------------------------------------------
        # Detección de outliers
        # --------------------------------------------------
        st.markdown("### Detección de valores atípicos")

        if columnas_numericas:
            columna_outlier = st.selectbox(
                "Seleccione una columna numérica para revisar valores atípicos",
                columnas_numericas
            )

            n_outliers, lim_inf, lim_sup = calcular_outliers_iqr(data, columna_outlier)

            colA, colB, colC = st.columns(3)
            colA.metric("Límite inferior", round(float(lim_inf), 2))
            colB.metric("Límite superior", round(float(lim_sup), 2))
            colC.metric("Outliers detectados", n_outliers)

            # Boxplot para visualizar los outliers
            fig_outlier = px.box(
                data,
                y=columna_outlier,
                title=f"Boxplot de la variable '{columna_outlier}'"
            )
            st.plotly_chart(fig_outlier, use_container_width=True)

            st.caption(
                "Los valores atípicos se calculan con el rango intercuartílico: "
                "se consideran outliers los valores por debajo de Q1 - 1.5*IQR o por "
                "encima de Q3 + 1.5*IQR."
            )
        else:
            st.info("No hay columnas numéricas disponibles para el análisis de outliers.")

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

        # Trabajamos con el dataset y nos asegamos de que las fechas estén convertidas
        data = convertir_columnas_fecha(st.session_state.data)

        # Detectamos los tipos de columnas disponibles en el dataset
        columnas_numericas = obtener_columnas_numericas(data)
        columnas_categoricas = obtener_columnas_categoricas(data)
        columnas_fecha = obtener_columnas_fecha(data)

        # --------------------------------------------------
        # FILTROS DINÁMICOS (barra lateral)
        # --------------------------------------------------
        st.sidebar.markdown("### Filtros para el análisis visual")

        data_filtrada = data.copy()

        # ---- Filtro por una columna categórica ----
        if columnas_categoricas:
            columna_filtro_cat = st.sidebar.selectbox(
                "Filtrar por columna categórica",
                ["(Sin filtro)"] + columnas_categoricas
            )

            if columna_filtro_cat != "(Sin filtro)":
                valores_disponibles = data[columna_filtro_cat].dropna().unique().tolist()

                valores_seleccionados = st.sidebar.multiselect(
                    f"Valores de '{columna_filtro_cat}' a incluir",
                    valores_disponibles,
                    default=valores_disponibles
                )

                if valores_seleccionados:
                    data_filtrada = data_filtrada[
                        data_filtrada[columna_filtro_cat].isin(valores_seleccionados)
                    ]

        # ---- Filtro por rango de una columna numérica ----
        if columnas_numericas:
            columna_filtro_num = st.sidebar.selectbox(
                "Filtrar por rango numérico",
                ["(Sin filtro)"] + columnas_numericas
            )

            if columna_filtro_num != "(Sin filtro)":
                valores_num = data[columna_filtro_num].dropna()

                if not valores_num.empty:
                    valor_min = float(valores_num.min())
                    valor_max = float(valores_num.max())

                    if valor_min < valor_max:
                        rango_seleccionado = st.sidebar.slider(
                            f"Rango de '{columna_filtro_num}'",
                            min_value=valor_min,
                            max_value=valor_max,
                            value=(valor_min, valor_max)
                        )

                        data_filtrada = data_filtrada[
                            (data_filtrada[columna_filtro_num] >= rango_seleccionado[0]) &
                            (data_filtrada[columna_filtro_num] <= rango_seleccionado[1])
                        ]
                    else:
                        st.sidebar.info(
                            f"La columna '{columna_filtro_num}' tiene un único valor, "
                            "no se aplica filtro."
                        )

        # ---- Filtro por rango de fechas ----
        if columnas_fecha:
            columna_fecha_filtro = columnas_fecha[0]
            fechas_validas = data[columna_fecha_filtro].dropna()

            if not fechas_validas.empty:
                fecha_min = fechas_validas.min().date()
                fecha_max = fechas_validas.max().date()

                if fecha_min < fecha_max:
                    rango_fechas = st.sidebar.slider(
                        f"Rango de fechas ('{columna_fecha_filtro}')",
                        min_value=fecha_min,
                        max_value=fecha_max,
                        value=(fecha_min, fecha_max)
                    )

                    data_filtrada = data_filtrada[
                        (data_filtrada[columna_fecha_filtro].dt.date >= rango_fechas[0]) &
                        (data_filtrada[columna_fecha_filtro].dt.date <= rango_fechas[1])
                    ]

        # ---- Checkbox para ver los datos filtrados ----
        if st.sidebar.checkbox("Mostrar datos filtrados (vista previa)"):
            st.write("Vista previa de los datos filtrados:")
            st.dataframe(data_filtrada.head(20))

        st.caption(
            f"Registros totales: {data.shape[0]} | "
            f"Registros después de aplicar filtros: {data_filtrada.shape[0]}"
        )

        # --------------------------------------------------
        # TABS DE ANÁLISIS
        # --------------------------------------------------
        tab_resumen, tab_univariado, tab_bivariado, tab_multivariado, tab_temporal, tab_insights = st.tabs(
            ["Resumen", "Univariado", "Bivariado", "Multivariado", "Temporal", "Insights"]
        )

        # ====================================================
        # TAB 1: RESUMEN
        # ====================================================
        with tab_resumen:

            st.markdown("### Indicadores principales")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Filas", data_filtrada.shape[0])
            col2.metric("Columnas", data_filtrada.shape[1])
            col3.metric("Valores nulos", int(data_filtrada.isnull().sum().sum()))
            col4.metric("Duplicados", int(data_filtrada.duplicated().sum()))

            st.markdown("### Tipos de datos")
            st.write(data_filtrada.dtypes)

            st.markdown("### Valores nulos por columna")
            st.write(data_filtrada.isnull().sum())

            st.markdown("### Resumen estadístico")
            st.write(data_filtrada.describe())

        # ====================================================
        # TAB 2: ANÁLISIS UNIVARIADO
        # ====================================================
        with tab_univariado:

            st.markdown("### Variables numéricas")

            if columnas_numericas:
                variable_numerica = st.selectbox(
                    "Seleccione una variable numérica",
                    columnas_numericas,
                    key="univ_num"
                )

                col1, col2 = st.columns(2)

                with col1:
                    fig_hist = px.histogram(
                        data_filtrada,
                        x=variable_numerica,
                        nbins=30,
                        title=f"Distribución de {variable_numerica}"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                with col2:
                    fig_box = px.box(
                        data_filtrada,
                        y=variable_numerica,
                        title=f"Boxplot de {variable_numerica}"
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

                if st.checkbox("Mostrar estadísticas descriptivas de esta variable"):
                    st.write(data_filtrada[variable_numerica].describe())

                st.caption(
                    "El histograma muestra cómo se distribuyen los valores de la "
                    "variable seleccionada. El boxplot ayuda a identificar la mediana, "
                    "el rango intercuartílico y posibles valores atípicos."
                )
            else:
                st.info("No hay columnas numéricas disponibles para el análisis univariado.")

            st.markdown("### Variables categóricas")

            if columnas_categoricas:
                variable_categorica = st.selectbox(
                    "Seleccione una variable categórica",
                    columnas_categoricas,
                    key="univ_cat"
                )

                conteo = data_filtrada[variable_categorica].value_counts().reset_index()
                conteo.columns = [variable_categorica, "conteo"]
                conteo["proporcion_%"] = (conteo["conteo"] / conteo["conteo"].sum() * 100).round(2)

                col1, col2 = st.columns(2)

                with col1:
                    fig_bar = px.bar(
                        conteo.head(15),
                        x=variable_categorica,
                        y="conteo",
                        title=f"Conteo de categorías - {variable_categorica}"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col2:
                    st.write("Tabla de frecuencias (top 15):")
                    st.dataframe(conteo.head(15))

                st.caption(
                    "El gráfico de barras muestra las categorías más frecuentes y la "
                    "tabla incluye el conteo y el porcentaje que representa cada categoría."
                )
            else:
                st.info("No hay columnas categóricas disponibles para el análisis univariado.")

        # ====================================================
        # TAB 3: ANÁLISIS BIVARIADO
        # ====================================================
        with tab_bivariado:

            st.markdown("### Numérica vs Numérica")

            if len(columnas_numericas) >= 2:
                col1, col2 = st.columns(2)

                with col1:
                    var_x = st.selectbox("Variable X", columnas_numericas, key="biv_x")
                with col2:
                    opciones_y = [c for c in columnas_numericas if c != var_x]
                    var_y = st.selectbox("Variable Y", opciones_y, key="biv_y")

                fig_scatter = px.scatter(
                    data_filtrada,
                    x=var_x,
                    y=var_y,
                    title=f"Relación entre {var_x} y {var_y}"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

                correlacion = data_filtrada[[var_x, var_y]].corr().iloc[0, 1]
                st.write(f"Correlación entre **{var_x}** y **{var_y}**: **{correlacion:.2f}**")
            else:
                st.info("Se necesitan al menos dos columnas numéricas para este análisis.")

            st.markdown("### Numérica vs Categórica")

            if columnas_numericas and columnas_categoricas:
                col1, col2 = st.columns(2)

                with col1:
                    var_num_cat = st.selectbox("Variable numérica", columnas_numericas, key="biv_num_cat")
                with col2:
                    var_cat_num = st.selectbox("Variable categórica", columnas_categoricas, key="biv_cat_num")

                # Limitamos a las categorías más frecuentes para no saturar el gráfico
                top_categorias = data_filtrada[var_cat_num].value_counts().head(10).index
                data_top = data_filtrada[data_filtrada[var_cat_num].isin(top_categorias)]

                fig_box_cat = px.box(
                    data_top,
                    x=var_cat_num,
                    y=var_num_cat,
                    title=f"{var_num_cat} por {var_cat_num}"
                )
                st.plotly_chart(fig_box_cat, use_container_width=True)

                st.caption(
                    "Se muestran únicamente las 10 categorías más frecuentes para "
                    "mantener el gráfico legible."
                )
            else:
                st.info("Se necesita al menos una columna numérica y una categórica para este análisis.")

            st.markdown("### Categórica vs Categórica")

            if len(columnas_categoricas) >= 2:
                col1, col2 = st.columns(2)

                with col1:
                    cat_1 = st.selectbox("Primera variable categórica", columnas_categoricas, key="biv_cat1")
                with col2:
                    opciones_cat2 = [c for c in columnas_categoricas if c != cat_1]
                    cat_2 = st.selectbox("Segunda variable categórica", opciones_cat2, key="biv_cat2")

                # Limitamos categorías para que el gráfico y la tabla sean legibles
                top_cat1 = data_filtrada[cat_1].value_counts().head(8).index
                top_cat2 = data_filtrada[cat_2].value_counts().head(8).index

                data_cruzada = data_filtrada[
                    data_filtrada[cat_1].isin(top_cat1) & data_filtrada[cat_2].isin(top_cat2)
                ]

                fig_barras_agrupadas = px.histogram(
                    data_cruzada,
                    x=cat_1,
                    color=cat_2,
                    barmode="group",
                    title=f"Distribución de {cat_2} por {cat_1}"
                )
                st.plotly_chart(fig_barras_agrupadas, use_container_width=True)

                st.write("Tabla de contingencia (frecuencias):")
                tabla_cruzada = pd.crosstab(data_cruzada[cat_1], data_cruzada[cat_2])
                st.dataframe(tabla_cruzada)
            else:
                st.info("Se necesitan al menos dos columnas categóricas para este análisis.")

        # ====================================================
        # TAB 4: ANÁLISIS MULTIVARIADO
        # ====================================================
        with tab_multivariado:

            st.markdown("### Matriz de correlación")

            if len(columnas_numericas) >= 2:
                matriz_corr = data_filtrada[columnas_numericas].corr()

                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                ax.set_title("Heatmap de correlación entre variables numéricas")
                st.pyplot(fig)

                st.caption(
                    "Valores cercanos a 1 o -1 indican una relación lineal fuerte "
                    "(positiva o negativa) entre las variables. Valores cercanos a "
                    "0 indican poca relación lineal."
                )
            else:
                st.info("Se necesitan al menos dos columnas numéricas para calcular correlaciones.")

            st.markdown("### Dispersión con una tercera variable (color)")

            if len(columnas_numericas) >= 2 and columnas_categoricas:
                col1, col2, col3 = st.columns(3)

                with col1:
                    mv_x = st.selectbox("Eje X", columnas_numericas, key="mv_x")
                with col2:
                    opciones_mv_y = [c for c in columnas_numericas if c != mv_x]
                    mv_y = st.selectbox("Eje Y", opciones_mv_y, key="mv_y")
                with col3:
                    mv_color = st.selectbox("Color (categórica)", columnas_categoricas, key="mv_color")

                # Limitamos las categorías mostradas para que la leyenda sea legible
                top_categorias_color = data_filtrada[mv_color].value_counts().head(8).index
                data_mv = data_filtrada[data_filtrada[mv_color].isin(top_categorias_color)]

                fig_scatter_mv = px.scatter(
                    data_mv,
                    x=mv_x,
                    y=mv_y,
                    color=mv_color,
                    title=f"{mv_y} vs {mv_x}, segmentado por {mv_color}"
                )
                st.plotly_chart(fig_scatter_mv, use_container_width=True)
            else:
                st.info(
                    "Se necesitan al menos dos columnas numéricas y una columna "
                    "categórica para este análisis."
                )

            st.markdown("### Barras apiladas por categorías")

            if len(columnas_categoricas) >= 2 and columnas_numericas:
                col1, col2, col3 = st.columns(3)

                with col1:
                    apilado_cat_principal = st.selectbox(
                        "Categoría principal (eje X)", columnas_categoricas, key="ap_cat1"
                    )
                with col2:
                    opciones_apilado_cat2 = [c for c in columnas_categoricas if c != apilado_cat_principal]
                    apilado_cat_secundaria = st.selectbox(
                        "Categoría de segmentación (color)", opciones_apilado_cat2, key="ap_cat2"
                    )
                with col3:
                    apilado_valor = st.selectbox(
                        "Variable numérica a sumar", columnas_numericas, key="ap_valor"
                    )

                # Limitamos categorías para que el gráfico sea legible
                top_principal = data_filtrada[apilado_cat_principal].value_counts().head(8).index
                data_apilado = data_filtrada[data_filtrada[apilado_cat_principal].isin(top_principal)]

                tabla_apilada = (
                    data_apilado
                    .groupby([apilado_cat_principal, apilado_cat_secundaria])[apilado_valor]
                    .sum()
                    .reset_index()
                )

                fig_apilado = px.bar(
                    tabla_apilada,
                    x=apilado_cat_principal,
                    y=apilado_valor,
                    color=apilado_cat_secundaria,
                    title=(
                        f"{apilado_valor} por {apilado_cat_principal}, "
                        f"segmentado por {apilado_cat_secundaria}"
                    ),
                    barmode="stack"
                )
                st.plotly_chart(fig_apilado, use_container_width=True)
            else:
                st.info(
                    "Se necesitan al menos dos columnas categóricas y una columna "
                    "numérica para construir el gráfico de barras apiladas."
                )

        # ====================================================
        # TAB 5: ANÁLISIS TEMPORAL
        # ====================================================
        with tab_temporal:

            if columnas_fecha and columnas_numericas:

                col1, col2, col3 = st.columns(3)

                with col1:
                    columna_fecha_sel = st.selectbox("Columna de fecha", columnas_fecha, key="temp_fecha")
                with col2:
                    variable_temporal = st.selectbox("Variable numérica", columnas_numericas, key="temp_num")
                with col3:
                    frecuencia = st.selectbox(
                        "Frecuencia de agrupación",
                        ["Diaria", "Semanal", "Mensual", "Trimestral"],
                        index=2,
                        key="temp_freq"
                    )

                mapa_frecuencia = {"Diaria": "D", "Semanal": "W", "Mensual": "ME", "Trimestral": "QE"}

                # Quitamos filas sin fecha válida y ordenamos cronológicamente
                data_temporal = data_filtrada.dropna(subset=[columna_fecha_sel]).sort_values(columna_fecha_sel)

                if not data_temporal.empty:

                    # Agrupamos la serie según la frecuencia seleccionada
                    serie_temporal = (
                        data_temporal
                        .set_index(columna_fecha_sel)
                        .resample(mapa_frecuencia[frecuencia])[variable_temporal]
                        .sum()
                        .reset_index()
                    )

                    fig_temporal = px.line(
                        serie_temporal,
                        x=columna_fecha_sel,
                        y=variable_temporal,
                        title=f"Evolución de {variable_temporal} ({frecuencia.lower()})",
                        markers=True
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)

                    # Gráfico adicional con Seaborn: cantidad de registros por periodo
                    serie_conteo = (
                        data_temporal
                        .set_index(columna_fecha_sel)
                        .resample(mapa_frecuencia[frecuencia])
                        .size()
                        .reset_index(name="registros")
                    )

                    fig2, ax2 = plt.subplots(figsize=(10, 4))
                    sns.lineplot(data=serie_conteo, x=columna_fecha_sel, y="registros", ax=ax2)
                    ax2.set_title(f"Cantidad de registros por periodo ({frecuencia.lower()})")
                    ax2.set_xlabel("Fecha")
                    ax2.set_ylabel("Registros")
                    plt.xticks(rotation=45)
                    st.pyplot(fig2)

                    st.caption(
                        "El primer gráfico muestra la evolución de la variable numérica "
                        "seleccionada agrupada por el periodo elegido. El segundo gráfico "
                        "muestra cuántos registros existen en cada periodo, lo cual ayuda "
                        "a entender la cantidad de información disponible por fecha."
                    )
                else:
                    st.warning("No hay datos con fechas válidas para el rango seleccionado.")

            elif not columnas_fecha:
                st.info(
                    "Este dataset no tiene columnas de fecha, por lo que no es posible "
                    "realizar un análisis temporal."
                )
            else:
                st.info(
                    "Se necesita al menos una columna numérica para realizar el análisis temporal."
                )

        # ====================================================
        # TAB 6: INSIGHTS
        # ====================================================
        with tab_insights:

            st.markdown("### Hallazgos automáticos")

            st.write(
                "A continuación se presentan algunos hallazgos generales calculados "
                "automáticamente a partir del dataset filtrado. Estos hallazgos son "
                "exploratorios y deben complementarse con el criterio del analista."
            )

            # Aviso adicional si el dataset parece contener variables sensibles de bienestar/salud mental
            columnas_sensibles = [
                "stress_level", "anxiety_level", "depression_label", "addiction_level"
            ]
            if any(col in data_filtrada.columns for col in columnas_sensibles):
                st.warning(
                    "Este dataset contiene variables relacionadas con bienestar y salud "
                    "mental. Los resultados son exploratorios y NO deben interpretarse "
                    "como un diagnóstico clínico."
                )

            # ---- Hallazgo 1: variable numérica con mayor variabilidad ----
            if columnas_numericas:
                desviaciones = data_filtrada[columnas_numericas].std().sort_values(ascending=False)

                if not desviaciones.empty and desviaciones.iloc[0] > 0:
                    st.write(
                        f"- La variable numérica con mayor variabilidad (desviación "
                        f"estándar) es **{desviaciones.index[0]}**, con un valor de "
                        f"**{desviaciones.iloc[0]:.2f}**."
                    )

            # ---- Hallazgo 2: par de variables con mayor correlación ----
            if len(columnas_numericas) >= 2:
                corr_matrix = data_filtrada[columnas_numericas].corr().abs()

                # Quitamos la diagonal (correlación de cada variable consigo misma)
                valores_corr = corr_matrix.values.copy()
                np.fill_diagonal(valores_corr, 0)
                corr_matrix = pd.DataFrame(
                    valores_corr, index=corr_matrix.index, columns=corr_matrix.columns
                )

                if corr_matrix.max().max() > 0:
                    var1, var2 = corr_matrix.stack().idxmax()
                    valor_corr = corr_matrix.loc[var1, var2]
                    st.write(
                        f"- Las variables **{var1}** y **{var2}** presentan la "
                        f"correlación más alta del dataset, con un valor de "
                        f"**{valor_corr:.2f}**."
                    )

            # ---- Hallazgo 3: categoría más frecuente ----
            if columnas_categoricas:
                col_cat_principal = columnas_categoricas[0]
                conteo_cat = data_filtrada[col_cat_principal].value_counts()

                if not conteo_cat.empty:
                    categoria_top = conteo_cat.idxmax()
                    cantidad_top = conteo_cat.max()
                    st.write(
                        f"- En la variable **{col_cat_principal}**, la categoría más "
                        f"frecuente es **{categoria_top}**, con **{cantidad_top}** registros."
                    )

            # ---- Hallazgo 4: columna con mayor porcentaje de nulos ----
            porcentaje_nulos = (data_filtrada.isnull().mean() * 100).sort_values(ascending=False)

            if porcentaje_nulos.iloc[0] > 0:
                st.write(
                    f"- La columna **{porcentaje_nulos.index[0]}** es la que presenta "
                    f"mayor porcentaje de valores nulos "
                    f"(**{porcentaje_nulos.iloc[0]:.1f}%**)."
                )
            else:
                st.write("- El dataset filtrado no presenta valores nulos.")

    else:
        st.warning(
            "Primero debe cargar un dataset en el módulo "
            "'Carga y perfil del dataset'."
        )
