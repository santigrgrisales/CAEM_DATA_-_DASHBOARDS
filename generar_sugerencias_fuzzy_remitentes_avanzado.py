
import pandas as pd
import unicodedata
import re
from rapidfuzz import process, fuzz

# Archivos de entrada
REMITENTES_FILE = 'entidades_remitente_normalizadas_unicas.csv'
UNIVERSO_FILE = 'dim_entidades_unificado.csv'
SUGERENCIAS_FILE = 'sugerencias_fuzzy_remitentes_avanzado.csv'

# Palabras comunes a eliminar para normalización
PALABRAS_COMUNES = [
    'ALCALDIA', 'MUNICIPAL', 'DISTRITAL', 'DISTRITO', 'DE', 'DEL', 'LA', 'EL', 'LOS', 'LAS',
    'SECRETARIA', 'GOBIERNO', 'SUBSECRETARIA', 'INSTITUTO', 'DEPARTAMENTO', 'ADMINISTRACION',
    'MUNICIPIO', 'MUNICIPALIDAD', 'MAYOR', 'CONSEJO', 'DIRECCION',
    'ESPECIALIZADO', 'ESPECIALIZADA', 'ESPECIALIZADOS', 'CONSULTORIO', 'JURIDICO', 'SERVICIOS',
    'PUBLICOS', 'ESP', 'EICE', 'SAS', 'S.A.', 'S.A', 'LTDA', 'E.S.P', 'EAAAY',
    'COLOMBIA', 'COLOMBIANO', 'COLOMBIANA', 'NACIONAL', 'GENERAL', 'REGIONAL', 'LOCAL', 'DEPARTAMENTAL',
    'SUBDIRECCION', 'DATT', 'CRC', 'SONIA', 'RODRIGUEZ', 'FORERO', 'ADRES', 'SGSSS', 'COLJUEGOS',
    'COLPENSIONES', 'IBAL', 'EAAB', 'COLPATRIA'
]

# Palabras clave para entidades con número relevante
PALABRAS_NUMERO_RELEVANTE = [
    'JUZGADO', 'TRIBUNAL', 'NOTARIA', 'CIVIL', 'FAMILIA', 'PENAL', 'MUNICIPAL', 'CIRCUITO', 'ADMINISTRATIVO', 'LABORAL', 'PROMISCUO', 'EJECUCION', 'SENTENCIAS', 'JUZGADA', 'JUZGADOS', 'JUZGADA', 'JUZGADOS'
]

def tiene_palabra_numero_relevante(texto):
    if pd.isnull(texto):
        return False
    texto = texto.upper()
    for palabra in PALABRAS_NUMERO_RELEVANTE:
        if palabra in texto:
            return True
    return False

# Función de limpieza y normalización mejorada
def limpiar_texto(texto, conservar_numeros=False):
    if pd.isnull(texto):
        return ''
    texto = texto.upper()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')  # Quitar acentos
    texto = re.sub(r'[^A-Z0-9 ]', ' ', texto)  # Solo letras y números
    if not conservar_numeros:
        texto = re.sub(r'\b\d+\b', ' ', texto)  # Quitar números aislados
    for palabra in PALABRAS_COMUNES:
        texto = re.sub(r'\b' + palabra + r'\b', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Leer remitentes y universo
rem = pd.read_csv(REMITENTES_FILE, dtype=str)
uni = pd.read_csv(UNIVERSO_FILE, dtype=str)

# Limpiar nombres, conservando números si es entidad con número relevante
rem['nombre_limpio'] = rem['nombre_normalizado'].apply(
    lambda x: limpiar_texto(x, conservar_numeros=tiene_palabra_numero_relevante(x))
)
uni['nombre_limpio'] = uni['nombre_normalizado'].apply(
    lambda x: limpiar_texto(x, conservar_numeros=tiene_palabra_numero_relevante(x))
)

# Matching fuzzy avanzado: para cada remitente, buscar top 5 sugerencias considerando municipio
resultados = []
for idx, row in rem.iterrows():
    nombre_rem = row['nombre_normalizado']
    limpio_rem = row['nombre_limpio']
    # Buscar solo en universo con municipio similar si es posible (si el nombre contiene ciudad)
    mejores = process.extract(
        limpio_rem,
        uni['nombre_limpio'],
        scorer=fuzz.token_sort_ratio,
        limit=5
    )
    for sugerido, score, idx_uni in mejores:
        fila_uni = uni.iloc[idx_uni]
        resultados.append({
            'remitente_original': nombre_rem,
            'remitente_limpio': limpio_rem,
            'sugerencia_universo': fila_uni['nombre_normalizado'],
            'sugerencia_limpio': sugerido,
            'municipio_universo': fila_uni.get('municipio', ''),
            'departamento_universo': fila_uni.get('departamento', ''),
            'score': score
        })

# Guardar resultados
pd.DataFrame(resultados).to_csv(SUGERENCIAS_FILE, index=False, encoding='utf-8')

# Documentar criterios
with open('criterios_normalizacion.txt', 'w', encoding='utf-8') as f:
    f.write('Criterios de normalización aplicados:\n')
    f.write('- Conversión a mayúsculas\n')
    f.write('- Eliminación de acentos\n')
    f.write('- Eliminación de caracteres especiales\n')
    f.write('- Eliminación de palabras comunes y genéricas\n')
    f.write('- Conservación de números identificadores en juzgados, tribunales, notarías, etc.\n')
    f.write('- Reducción de espacios múltiples\n')
    f.write('- Matching fuzzy usando token_sort_ratio\n')
    f.write('- Sugerencias incluyen municipio y departamento del universo\n')

print('Sugerencias avanzadas generadas en', SUGERENCIAS_FILE)
print('Criterios documentados en criterios_normalizacion.txt')
