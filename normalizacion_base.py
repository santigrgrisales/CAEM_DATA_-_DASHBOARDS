import pandas as pd
import unidecode
import os

# Cargar datos extraídos
DIR = 'muestras_db'

# 1. Normalización de bancos (entidad_bancaria)
bancos = pd.read_csv(os.path.join(DIR, 'entidad_bancaria_completo.csv'))
def limpiar_nombre(nombre):
    if pd.isnull(nombre):
        return ''
    return unidecode.unidecode(str(nombre)).strip().upper()
bancos['nombre_normalizado'] = bancos['nombre'].apply(limpiar_nombre)
# Aquí deberás asociar manualmente el código Superfinanciera (puedes agregar una columna 'codigo_superfinanciera')

# 2. Normalización de entidades (datos_entidad)
entidades = pd.read_csv(os.path.join(DIR, 'datos_entidad_completo.csv'))
entidades['nombres_normalizado'] = entidades['nombres'].apply(limpiar_nombre)
entidades['identificacion'] = entidades['identificacion'].astype(str).str.strip()
# Elimina duplicados por identificacion y nombre
entidades = entidades.drop_duplicates(subset=['identificacion','nombres_normalizado'])

# 3. Normalización de ciudades (de embargos)
# NOTA: El archivo embargos_completo.csv no se generó por error de columna. Debes revisar los campos disponibles y ajustar el script de extracción.
# Cuando tengas el archivo, puedes hacer:
# embargos = pd.read_csv(os.path.join(DIR, 'embargos_completo.csv'))
# embargos['ciudad_normalizada'] = embargos['ciudad'].apply(limpiar_nombre)
# Aquí deberás mapear a código DANE usando un catálogo externo

# Guardar resultados intermedios
bancos.to_csv(os.path.join(DIR, 'entidad_bancaria_normalizada.csv'), index=False)
entidades.to_csv(os.path.join(DIR, 'datos_entidad_normalizada.csv'), index=False)

print('Normalización básica de bancos y entidades completada. Revisa los archivos *_normalizada.csv.')
