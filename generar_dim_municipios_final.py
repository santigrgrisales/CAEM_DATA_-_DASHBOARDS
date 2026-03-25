import pandas as pd
import unicodedata

def limpiar_texto(texto):
    if pd.isnull(texto):
        return ''
    texto = str(texto).strip().upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    texto = ' '.join(texto.split())  # Normaliza espacios múltiples
    return texto

# Leer DIVIPOLA
ruta_divipola = 'DATOS_GUBERNAMENTALES/DIVIPOLA_CentrosPoblados.csv'
df = pd.read_csv(ruta_divipola, sep=';', encoding='latin1')

# Filtrar solo municipios cabecera (CM)
if 'Tipo' in df.columns:
    df = df[df['Tipo'].str.upper().str.strip() == 'CM']

# Limpiar y estandarizar nombres
for col in ['Nombre_Municipio', 'Nombre_Departamento']:
    if col in df.columns:
        df[col + '_limpio'] = df[col].apply(limpiar_texto)
    else:
        df[col + '_limpio'] = ''

# Generar columna nombre_normalizado
if 'Nombre_Municipio' in df.columns:
    df['nombre_normalizado'] = df['Nombre_Municipio'].apply(limpiar_texto)
else:
    df['nombre_normalizado'] = ''

# Seleccionar y renombrar columnas clave
salida = df[['Código_Municipio', 'Nombre_Municipio', 'Nombre_Departamento', 'nombre_normalizado']].copy()
salida = salida.rename(columns={
    'Código_Municipio': 'codigo_dane',
    'Nombre_Municipio': 'nombre',
    'Nombre_Departamento': 'departamento'
})

# Quitar duplicados por código DANE
salida = salida.drop_duplicates(subset=['codigo_dane'])

# Guardar resultado para revisión
salida.to_csv('dim_municipios_final.csv', index=False, encoding='utf-8')
print('Archivo dim_municipios_final.csv generado. Revisa el archivo antes de insertar en la base de datos.')
