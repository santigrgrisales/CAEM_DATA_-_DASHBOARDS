import pandas as pd
import mysql.connector
from mysql.connector import Error
from fuzzywuzzy import fuzz
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Config DB
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'producto',
    'password': ')VZ)aLY<R}V{pC2%',
    'database': 'pyc_embargos'
}

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Conexión exitosa a DB")
            return conn
    except Error as e:
        print(f"Error conexión: {e}")
        return None

def safe_query(conn, query, limit=1000):
    try:
        df = pd.read_sql_query(query, conn)
        print(f"Query OK: {len(df)} rows")
        return df
    except Error as e:
        print(f"Error query: {e}")
        return pd.DataFrame()

def analyze_counts(conn):
    query = """
    SELECT tipo_documento, COUNT(*) as count
    FROM embargos 
    WHERE tipo_documento IN ('EMBARGO', 'DESEMBARGO')
    GROUP BY tipo_documento
    """
    df = safe_query(conn, query)
    print("Counts:")
    print(df)
    return df

def sample_embargos(conn, tipo, limit=500):
    query = f"""
    SELECT id, tipo_documento, referencia, radicado_banco, oficio, fecha_oficio, 
           entidad_remitente, ciudad, monto, fecha_recibido, create_at
    FROM embargos 
    WHERE tipo_documento = '{tipo}'
    ORDER BY fecha_recibido DESC, create_at DESC
    LIMIT {limit}
    """
    df = safe_query(conn, query)
    return df

def load_sample_csv(path):
    try:
        df = pd.read_csv(path)
        print(f"Loaded {path}: {len(df)} rows")
        return df
    except:
        return pd.DataFrame()

def find_pairs(emb_df, des_df):
    pairs = []
    emb_dict = defaultdict(list)
    
    # Index embargos by cleaned referencia, entidad, ciudad
    for _, emb in emb_df.iterrows():
        key = (emb.get('referencia', '').strip().upper() or emb.get('radicado_banco', '').strip().upper() or emb.get('oficio', '').strip().upper(),
               emb.get('entidad_remitente', '').strip().upper(),
               emb.get('ciudad', '').strip().upper())
        emb_dict[key].append(emb)
    
    for _, des in des_df.iterrows():
        key = (des.get('referencia', '').strip().upper() or des.get('radicado_banco', '').strip().upper() or des.get('oficio', '').strip().upper(),
               des.get('entidad_remitente', '').strip().upper(),
               des.get('ciudad', '').strip().upper())
        if key in emb_dict:
            for emb in emb_dict[key]:
                if pd.to_datetime(des.get('fecha_oficio', pd.NaT)) > pd.to_datetime(emb.get('fecha_oficio', pd.NaT)):
                    score = 100  # Exact key match
                else:
                    score = fuzz.ratio(str(des.get('referencia', '')), str(emb.get('referencia', '')))
                pairs.append({
                    'embargo_id': emb['id'],
                    'desembargo_id': des['id'],
                    'referencia': key[0],
                    'entidad': key[1],
                    'ciudad': key[2],
                    'fecha_embargo': emb.get('fecha_oficio'),
                    'fecha_desembargo': des.get('fecha_oficio'),
                    'monto_embargo': emb.get('monto'),
                    'monto_desembargo': des.get('monto'),
                    'match_score': score,
                    'match_type': 'exact_key' if score == 100 else 'fuzzy_ref'
                })
    return pd.DataFrame(pairs)

def main():
    conn = connect_db()
    if not conn:
        return
    
    # Análisis
    print("1. Counts EMBARGO/DESEMBARGO")
    analyze_counts(conn)
    
    print("\n2. Sample EMBARGO recientes")
    emb_sample = sample_embargos(conn, 'EMBARGO')
    
    print("\n3. Sample DESEMBARGO recientes")
    des_sample = sample_embargos(conn, 'DESEMBARGO')
    
    # Load local samples
    emb_local_df = load_sample_csv('muestras_db/embargos_muestra.csv')
    des_local = emb_local_df[emb_local_df['tipo_documento'] == 'DESEMBARGO'] if len(emb_local_df)>0 and 'tipo_documento' in emb_local_df.columns else pd.DataFrame()
    emb_local = emb_local_df[emb_local_df['tipo_documento'] == 'EMBARGO'] if len(emb_local_df)>0 and 'tipo_documento' in emb_local_df.columns else pd.DataFrame()
    
    # Combina local + DB samples
    emb_all = pd.concat([emb_sample, emb_local], ignore_index=True).drop_duplicates(subset=['id'], keep='last').reset_index(drop=True) if not emb_sample.empty or not emb_local.empty else pd.DataFrame()
    des_all = pd.concat([des_sample, des_local], ignore_index=True).drop_duplicates(subset=['id'], keep='last').reset_index(drop=True) if not des_sample.empty or not des_local.empty else pd.DataFrame()
    
    print("\n4. Buscando pairs en samples...")
    pairs = find_pairs(emb_all, des_all)
    print(f"Found {len(pairs)} potential pairs")
    print(pairs.head(10))
    
    # Save
    emb_all.to_csv('embargo_sample.csv', index=False)
    des_all.to_csv('desembargo_sample.csv', index=False)
    pairs.to_csv('correlacion_pairs.csv', index=False)
    
    # Stats
    total_emb = len(emb_all)
    total_des = len(des_all)
    matched_emb = pairs['embargo_id'].nunique()
    matched_des = pairs['desembargo_id'].nunique()
    print(f"\nSTATS: Embargos: {total_emb}, Desembargos: {total_des}, Matched E: {matched_emb} ({matched_emb/total_emb*100:.1f}%), Matched D: {matched_des} ({matched_des/total_des*100:.1f}%)")
    
    # Close
    conn.close()
    print("\nFiles generados: embargo_sample.csv, desembargo_sample.csv, correlacion_pairs.csv")
    print("Hipótesis: Correlación primaria por referencia/oficio + entidad + ciudad + fecha orden. Alta tasa matches en samples.")

if __name__ == '__main__':
    main()

