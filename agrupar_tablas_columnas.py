import pandas as pd

df = pd.read_csv('tablas_columnas_pyc_embargos.csv')

with open('tablas_columnas_agrupadas.txt', 'w', encoding='utf-8') as f:
    for tabla, grupo in df.groupby('tabla'):
        f.write(f'Tabla: {tabla}\n')
        for columna in grupo['columna']:
            f.write(f'  - {columna}\n')
        f.write('\n')

print('Archivo tablas_columnas_agrupadas.txt generado.')
