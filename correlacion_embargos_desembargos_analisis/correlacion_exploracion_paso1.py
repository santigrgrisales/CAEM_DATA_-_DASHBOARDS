import pymysql
import sys

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3307,
        user='producto',
        password=')VZ)aLY<R}V{pC2%',
        db='pyc_embargos',
        charset='utf8mb4'
    )
    cur = conn.cursor()
    
    # Paso 1: Identificación de tipos embargo/desembargo
    cur.execute("SELECT id, tipo FROM tipo_embargo ORDER BY id;")
    tipos = cur.fetchall()
    print("=== PASO 1: TIPOS DE EMBARGO ===")
    for row in tipos:
        print(f"ID: {row[0]}, Tipo: {row[1]}")
    
    conn.close()
    print("\nConexión exitosa y consulta completada.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
