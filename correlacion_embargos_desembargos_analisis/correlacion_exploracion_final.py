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
    
    # Conteo rápido sin JOIN pesado
    print("=== CONTEO DESEMBARGOS con secondary_id ===")
    cur.execute("""
        SELECT tipo_documento, COUNT(*) 
        FROM embargos 
        WHERE secondary_id IS NOT NULL AND secondary_id != '' AND tipo_documento = 'DESEMBARGO'
        GROUP BY tipo_documento
    """)
    for row in cur.fetchall():
        print(row)
    
    # Muestra reciente DESEMBARGO con secondary_id
    print("\n=== MUESTRA RECIENTES DESEMBARGOS con secondary_id ===")
    cur.execute("""
        SELECT id, tipo_embargo, tipo_documento, secondary_id, referencia, radicado_banco, 
               create_at, entidad_remitente
        FROM embargos 
        WHERE tipo_documento = 'DESEMBARGO' 
          AND secondary_id IS NOT NULL AND secondary_id != ''
        ORDER BY id DESC 
        LIMIT 10
    """)
    des = cur.fetchall()
    for row in des:
        print(row)
    
    # Test JOIN solo para 3 muestras explícitas (evitar heavy)
    print("\n=== TEST JOIN PARA MUESTRAS ESPECÍFICAS ===")
    for d_row in des[:3]:
        des_id, _, _, sec_id, _, _, _, _ = d_row
        cur.execute("""
            SELECT id, tipo_documento, create_at FROM embargos 
            WHERE id = %s OR secondary_id = %s LIMIT 1
        """, (sec_id, sec_id))
        orig = cur.fetchone()
        print(f"Des {des_id} (sec={sec_id}) -> Original: {orig}")
    
    conn.close()
    print("\nFinalizado.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
