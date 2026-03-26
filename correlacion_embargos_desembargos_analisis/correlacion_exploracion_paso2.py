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
    
    # Paso 2a: Verificar múltiples embargos por demandado (identificacion + expediente)
    print("=== PASO 2a: Múltiples EMBARGOS por IDENTIFICACION + EXPEDIENTE ===")
    cur.execute("""
        SELECT identificacion, expediente, 
               COUNT(DISTINCT embargo_id) as num_embargos,
               GROUP_CONCAT(DISTINCT tipo_embargo ORDER BY tipo_embargo) as tipos,
               COUNT(DISTINCT CASE WHEN tipo_embargo IN (2,3) THEN embargo_id END) as des_emb
        FROM demandado d 
        JOIN embargos e ON d.embargo_id = e.id 
        WHERE d.identificacion IS NOT NULL AND d.identificacion != '' 
          AND d.expediente IS NOT NULL AND d.expediente != ''
        GROUP BY identificacion, expediente 
        HAVING num_embargos > 1 
        ORDER BY num_embargos DESC 
        LIMIT 20
    """)
    for row in cur.fetchall():
        print(row)
    
    # Paso 2b: secondary_id en embargos tipo des
    print("\n=== PASO 2b: Uso de secondary_id por tipo_embargo (solo donde NOT NULL) ===")
    cur.execute("""
        SELECT tipo_embargo, tipo_documento, COUNT(*) as count_sec_id
        FROM embargos 
        WHERE secondary_id IS NOT NULL AND secondary_id != ''
        GROUP BY tipo_embargo, tipo_documento 
        ORDER BY count_sec_id DESC
    """)
    for row in cur.fetchall():
        print(row)
    
    # Paso 2c: Muestra embargos tipo 2/3 con campos de referencia
    print("\n=== PASO 2c: MUESTRA EMBARGOS TIPO 2/3 (campos correlación) ===")
    cur.execute("""
        SELECT id, tipo_embargo, tipo_documento, secondary_id, referencia, radicado_banco, 
               oficio, entidad_remitente, fecha_oficio, create_at
        FROM embargos 
        WHERE tipo_embargo IN (2,3) 
        ORDER BY create_at DESC 
        LIMIT 20
    """)
    for row in cur.fetchall():
        print(row)
    
    conn.close()
    print("\nPaso 2 completado.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
