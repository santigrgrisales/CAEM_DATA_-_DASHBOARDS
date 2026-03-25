import pymysql
import pandas as pd

# Configuración de conexión
conn = pymysql.connect(
    host='127.0.0.1',
    port=3307,
    user='producto',
    password=')VZ)aLY<R}V{pC2%',
    database='pyc_embargos'
)

# Obtener nombres de tablas
with conn.cursor() as cursor:
    cursor.execute("SHOW TABLES;")
    tablas = [row[0] for row in cursor.fetchall()]

# Obtener columnas de cada tabla
tablas_columnas = []
for tabla in tablas:
    with conn.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM `{tabla}`;")
        columnas = [row[0] for row in cursor.fetchall()]
        for columna in columnas:
            tablas_columnas.append({'tabla': tabla, 'columna': columna})

# Guardar resultado en un archivo CSV
pd.DataFrame(tablas_columnas).to_csv('tablas_columnas_pyc_embargos.csv', index=False)

print('Archivo tablas_columnas_pyc_embargos.csv generado.')
