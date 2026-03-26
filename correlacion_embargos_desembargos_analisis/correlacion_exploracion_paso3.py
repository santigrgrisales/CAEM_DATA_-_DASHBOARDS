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
    
    # Confirmar tipos con tipo_documento
    print("=== TIPOS EMBARGO con descripciones ===")
    cur.execute("""
        SELECT DISTINCT tipo_embargo, tipo_documento 
        FROM embargos 
        WHERE tipo_embargo IS NOT NULL 
        ORDER BY tipo_embargo
    """)
    for row in cur.fetchall():
        print(row)
    
    # Prueba JOIN via secondary_id: des -> original embargo
    print("\n=== PASO 3: CORRELACIÓN VIA secondary_id (muestra parejas) ===")
    cur.execute("""
        SELECT des.id as des_id, des.tipo_documento as des_tipo, des.secondary_id,
               emb.id as emb_id, emb.tipo_documento as emb_tipo,
               des.entidad_remitente, des.fecha_oficio
        FROM embargos des 
        JOIN embargos emb ON CAST(des.secondary_id AS UNSIGNED) = emb.id
        WHERE des.tipo_documento = 'DESEMBARGO' 
          AND emb.tipo_documento = 'EMBARGO'
          AND des.secondary_id IS NOT NULL
          AND des.secondary_id != ''
        ORDER BY des.create_at DESC 
        LIMIT 10
    """)
    pares = cur.fetchall()
    for row in pares:
        print(row)
    
    # Conteo total parejas
    print(f"\nTotal parejas encontradas: {len(pares)} en muestra LIMIT 10")
    cur.execute("""
        SELECT COUNT(*) 
        FROM embargos des 
        JOIN embargos emb ON CAST(des.secondary_id AS UNSIGNED) = emb.id
        WHERE des.tipo_documento = 'DESEMBARGO' 
          AND emb.tipo_documento = 'EMBARGO'
          AND des.secondary_id IS NOT NULL
    """)
    total = cur.fetchone()[0]
    print(f"Total estimado de parejas embargo-desembargo via secondary_id: {total}")
    
    conn.close()
    print("\nAnálisis completado.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
