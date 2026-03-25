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

# Filtrar solo municipios (no centros poblados)
# Suponiendo que el campo Tipo indica 'CM' para municipio cabecera
if 'Tipo' in df.columns:
    df = df[df['Tipo'].str.upper().str.strip() == 'CM']
else:
    df = df[df['Tipo'].str.upper().str.strip() == 'CM']  # Ajusta si el campo tiene otro nombre

# Limpiar y estandarizar nombres
for col in ['Nombre_Municipio', 'Nombre_Departamento']:
    if col in df.columns:
        df[col + '_limpio'] = df[col].apply(limpiar_texto)
    else:
        df[col + '_limpio'] = ''

# Seleccionar y renombrar columnas clave
salida = df[['Código_Municipio', 'Nombre_Municipio_limpio', 'Nombre_Departamento_limpio']].copy()
salida = salida.rename(columns={
    'Código_Municipio': 'codigo_dane',
    'Nombre_Municipio_limpio': 'nombre',
    'Nombre_Departamento_limpio': 'departamento'
})

# Quitar duplicados por código DANE
salida = salida.drop_duplicates(subset=['codigo_dane'])

# Guardar resultado para revisión
salida.to_csv('dim_municipios.csv', index=False, encoding='utf-8')
print('Archivo dim_municipios.csv generado. Revisa el archivo antes de insertar en la base de datos.')
