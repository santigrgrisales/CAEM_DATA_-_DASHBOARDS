import pandas as pd
import pymysql

# Configuración de conexión a la base de datos destino (caem_clean)
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'producto',
    'password': ')VZ)aLY<R}V{pC2%',
    'database': 'caem_clean',
    'charset': 'utf8mb4'
}

# Ruta al archivo CSV generado
CSV_PATH = 'dim_municipios_final.csv'

# Nombre de la tabla destino
TABLE_NAME = 'dim_municipios'

# Leer el CSV
print('Leyendo archivo CSV...')
df = pd.read_csv(CSV_PATH, dtype=str)

# Conectar a la base de datos
print('Conectando a la base de datos...')
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# Insertar fila por fila (puedes optimizar con executemany si es necesario)
insert_sql = f"""
INSERT INTO {TABLE_NAME} (codigo_dane, nombre, departamento, nombre_normalizado)
VALUES (%s, %s, %s, %s)
"""

print('Insertando registros...')
for idx, row in df.iterrows():
    cursor.execute(insert_sql, (
        row['codigo_dane'],
        row['nombre'],
        row['departamento'],
        row['nombre_normalizado']
    ))

conn.commit()
print(f'Se insertaron {len(df)} registros en {TABLE_NAME}.')
cursor.close()
conn.close()
print('Proceso completado.')
