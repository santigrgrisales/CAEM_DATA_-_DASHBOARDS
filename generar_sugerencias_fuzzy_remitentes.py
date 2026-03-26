import pandas as pd
from rapidfuzz import process, fuzz

# Archivos de entrada
REMITENTES_FILE = 'entidades_remitente_normalizadas_unicas.csv'
UNIVERSO_FILE = 'dim_entidades_unificado.csv'
REPORTE_CRUCE_FILE = 'reporte_cruce_remitentes_vs_universo.csv'

# Archivo de salida
SUGERENCIAS_FILE = 'sugerencias_fuzzy_remitentes.csv'


# Leer remitentes sin match exacto
df_cruce = pd.read_csv(REPORTE_CRUCE_FILE, dtype=str)
remitentes_no_match = df_cruce[df_cruce['match'].str.lower() == 'false']['nombre_normalizado'].dropna().unique()

# Leer universo de entidades
df_universo = pd.read_csv(UNIVERSO_FILE, dtype=str)

# Usar la columna normalizada para comparar
universo_nombres = df_universo['nombre_normalizado'].dropna().unique().tolist()

# Fuzzy matching: para cada remitente sin match, buscar top 5 sugerencias
data = []
for remitente in remitentes_no_match:
    matches = process.extract(
        remitente,
        universo_nombres,
        scorer=fuzz.token_sort_ratio,
        limit=5
    )
    for sugerido, score, _ in matches:
        data.append({
            'remitente_sin_match': remitente,
            'sugerencia_universo': sugerido,
            'score': score
        })

# Guardar resultados
df_sugerencias = pd.DataFrame(data)
df_sugerencias.to_csv(SUGERENCIAS_FILE, index=False, encoding='utf-8')

print(f"Archivo de sugerencias generado: {SUGERENCIAS_FILE}")
