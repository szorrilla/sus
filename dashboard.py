import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Sostenibilidad",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel('Indicadores.xlsx', sheet_name='Hoja3', skiprows=2)
    df.columns = ['Indicador', 'Unidad', 'Frecuencia', 
                 '2022_1', '2022_2', '2023_1', '2023_2', 
                 '2024_1', '2024_2', '2025_1', '2025_2']
    
    melted_df = df.melt(
        id_vars=['Indicador', 'Unidad', 'Frecuencia'], 
        var_name='Periodo', 
        value_name='Valor'
    ).dropna()
    
    melted_df[['Año', 'Semestre']] = melted_df['Periodo'].str.split('_', expand=True)
    melted_df['Semestre'] = melted_df['Semestre'].replace({'1': '1er Semestre', '2': '2do Semestre'})
    melted_df['Año_Semestre'] = melted_df['Año'] + ' ' + melted_df['Semestre']
    return melted_df

# Cargar datos
data = load_data()

# Título
st.title("🌱 Dashboard de Indicadores de Sostenibilidad")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Filtros")
    indicador_seleccionado = st.selectbox("Seleccione un indicador:", data['Indicador'].unique())
    años_disponibles = data['Año'].unique()
    años_seleccionados = st.multiselect("Seleccione años:", años_disponibles, default=años_disponibles)
    semestres_seleccionados = st.multiselect("Seleccione semestres:", ['1er Semestre', '2do Semestre'], default=['1er Semestre', '2do Semestre'])

# Filtro
filtered_data = data[
    (data['Indicador'] == indicador_seleccionado) &
    (data['Año'].isin(años_seleccionados)) &
    (data['Semestre'].isin(semestres_seleccionados))
].copy()

# KPI
st.subheader(f"Indicador: {indicador_seleccionado}")
unidad = filtered_data['Unidad'].iloc[0] if not filtered_data.empty else ""

col1, col2, col3 = st.columns(3)
with col1:
    if not filtered_data.empty:
        st.metric("Último valor", f"{filtered_data.iloc[-1]['Valor']} {unidad}")
with col2:
    if not filtered_data.empty:
        st.metric("Máximo histórico", f"{filtered_data['Valor'].max()} {unidad}")
with col3:
    if not filtered_data.empty:
        st.metric("Mínimo histórico", f"{filtered_data['Valor'].min()} {unidad}")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📈 Evolución Temporal", 
    "📊 Comparación por Semestre", 
    "🔍 Indicadores Porcentuales"
])

with tab1:
    st.subheader("Evolución Temporal")
    if not filtered_data.empty:
        df_plot = filtered_data[['Año_Semestre', 'Valor']].set_index('Año_Semestre').sort_index()
        st.line_chart(df_plot)
    else:
        st.warning("No hay datos disponibles.")

with tab2:
    st.subheader("Comparación por Semestre")
    if not filtered_data.empty:
        df_bar = filtered_data.pivot_table(
            index='Año',
            columns='Semestre',
            values='Valor'
        ).fillna(0)
        st.bar_chart(df_bar)
    else:
        st.warning("No hay datos disponibles.")

with tab3:
    st.subheader("Indicadores Porcentuales")
    percent_data = data[data['Unidad'] == '%']
    if not percent_data.empty:
        indicadores_seleccionados = st.multiselect(
            "Seleccione indicadores:",
            percent_data['Indicador'].unique(),
            default=percent_data['Indicador'].unique()[:3]
        )
        if indicadores_seleccionados:
            df_percent = percent_data[percent_data['Indicador'].isin(indicadores_seleccionados)]
            df_pivot = df_percent.pivot_table(
                index='Año_Semestre',
                columns='Indicador',
                values='Valor'
            ).sort_index()
            st.line_chart(df_pivot)
            st.dataframe(df_pivot.T.round(1))
        else:
            st.info("Seleccione al menos un indicador.")
    else:
        st.warning("No hay indicadores porcentuales disponibles.")

# Footer
st.markdown("---")
st.caption("Dashboard creado con Streamlit | Datos actualizados a Marzo 2024")
