import pandas as pd
from sqlalchemy import create_engine
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

# Tablas/campos clave a extraer
queries = {
    'entidad_bancaria': 'SELECT * FROM entidad_bancaria',
    'datos_entidad': 'SELECT * FROM datos_entidad',
    'embargos': 'SELECT id, ciudad, entidad_remitente, entidad_bancaria_id, fecha_banco, tipo_embargo, monto, demandado_id FROM embargos',
}

for name, query in queries.items():
    print(f"Extrayendo {name}...")
    try:
        df = pd.read_sql(query, engine)
        df.to_csv(os.path.join(OUTPUT_DIR, f"{name}_completo.csv"), index=False)
        print(f"Guardado: {name}_completo.csv")
    except Exception as e:
        print(f"Error extrayendo {name}: {e}")

print("\nListo. Revisa la carpeta 'muestras_db' para los archivos CSV completos.")
