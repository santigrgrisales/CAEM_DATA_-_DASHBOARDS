# Dashboard Colpatria — Oficios de Embargo

Panel de control interactivo para analizar oficios de embargo/desembargo del portafolio Colpatria.

## Características

- **KPIs principales**: total de oficios, clasificación (embargo / desembargo / requerimiento), tipo (judicial / coactivo)
- **Gráficos interactivos**: barras, pie, treemap, tabla de variantes
- **Filtros combinados**: por clasificación, tipo, entidad, ciudad y rango de fechas
- **Normalización robusta**: +400 alias de ciudades, +50 reglas de entidades (diccionario exacto, sin falsos positivos)
- **Detección de duplicados**: por Número de Oficio, Juzgado y Fecha

## Stack

| Componente | Tecnología |
|---|---|
| Dashboard interactivo | Streamlit + Plotly |
| Sitio estático (Netlify) | Plotly.js + HTML/JS |
| Procesamiento de datos | Pandas |
| Normalización de texto | Unidecode + Regex |

## Estructura del proyecto

```
dashboard.py          # Dashboard Streamlit (principal)
generar_sitio.py      # Genera sitio estático en dist/
_site_template.html   # Template HTML del sitio estático
netlify.toml          # Configuración de Netlify
datos/                # CSVs de entrada (no versionados)
dist/                 # Sitio estático generado (no versionado)
```

## Uso local

### Streamlit

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas streamlit plotly openpyxl unidecode rapidfuzz
streamlit run dashboard.py
```

### Sitio estático

```bash
python generar_sitio.py
cd dist && python -m http.server 8080
```

## Despliegue en Netlify

1. Conectar este repo en Netlify
2. Build command: `pip install pandas unidecode && python generar_sitio.py`
3. Publish directory: `dist`

## Datos

Los archivos CSV deben ubicarse en la carpeta `datos/`:
- `embargos_colpatria.csv` — oficios de embargo (410K+ filas)
- `demandados_colpatria.csv` — información de demandados
