import pandas as pd

# Archivos de entrada
CSV_REMITENTES = 'entidades_remitente_normalizadas_unicas.csv'
CSV_UNIVERSO = 'dim_entidades_unificado.csv'
CSV_SALIDA = 'reporte_cruce_remitentes_vs_universo.csv'

print('Leyendo remitentes...')
rem = pd.read_csv(CSV_REMITENTES, dtype=str)
rem = rem.rename(columns=lambda x: x.strip())
if 'nombre_normalizado' not in rem.columns:
    rem.columns = ['nombre_normalizado']
rem = rem[rem['nombre_normalizado'].notnull() & (rem['nombre_normalizado'].str.strip() != '')]

print('Leyendo universo de entidades...')
uni = pd.read_csv(CSV_UNIVERSO, dtype=str)
uni = uni.rename(columns=lambda x: x.strip())

# Cruce left join
print('Realizando cruce...')
cruce = rem.merge(uni, on='nombre_normalizado', how='left', suffixes=('', '_uni'))
cruce['match'] = cruce['nombre_oficial'].notnull()

# Reordenar columnas para claridad
cols = ['nombre_normalizado','match','nombre_oficial','tipo','fuente','municipio','departamento','sector','estado']
cruce = cruce[cols]

print(f'Total remitentes: {len(rem)}')
print(f'Coincidencias exactas: {cruce["match"].sum()}')
print(f'Sin match: {len(cruce) - cruce["match"].sum()}')

print(f'Guardando reporte: {CSV_SALIDA}')
cruce.to_csv(CSV_SALIDA, index=False, encoding='utf-8')
print('Proceso completado.')
