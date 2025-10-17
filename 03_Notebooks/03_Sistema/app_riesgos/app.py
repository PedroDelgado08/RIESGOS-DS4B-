from codigoEjecucion import ejecutar_modelos
import streamlit as st
from streamlit_echarts import st_echarts
import os
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
dir_path = os.getcwd()  # Asegura compatibilidad en Streamlit Cloud
icon_path = os.path.join(dir_path, "DS4B_Logo_Blanco_Vertical_FB.png")
image_path = os.path.join(dir_path, "risk_score.jpg")

st.set_page_config(
    page_title='DS4B Risk Score Analyzer',
    page_icon=icon_path,
    layout='wide'
)

# SIDEBAR
with st.sidebar:
    try:
        st.image(image_path)
    except Exception as e:
        st.warning(f"No se pudo cargar la imagen: {e}")

    # INPUTS DE LA APLICACION
    principal = st.number_input('Importe Solicitado', 500, 50000)
    finalidad = st.selectbox('Finalidad Préstamo', ['debt_consolidation','credit_card','home_improvement','other'])
    num_cuotas = st.radio('Número Cuotas', ['36 months','60 months'])
    ingresos = st.slider('Ingresos anuales', 20000, 300000)

    # DATOS CONOCIDOS (fijos)
    ingresos_verificados = 'Verified'
    antigüedad_empleo = '10+ years'
    rating = 'B'
    dti = 28
    num_lineas_credito = 3
    porc_uso_revolving = 50
    tipo_interes = 7.26
    imp_cuota = 500
    num_derogatorios = 0
    vivienda = 'MORTGAGE'

# MAIN
st.title('DS4B RISK SCORE ANALYZER')

# CREAR EL REGISTRO
registro = pd.DataFrame({
    'ingresos_verificados': ingresos_verificados,
    'vivienda': vivienda,
    'finalidad': finalidad,
    'num_cuotas': num_cuotas,
    'antigüedad_empleo': antigüedad_empleo,
    'rating': rating,
    'ingresos': ingresos,
    'dti': dti,
    'num_lineas_credito': num_lineas_credito,
    'porc_uso_revolving': porc_uso_revolving,
    'principal': principal,
    'tipo_interes': tipo_interes,
    'imp_cuota': imp_cuota,
    'num_derogatorios': num_derogatorios
}, index=[0])

# CALCULAR RIESGO
if st.sidebar.button('CALCULAR RIESGO'):
    try:
        EL = ejecutar_modelos(registro)

        # KPIs
        kpi_pd = int(EL.pd.iloc[0] * 100)
        kpi_ead = int(EL.ead.iloc[0] * 100)
        kpi_lgd = int(EL.lgd.iloc[0] * 100)
        kpi_el = int(EL.perdida_esperada.iloc[0])

        # Velocímetros
        def crear_gauge(nombre, valor):
            return {
                "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
                "series": [{
                    "name": nombre,
                    "type": "gauge",
                    "axisLine": {"lineStyle": {"width": 10}},
                    "progress": {"show": True, "width": 10},
                    "detail": {"valueAnimation": True, "formatter": "{value}"},
                    "data": [{"value": valor, "name": nombre}]
                }]
            }

        col1, col2, col3 = st.columns(3)
        with col1:
            st_echarts(options=crear_gauge("PD", kpi_pd), width="110%", key="pd_gauge")
        with col2:
            st_echarts(options=crear_gauge("EAD", kpi_ead), width="110%", key="ead_gauge")
        with col3:
            st_echarts(options=crear_gauge("LGD", kpi_lgd), width="110%", key="lgd_gauge")

        # Prescripción
        col1, col2 = st.columns(2)
        with col1:
            st.write('La pérdida esperada es de (Euros):')
            st.metric(label="PÉRDIDA ESPERADA", value=kpi_el)
        with col2:
            st.write('Se recomienda un extratipo de (Euros):')
            st.metric(label="COMISIÓN A APLICAR", value=kpi_el * 3)

    except FileNotFoundError as e:
        st.error(str(e))
else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')
