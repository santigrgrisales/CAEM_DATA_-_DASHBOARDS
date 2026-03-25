# Criterios de Normalización de Datos CAEM

## 1. Ciudades (Códigos DANE)
- Usar el archivo DIVIPOLA_CentrosPoblados.csv como referencia oficial.
- Normalizar los nombres de ciudades/municipios usando el Código DANE (Código_Municipio y/o Código_Entidad).
- Estandarizar nombres: mayúsculas, sin tildes, sin espacios extra.

## 2. Entidades Públicas y Despachos
- Usar los archivos GOV.CO_Universo_de_entidades_20260325.csv y Directorio_Judicial_Despachos_20260325_111213.csv.
- Estandarizar nombres y códigos oficiales.
- Unificar formato: mayúsculas, sin tildes, sin espacios extra.

## 3. Bancos y Entidades Financieras
- Usar ListageneraldeentidadesvigiladasporlaSuperintendenciaFinancieradeColombia.csv.
- Normalizar bancos usando NIT y nombre oficial.
- Estandarizar formato: mayúsculas, sin tildes, sin espacios extra.

## 4. Estandarización de Formatos Generales
- Unificar mayúsculas/minúsculas.
- Eliminar tildes y caracteres especiales.
- Quitar espacios extra al inicio/final.
- Tratar duplicados por nombre y/o código.

## 5. Documentación
- Documentar cada decisión y transformación aplicada.
- Mantener este archivo actualizado con los criterios y cambios realizados.
