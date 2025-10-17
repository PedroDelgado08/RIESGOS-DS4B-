# 1. LIBRERÍAS
import numpy as np
import pandas as pd
import pickle
import os

from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, Binarizer, MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import make_column_transformer


# 4. FUNCIONES DE SOPORTE
def calidad_datos(temp):
    temp['antigüedad_empleo'] = temp['antigüedad_empleo'].fillna('desconocido')
    for column in temp.select_dtypes('number').columns:
        temp[column] = temp[column].fillna(0)
    return temp


def creacion_variables(df):
    temp = df.copy()
    temp.vivienda = temp.vivienda.replace(['ANY', 'NONE', 'OTHER'], 'MORTGAGE')
    temp.finalidad = temp.finalidad.replace(['wedding', 'educational', 'renewable_energy'], 'otros')
    return temp


def ejecutar_modelos(df):
    # 5. CALIDAD Y CREACIÓN DE VARIABLES
    x_pd = creacion_variables(calidad_datos(df))
    x_ead = creacion_variables(calidad_datos(df))
    x_lgd = creacion_variables(calidad_datos(df))

    # 6. CARGA DE PIPES DE EJECUCIÓN
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(dir_path, 'pipe_ejecucion_pd.pickle'), 'rb') as file:
        pipe_ejecucion_pd = pickle.load(file)

    with open(os.path.join(dir_path, 'pipe_ejecucion_ead.pickle'), 'rb') as file:
        pipe_ejecucion_ead = pickle.load(file)

    with open(os.path.join(dir_path, 'pipe_ejecucion_lgd.pickle'), 'rb') as file:
        pipe_ejecucion_lgd = pickle.load(file)

    # 7. EJECUCIÓN
    scoring_pd = pipe_ejecucion_pd.predict_proba(x_pd)[:, 1]
    ead = pipe_ejecucion_ead.predict(x_ead)
    lgd = pipe_ejecucion_lgd.predict(x_lgd)

    # 8. RESULTADO
    principal = x_pd.principal
    EL = pd.DataFrame({
        'principal': principal,
        'pd': scoring_pd,
        'ead': ead,
        'lgd': lgd
    })

    EL['perdida_esperada'] = round(EL.pd * EL.principal * EL.ead * EL.lgd, 2)

    return EL
