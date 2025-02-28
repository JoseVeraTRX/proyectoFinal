# Importamos las librerías, verificar sí están instaladas
import streamlit as st
# Configuración de la interfaz (Debe ir antes de cualquier otro comando de Streamlit)
st.set_page_config(layout="wide")
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

#-----------------

# Cargar datos
@st.cache_data
def load_data():
    file_path = "dataSetProyectoF-MHMS.xlsx" 
    # Definimos la ruta, si el archivo .xlsx no se encuentra en la misma carpeta del archivo se debe configurar adecuadamente la ruta
    xls = pd.ExcelFile(file_path)
    df_dict = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return df_dict
    # retornamos el dataframe diccionario
data = load_data()

def preprocess_data(df_dict):
    # Unir todas las hojas en un solo DataFrame
    df = pd.concat(df_dict.values(), ignore_index=True)
    
    # Crear columna de tasa de suicidio por cada 100k habitantes
    df["Tasa_Suicidio"] = (df["NCasos"] / df["Total_edad_total"]) * 100000
    # la tasa de sucicidios será el numero de casos divido por el total multiplicado por cada 100k habitantes
    return df

df = preprocess_data(data)
st.image("alphadeltabanner.png", use_container_width=True)

st.title("Análisis de Suicidio en Antioquia")
st.markdown("Este panel muestra el análisis de suicidio basado en población y edad")

subregiones = {
    "Bajo Cauca": ["Cáceres", "Caucasia", "El Bagre", "Nechí", "Tarazá", "Zaragoza"],
    "Magdalena Medio": ["Caracolí", "Maceo", "Puerto Berrío", "Puerto Nare", "Puerto Triunfo", "Yondó"],
    "Nordeste": ["Amalfi", "Anorí", "Cisneros", "Remedios", "San Roque", "Santo Domingo", "Segovia", "Vegachí", "Yalí", "Yolombó"],
    "Norte": ["Angostura", "Belmira", "Briceño", "Campamento", "Carolina", "Donmatías", "Entrerríos", "Gómez Plata", "Guadalupe",
              "Ituango", "San Andrés de Cuerquia", "San José de la Montaña", "San Pedro de los Milagros", "Santa Rosa de Osos",
              "Toledo", "Valdivia", "Yarumal"],
    "Occidente": ["Abriaquí", "Armenia", "Buriticá", "Cañasgordas", "Dabeiba", "Ebéjico", "Frontino", "Giraldo", "Heliconia",
                  "Liborina", "Olaya", "Peque", "Sabanalarga", "San Jerónimo", "Santa Fe de Antioquia", "Sopetrán", "Uramita"],
    "Oriente": ["Alejandría", "Argelia", "Cocorná", "Concepción", "El Carmen de Viboral", "El Peñol", "Granada", "Guarne", "Guatapé",
                "La Ceja", "La Unión", "Marinilla", "Nariño", "Retiro", "Rionegro", "San Carlos", "San Francisco", "San Luis",
                "San Rafael", "San Vicente"],
    "Suroeste": ["Amagá", "Andes", "Angelópolis", "Betania", "Betulia", "Caramanta", "Concordia", "Fredonia", "Hispania",
                 "Jardín", "Jericó", "La Pintada", "Montebello", "Pueblorrico", "Salgar", "Santa Bárbara", "Támesis",
                 "Tarso", "Titiribí", "Urrao", "Valparaíso", "Venecia"],
    "Urabá": ["Apartadó", "Arboletes", "Carepa", "Chigorodó", "Murindó", "Mutatá", "Necoclí", "San Juan de Urabá", "San Pedro de Urabá",
              "Turbo", "Vigía del Fuerte"],
    "Valle de Aburrá": ["Barbosa", "Bello", "Caldas", "Copacabana", "Envigado", "Girardota", "Itagüí", "La Estrella", "Medellín",
                        "Sabaneta"]
}

# Filtros dinámicos
opciones_filtro = ["Todos"] + list(subregiones.keys())+list(df["Municipio"].unique())
años = sorted(df["Año"].unique())

col_filtros1, col_filtros2 = st.columns([1, 2])
seleccion = col_filtros1.selectbox("Selecciona una subregión o municipio", opciones_filtro)
año_seleccionado = col_filtros2.slider("Selecciona el rango de años", min_value=min(años), max_value=max(años), value=(min(años), max(años)))

# Filtrado de datos
df_filtrado = df[(df["Año"] >= año_seleccionado[0]) & (df["Año"] <= año_seleccionado[1])]
if seleccion != "Todos":
    if seleccion in subregiones:
        df_filtrado=df_filtrado[df_filtrado["Municipio"].isin(subregiones[seleccion])]
    else:   
        df_filtrado = df_filtrado[df_filtrado["Municipio"] == seleccion]

# Cálculo de población masculina y femenina
poblacion_total = df_filtrado["Total_edad_total"].sum()
poblacion_hombres = df_filtrado["Total_hombres"].sum()
poblacion_mujeres = poblacion_total - poblacion_hombres
porcentaje_hombres = (poblacion_hombres / poblacion_total) * 100 if poblacion_total > 0 else 0
porcentaje_mujeres = (poblacion_mujeres / poblacion_total) * 100 if poblacion_total > 0 else 0

total_suicidios = df_filtrado["NCasos"].sum()
tasa_promedio = df_filtrado["Tasa_Suicidio"].mean()

# Diseño en una sola línea horizontal
col1, col2, col3 = st.columns(3)
col1.metric("Población Total", f"{poblacion_total:,}")
col2.metric("Casos de Suicidio", f"{total_suicidios}")
col3.metric("Tasa Promedio", f"{tasa_promedio:.2f} por 100k")

