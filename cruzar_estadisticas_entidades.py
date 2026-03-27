import pandas as pd
from fuzzywuzzy import fuzz, process

# Cargar data oficial (dim_entidades_unificado.csv)
df_oficial = pd.read_csv('dim_entidades_unificado.csv')

# Cargar data cruda (entidades_remitente_normalizadas_unicas.csv)
df_cruda = pd.read_csv('entidades_remitente_normalizadas_unicas.csv')

# Normalizar columnas relevantes
df_oficial['nombre_normalizado'] = df_oficial['nombre_normalizado'].astype(str).str.strip().str.upper()
df_cruda['nombre_normalizado'] = df_cruda['nombre_normalizado'].astype(str).str.strip().str.upper()

# Estadísticas básicas
stats = {}
stats['total_cruda'] = len(df_cruda)
stats['total_cruda_unicos'] = df_cruda['nombre_normalizado'].nunique()
stats['total_oficial'] = len(df_oficial)
stats['total_oficial_unicos'] = df_oficial['nombre_normalizado'].nunique()

# Coincidencias exactas
cruce = df_cruda['nombre_normalizado'].isin(df_oficial['nombre_normalizado'])
stats['coincidencias_exactas'] = cruce.sum()
stats['no_coincidencias'] = (~cruce).sum()

# Ejemplos de no coincidencias
no_coincidentes = df_cruda.loc[~cruce, 'nombre_normalizado'].unique()[:20]

# Duplicados en cruda y oficial
stats['duplicados_cruda'] = df_cruda['nombre_normalizado'].duplicated().sum()
stats['duplicados_oficial'] = df_oficial['nombre_normalizado'].duplicated().sum()

# Sugerencias fuzzy para los primeros 10 no coincidentes
fuzzy_matches = []
for nombre in no_coincidentes[:10]:
    result = process.extractOne(nombre, df_oficial['nombre_normalizado'], scorer=fuzz.token_sort_ratio)
    if result:
        match, score, _ = result
        fuzzy_matches.append({'crudo': nombre, 'oficial_sugerido': match, 'score': score})
    else:
        fuzzy_matches.append({'crudo': nombre, 'oficial_sugerido': None, 'score': None})

# Reporte
print('===== ESTADÍSTICAS DEL CRUCE =====')
for k, v in stats.items():
    print(f'{k}: {v}')
print('\nEjemplos de no coincidencias:')
for n in no_coincidentes:
    print('-', n)
print('\nSugerencias fuzzy para no coincidencias:')
for m in fuzzy_matches:
    print(f"Crudo: {m['crudo']} | Sugerido: {m['oficial_sugerido']} | Score: {m['score']}")

# Guardar reporte en Excel
with pd.ExcelWriter('reporte_estadisticas_cruce.xlsx') as writer:
    pd.DataFrame([stats]).to_excel(writer, sheet_name='estadisticas', index=False)
    pd.DataFrame({'no_coincidentes': no_coincidentes}).to_excel(writer, sheet_name='no_coincidentes', index=False)
    pd.DataFrame(fuzzy_matches).to_excel(writer, sheet_name='fuzzy_sugerencias', index=False)

print('\nReporte guardado en reporte_estadisticas_cruce.xlsx')
