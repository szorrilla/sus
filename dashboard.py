import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    
    # Limpiar datos
    df.columns = ['Indicador', 'Unidad', 'Frecuencia', 
                 '2022_1', '2022_2', '2023_1', '2023_2', 
                 '2024_1', '2024_2', '2025_1', '2025_2']
    
    # Reestructurar datos
    melted_df = df.melt(
        id_vars=['Indicador', 'Unidad', 'Frecuencia'], 
        var_name='Periodo', 
        value_name='Valor'
    ).dropna()
    
    # Separar año y semestre
    melted_df[['Año', 'Semestre']] = melted_df['Periodo'].str.split('_', expand=True)
    melted_df['Semestre'] = melted_df['Semestre'].replace({'1': '1er Semestre', '2': '2do Semestre'})
    melted_df['Año_Semestre'] = melted_df['Año'] + ' ' + melted_df['Semestre']
    
    return melted_df

# Cargar datos
data = load_data()

# Título del dashboard
st.title("🌱 Dashboard de Indicadores de Sostenibilidad")
st.markdown("---")

# Sidebar para filtros
with st.sidebar:
    st.header("Filtros")
    
    indicador_seleccionado = st.selectbox(
        "Seleccione un indicador:",
        options=data['Indicador'].unique(),
        index=0
    )
    
    años_disponibles = data['Año'].unique()
    años_seleccionados = st.multiselect(
        "Seleccione años:",
        options=años_disponibles,
        default=años_disponibles
    )
    
    semestres_seleccionados = st.multiselect(
        "Seleccione semestres:",
        options=['1er Semestre', '2do Semestre'],
        default=['1er Semestre', '2do Semestre']
    )

# Filtrar datos
filtered_data = data[
    (data['Indicador'] == indicador_seleccionado) &
    (data['Año'].isin(años_seleccionados)) &
    (data['Semestre'].isin(semestres_seleccionados))
]

# Mostrar KPI principal
st.subheader(f"Indicador: {indicador_seleccionado}")
unidad = filtered_data['Unidad'].iloc[0] if not filtered_data.empty else ""

# Métricas
col1, col2, col3 = st.columns(3)
with col1:
    if not filtered_data.empty:
        st.metric(
            label=f"Último valor ({filtered_data.iloc[-1]['Año_Semestre']})",
            value=f"{filtered_data.iloc[-1]['Valor']} {unidad}"
        )
with col2:
    if not filtered_data.empty:
        st.metric(
            label="Valor máximo histórico",
            value=f"{filtered_data['Valor'].max()} {unidad}"
        )
with col3:
    if not filtered_data.empty:
        st.metric(
            label="Valor mínimo histórico",
            value=f"{filtered_data['Valor'].min()} {unidad}"
        )

# Gráficos principales - Ahora solo 3 pestañas
tab1, tab2, tab3 = st.tabs([
    "📈 Evolución Temporal", 
    "📊 Comparación por Semestre", 
    "🔍 Todos los Porcentuales"
])

with tab1:
    st.subheader("Evolución Temporal")
    if not filtered_data.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=filtered_data['Año_Semestre'],
            y=filtered_data['Valor'],
            mode='lines+markers+text',
            line=dict(width=4, shape='spline', smoothing=1.3),
            marker=dict(size=10, color='#636EFA'),
            text=filtered_data['Valor'].round(1),
            textposition="top center",
            name=indicador_seleccionado,
            hovertemplate="<b>%{x}</b><br>Valor: %{y:.1f}%<extra></extra>"
        ))
        
        fig.update_layout(
            title=f"Evolución de {indicador_seleccionado}",
            xaxis_title="Periodo",
            yaxis_title=unidad,
            hovermode="x unified",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

with tab2:
    st.subheader("Comparación por Semestre")
    if not filtered_data.empty:
        fig = px.bar(
            filtered_data,
            x='Año',
            y='Valor',
            color='Semestre',
            barmode='group',
            labels={'Valor': unidad},
            title=f"Comparación semestral de {indicador_seleccionado}"
        )
        
        fig.update_traces(
            marker_line_width=1.5,
            opacity=0.8,
            texttemplate='%{y:.1f}',
            textposition='outside'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados")

with tab3:
    st.subheader("Visualización Mejorada de Indicadores Porcentuales")
    
    percent_data = data[data['Unidad'] == '%']
    
    if not percent_data.empty:
        # Gráfico de líneas con selectores
        st.markdown("### Evolución de Indicadores Porcentuales")
        
        # Selector de indicadores porcentuales
        indicadores_seleccionados = st.multiselect(
            "Seleccione indicadores a visualizar:",
            options=percent_data['Indicador'].unique(),
            default=percent_data['Indicador'].unique()[:3]  # Muestra primeros 3 por defecto
        )
        
        if indicadores_seleccionados:
            fig = go.Figure()
            
            for indicador in indicadores_seleccionados:
                df_indicador = percent_data[percent_data['Indicador'] == indicador]
                
                fig.add_trace(go.Scatter(
                    x=df_indicador['Año_Semestre'],
                    y=df_indicador['Valor'],
                    mode='lines+markers',
                    name=indicador,
                    line=dict(width=3, shape='spline', smoothing=1.3),
                    marker=dict(size=8),
                    hovertemplate="<b>%{fullData.name}</b><br>Periodo: %{x}<br>Valor: %{y:.1f}%<extra></extra>"
                ))
            
            fig.update_layout(
                title="Comparación de Indicadores Porcentuales",
                xaxis_title="Periodo",
                yaxis_title="Porcentaje (%)",
                hovermode="x unified",
                height=600,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla resumen
            st.markdown("### Tabla Resumen de Valores")
            pivot_table = percent_data.pivot_table(
                index='Indicador',
                columns='Año_Semestre',
                values='Valor'
            ).round(1)
            
            # Filtrar solo los indicadores seleccionados
            pivot_table = pivot_table.loc[indicadores_seleccionados]
            
            st.dataframe(
                pivot_table.style
                .background_gradient(cmap='Blues', axis=1)
                .format("{:.1f}%"),
                use_container_width=True
            )
        else:
            st.warning("Seleccione al menos un indicador para visualizar")
    else:
        st.warning("No hay indicadores porcentuales disponibles")

# Notas al pie
st.markdown("---")
st.caption("Dashboard creado con Streamlit | Datos actualizados a Marzo 2024")