# Diseño de gráficos en una sola fila
col_g1, col_g2, col_g3 = st.columns(3)

# # Gráfica de distribución de género con valores exactos
# genero_df = pd.DataFrame({
#     "Género": ["Hombres", "Mujeres"],
#     "Población": [poblacion_hombres, poblacion_mujeres]
# })
# fig_genero = px.bar(genero_df, x="Género", y="Población", title="Distribución de Población por Género")
# col_g1.plotly_chart(fig_genero, use_container_width=True)

# Gráfica de distribución de género
genero_df = pd.DataFrame({
    "Género": ["Hombres", "Mujeres"],
    "Porcentaje": [porcentaje_hombres, porcentaje_mujeres]
})
fig_genero = px.bar(genero_df, x="Género", y="Porcentaje", title="Distribución de Población por Género")
col_g1.plotly_chart(fig_genero, use_container_width=True)
# Mostrar valores exactos
st.markdown(f"*Hombres:* {poblacion_hombres:,} | *Mujeres:* {poblacion_mujeres:,}")

# Gráfica de Línea de Tiempo
time_fig = px.line(df_filtrado, x="Año", y="NCasos", color="Municipio", title="Evolución de Suicidios")
col_g2.plotly_chart(time_fig, use_container_width=True)

# Gráfica de evolución de la población
time_fig_poblacion = px.line(df_filtrado, x="Año", y="Total_edad_total", color="Municipio", title="Evolución del Crecimiento Poblacional")
col_g3.plotly_chart(time_fig_poblacion, use_container_width=True)

# Mapa de Calor
# heatmap_data = df_filtrado.groupby(["Municipio", "Año"])["Tasa_Suicidio"].mean().reset_index()
# heatmap_fig = px.density_heatmap(heatmap_data, x="Año", y="Municipio", z="Tasa_Suicidio", title="Mapa de Calor de Suicidios")
# col_g3.plotly_chart(heatmap_fig, use_container_width=True)

#El mapa de calor no brinda información relevante, debido a la gran catidad de municipios, de manera individual no hay un valor 
#importante para poder hacer un correcto análsis de corrrelaciones. 

#GRÁFICO COMBINADO

if seleccion != "Todos" and seleccion not in subregiones.keys():
    # Crear un gráfico combinado (barras para suicidios y línea para población)
    fig_combinado = go.Figure()

    # Crear la figura combinada
    fig_combinado = go.Figure()

    # Agregar barras para número de casos de suicidio
    fig_combinado.add_trace(go.Bar(
        x=df_filtrado["Año"],
        y=df_filtrado["NCasos"],
        name="Casos de Suicidio",
        marker_color="red",
        opacity=0.6
    ))

    # Agregar línea para la población total
    fig_combinado.add_trace(go.Scatter(
        x=df_filtrado["Año"],
        y=df_filtrado["Total_edad_total"],
        name="Población Total",
        mode="lines+markers",
        line=dict(color="blue", width=2),
        yaxis="y2"  # Eje secundario
    ))

    # Configurar ejes
    fig_combinado.update_layout(
        title="Comparación de Casos de Suicidio vs Población Total",
        xaxis=dict(title="Año"),
        yaxis=dict(title="Casos de Suicidio", side="left"),
        yaxis2=dict(
            title="Población Total",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(x=0.01, y=1),
        barmode="group"
    )

    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig_combinado, use_container_width=True)

# Segunda fila de gráficos
col_g4, col_g5 = st.columns(2)

# Gráfica de Barras (Rangos de Edad)
edades_cols = [col for col in df.columns if "_edad_total" in col and col != "Total_edad_total"]
edad_data = df_filtrado.melt(id_vars=["Municipio", "Año"], value_vars=edades_cols, var_name="Grupo Edad", value_name="Poblacion")
edad_fig = px.bar(edad_data, x="Grupo Edad", y="Poblacion", color="Municipio", title="Distribución de Población por Edad")
col_g4.plotly_chart(edad_fig, use_container_width=True)

# Gráfica de Dispersión
# scatter_fig = px.scatter(df_filtrado, x="Total_edad_total", y="NCasos", color="Municipio", title="Casos de Suicidio vs. Población Total")
# col_g5.plotly_chart(scatter_fig, use_container_width=True)

#
# Gráfico de Torta por Subregión (si se selecciona una subregión o "Todos")
if seleccion in subregiones or seleccion == "Todos":
    # Agrupar datos por subregión
    df_subregiones = df_filtrado.groupby("Municipio").agg({
        "NCasos": "sum",
        "Total_edad_total": "sum"
    }).reset_index()
    
    # Asignar subregión a cada municipio
    df_subregiones["Subregión"] = df_subregiones["Municipio"].apply(
        lambda x: next((k for k, v in subregiones.items() if x in v), None))
    
    # Agrupar por subregión
    df_subregiones = df_subregiones.groupby("Subregión").agg({
        "NCasos": "sum",
        "Total_edad_total": "sum"
    }).reset_index()
    
    # Crear gráfico de torta
    fig_torta = px.pie(df_subregiones, values="NCasos", names="Subregión", title="Distribución de Casos de Suicidio por Subregión")
    st.plotly_chart(fig_torta, use_container_width=True)
    
    # Mostrar la cantidad exacta de casos por subregión
    st.write("Cantidad exacta de casos por subregión:")
    st.dataframe(df_subregiones[["Subregión", "NCasos"]].set_index("Subregión"))
