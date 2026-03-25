import pandas as pd
from sqlalchemy import create_engine, inspect
import os

# Parámetros de conexión
USER = 'producto'
PASSWORD = ')VZ)aLY<R}V{pC2%'
HOST = '127.0.0.1'
PORT = '3307'
DB = 'pyc_embargos'

# Crear engine de SQLAlchemy (solo lectura)
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}")

# Carpeta de salida
OUTPUT_DIR = 'muestras_db'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Listar tablas
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tablas encontradas: {tables}")

# Extraer muestra de cada tabla
for table in tables:
    print(f"Extrayendo muestra de {table}...")
    try:
        df = pd.read_sql(f"SELECT * FROM `{table}` LIMIT 10", engine)
        df.to_csv(os.path.join(OUTPUT_DIR, f"{table}_muestra.csv"), index=False)
        print(f"Guardado: {table}_muestra.csv")
    except Exception as e:
        print(f"Error extrayendo {table}: {e}")

print("\nListo. Revisa la carpeta 'muestras_db' para los archivos CSV de muestra.")
