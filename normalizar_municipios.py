import pandas as pd
import unicodedata

def limpiar_texto(texto):
    #########################################################
    # Diccionario de equivalencias de municipios/ciudades   #
    # Agrega aquí todas las variantes que encuentres         #
    #########################################################
    EQUIVALENCIAS_MUNICIPIOS = {
        'SANTIAGO DE CALI': 'CALI',
        'CALI, VALLE': 'CALI',
        'CALI': 'CALI',
        # Agrega más variantes aquí
    }

    if pd.isnull(texto):
        return ''
    texto = str(texto).strip().upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    return texto

# Cargar muestra de datos (ajusta el nombre del archivo si es necesario)
df_muestra = pd.read_csv('muestras_db/demandante_muestra.csv')

# Cargar referencia DIVIPOLA (DANE)
df_divipola = pd.read_csv('DATOS_GUBERNAMENTALES/DIVIPOLA_CentrosPoblados.csv', sep=';', encoding='latin1')


# Limpiar nombres en ambas fuentes
df_muestra['nombres_limpio'] = df_muestra['nombres'].apply(limpiar_texto)
df_muestra['municipio_equivalente'] = df_muestra['nombres_limpio'].map(EQUIVALENCIAS_MUNICIPIOS).fillna(df_muestra['nombres_limpio'])
df_divipola['Nombre_Municipio_limpio'] = df_divipola['Nombre_Municipio'].apply(limpiar_texto)


# Hacer merge para obtener el código DANE del municipio usando el campo equivalente
resultado = pd.merge(
    df_muestra,
    df_divipola,
    left_on='municipio_equivalente',
    right_on='Nombre_Municipio_limpio',
    how='left'
)

# Guardar resultado
resultado.to_csv('muestras_db/demandante_muestra_normalizada.csv', index=False)

print('Normalización de municipios completada. Revisa muestras_db/demandante_muestra_normalizada.csv')
