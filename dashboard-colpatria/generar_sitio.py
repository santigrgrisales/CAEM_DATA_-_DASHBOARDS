"""
generar_sitio.py
================
Lee el CSV, aplica la misma normalización que dashboard.py,
y exporta JSONs compactos + el HTML estático en dist/.

Ejecutar:  python generar_sitio.py
Resultado: carpeta dist/ lista para Netlify.
"""

import json, os, re, shutil, sys, ast
import pandas as pd
from unidecode import unidecode

# ─── Importar sólo las funciones de normalización del dashboard ─────────────
# Parseamos el archivo para extraer las funciones y constantes sin ejecutar
# el código de Streamlit/plotly.

_DASHBOARD = os.path.join(os.path.dirname(__file__), "dashboard.py")

def _import_normalizers():
    """Lee dashboard.py, extrae todo hasta 'cargar_y_procesar' y lo ejecuta
    en un namespace limpio, sin Streamlit."""
    with open(_DASHBOARD, "r", encoding="utf-8") as f:
        src = f.read()
    # Cortamos justo antes de la función cargar_y_procesar (y todo el dashboard UI)
    marker = "@st.cache_data"
    idx = src.find(marker)
    if idx == -1:
        marker = "def cargar_y_procesar"
        idx = src.find(marker)
    if idx > 0:
        src = src[:idx]
    # Quitar imports de streamlit y plotly
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import streamlit") or stripped.startswith("from streamlit"):
            continue
        if stripped.startswith("import plotly") or stripped.startswith("from plotly"):
            continue
        if stripped.startswith("st.set_page_config"):
            continue
        lines.append(line)
    clean_src = "\n".join(lines)
    ns = {"re": re, "pd": pd, "unidecode": unidecode}
    exec(compile(clean_src, _DASHBOARD, "exec"), ns)
    return ns["normalizar_ciudad"], ns["normalizar_entidad"]

normalizar_ciudad, normalizar_entidad = _import_normalizers()

# ─── Configuración ──────────────────────────────────────────────────────────

DIST = os.path.join(os.path.dirname(__file__), "dist")
DATA_DIR = os.path.join(DIST, "data")

def main():
    print("📂 Leyendo CSV …")
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),
                                  "datos", "embargos_colpatria.csv"),
                     low_memory=False)
    print(f"   {len(df):,} filas cargadas")

    # ── Normalizar ──
    print("🔧 Normalizando ciudades …")
    df["ciudad_norm"] = df["ciudad"].apply(normalizar_ciudad)

    print("🔧 Normalizando entidades …")
    df["entidad_norm"] = df.apply(
        lambda r: normalizar_entidad(r["entidad_remitente"], r["ciudad_norm"]),
        axis=1,
    )

    # ── Duplicados ──
    print("🔍 Detectando duplicados …")
    dup_cols = ["entidad_norm","tipo_documento","tipo_embargo",
                "monto","referencia","ciudad_norm"]
    conteo = df.groupby(dup_cols, dropna=False).size().reset_index(name="veces_repetido")
    df = df.merge(conteo, on=dup_cols, how="left")
    df["es_duplicado"] = df["veces_repetido"] > 1

    df_unicos = df.drop_duplicates(subset=dup_cols, keep="first").copy()

    # ── Crear carpeta dist ──
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DATA_DIR, exist_ok=True)

    # ── Generar JSONs ──
    print("📊 Generando JSONs …")

    # 1) KPIs globales
    kpis = {
        "total": int(len(df)),
        "unicos": int(len(df_unicos)),
        "duplicados": int(len(df) - len(df_unicos)),
        "entidades": int(df["entidad_norm"].nunique()),
        "ciudades": int(df["ciudad_norm"].nunique()),
    }
    _w(kpis, "kpis.json")

    # 2) Clasificación (tipo_documento)
    td = df["tipo_documento"].value_counts().to_dict()
    td = {str(k): int(v) for k,v in td.items()}
    _w(td, "clasificacion.json")

    # 3) Tipo de oficio (tipo_embargo)
    te = df["tipo_embargo"].value_counts().to_dict()
    te = {str(k): int(v) for k,v in te.items()}
    _w(te, "tipo_oficio.json")

    # 4) Cross tabla clasificacion x tipo
    cross = pd.crosstab(df["tipo_documento"], df["tipo_embargo"],
                        margins=True, margins_name="TOTAL")
    cross_dict = {}
    for idx in cross.index:
        cross_dict[str(idx)] = {str(c): int(cross.loc[idx, c]) for c in cross.columns}
    _w(cross_dict, "cross.json")

    # 5) Top 50 entidades
    ent_top = df["entidad_norm"].value_counts().head(50)
    ent_list = [{"name": str(k), "count": int(v)} for k,v in ent_top.items()]
    _w(ent_list, "top_entidades.json")

    # 6) Top 50 ciudades
    city_top = df["ciudad_norm"].value_counts().head(50)
    city_list = [{"name": str(k), "count": int(v)} for k,v in city_top.items()]
    _w(city_list, "top_ciudades.json")

    # 7) Top 15 duplicados
    top_dup = (
        df[df["es_duplicado"]]
        .drop_duplicates(subset=dup_cols, keep="first")
        .nlargest(15, "veces_repetido")
        [["entidad_norm","tipo_documento","tipo_embargo","monto",
          "ciudad_norm","veces_repetido"]]
    )
    dup_list = []
    for _, r in top_dup.iterrows():
        dup_list.append({
            "entidad": str(r["entidad_norm"]),
            "clasificacion": str(r["tipo_documento"]),
            "tipo": str(r["tipo_embargo"]),
            "monto": str(r["monto"]) if pd.notna(r["monto"]) else "",
            "ciudad": str(r["ciudad_norm"]),
            "repeticiones": int(r["veces_repetido"]),
        })
    _w(dup_list, "top_duplicados.json")

    # 8) Datos para filtros combinados: agrupados por clasificacion, tipo, ciudad, entidad
    # Para que el frontend pueda filtrar, generamos conteos cruzados
    # Agrupación: (clasificacion, tipo) → count
    clf_tipo = df.groupby(["tipo_documento","tipo_embargo"], dropna=False).size()
    clf_tipo_list = [{"clf": str(k[0]), "tipo": str(k[1]), "n": int(v)}
                     for k,v in clf_tipo.items()]
    _w(clf_tipo_list, "clf_tipo.json")

    # 9) Por clasificación → entidades top 25
    by_clf_ent = {}
    for clf in df["tipo_documento"].dropna().unique():
        sub = df[df["tipo_documento"] == clf]
        top = sub["entidad_norm"].value_counts().head(25)
        by_clf_ent[str(clf)] = [{"name": str(k), "count": int(v)} for k,v in top.items()]
    _w(by_clf_ent, "clf_entidades.json")

    # 10) Por clasificación → ciudades top 25
    by_clf_city = {}
    for clf in df["tipo_documento"].dropna().unique():
        sub = df[df["tipo_documento"] == clf]
        top = sub["ciudad_norm"].value_counts().head(25)
        by_clf_city[str(clf)] = [{"name": str(k), "count": int(v)} for k,v in top.items()]
    _w(by_clf_city, "clf_ciudades.json")

    # 11) Variantes de entidad (todas las entidades normalizadas con sus originales)
    var_ent = (
        df.groupby(["entidad_norm","entidad_remitente"], dropna=False)
        .agg(cantidad=("ciudad","count"),
             ciudades=("ciudad_norm", lambda x: ", ".join(sorted(x.unique())[:5])))
        .reset_index()
    )
    # Agrupar por entidad_norm
    ent_variantes = {}
    for ent_name in var_ent["entidad_norm"].unique():
        sub = var_ent[var_ent["entidad_norm"] == ent_name].sort_values("cantidad", ascending=False)
        items = []
        for _, r in sub.head(20).iterrows():
            items.append({
                "original": str(r["entidad_remitente"]) if pd.notna(r["entidad_remitente"]) else "",
                "cantidad": int(r["cantidad"]),
                "ciudades": str(r["ciudades"]),
            })
        ent_variantes[str(ent_name)] = items
    _w(ent_variantes, "variantes_entidad.json")

    # 12) Variantes de ciudad
    var_city = (
        df.groupby(["ciudad_norm","ciudad"], dropna=False)
        .agg(cantidad=("entidad_norm","count"),
             entidades=("entidad_norm","nunique"))
        .reset_index()
    )
    city_variantes = {}
    for city_name in var_city["ciudad_norm"].unique():
        sub = var_city[var_city["ciudad_norm"] == city_name].sort_values("cantidad", ascending=False)
        items = []
        for _, r in sub.head(20).iterrows():
            items.append({
                "original": str(r["ciudad"]) if pd.notna(r["ciudad"]) else "",
                "cantidad": int(r["cantidad"]),
                "entidades": int(r["entidades"]),
            })
        city_variantes[str(city_name)] = items
    _w(city_variantes, "variantes_ciudad.json")

    # 13) Listas completas para filtros
    all_clf = sorted([str(x) for x in df["tipo_documento"].dropna().unique()])
    all_tipo = sorted([str(x) for x in df["tipo_embargo"].dropna().unique()])
    all_cities = [{"name": str(k), "count": int(v)} 
                  for k,v in df["ciudad_norm"].value_counts().head(100).items()]
    all_ents = [{"name": str(k), "count": int(v)} 
                for k,v in df["entidad_norm"].value_counts().head(100).items()]
    _w({"clasificaciones": all_clf, "tipos": all_tipo,
        "ciudades": all_cities, "entidades": all_ents}, "filtros.json")

    # 14) Cube: datos agrupados indexados para filtrado client-side
    g = df.groupby(["tipo_documento","tipo_embargo","ciudad_norm","entidad_norm"],
                   dropna=False).size().reset_index(name="n")
    cube_clfs = sorted(g["tipo_documento"].dropna().unique().tolist())
    cube_tipos = sorted(g["tipo_embargo"].dropna().unique().tolist())
    cube_cities = sorted(g["ciudad_norm"].dropna().unique().tolist())
    cube_ents = sorted(g["entidad_norm"].dropna().unique().tolist())
    rows = []
    for _, r in g.iterrows():
        ci = cube_clfs.index(r["tipo_documento"]) if pd.notna(r["tipo_documento"]) else -1
        ti = cube_tipos.index(r["tipo_embargo"]) if pd.notna(r["tipo_embargo"]) else -1
        cyi = cube_cities.index(r["ciudad_norm"]) if pd.notna(r["ciudad_norm"]) else -1
        ei = cube_ents.index(r["entidad_norm"]) if pd.notna(r["entidad_norm"]) else -1
        rows.append([ci, ti, cyi, ei, int(r["n"])])
    _w({"clfs": cube_clfs, "tipos": cube_tipos, "cities": cube_cities,
        "ents": cube_ents, "rows": rows}, "cube.json")

    # 15) Cube sin duplicados
    g_u = df_unicos.groupby(["tipo_documento","tipo_embargo","ciudad_norm","entidad_norm"],
                            dropna=False).size().reset_index(name="n")
    rows_u = []
    for _, r in g_u.iterrows():
        ci = cube_clfs.index(r["tipo_documento"]) if pd.notna(r["tipo_documento"]) else -1
        ti = cube_tipos.index(r["tipo_embargo"]) if pd.notna(r["tipo_embargo"]) else -1
        cyi = cube_cities.index(r["ciudad_norm"]) if pd.notna(r["ciudad_norm"]) else -1
        ei = cube_ents.index(r["entidad_norm"]) if pd.notna(r["entidad_norm"]) else -1
        rows_u.append([ci, ti, cyi, ei, int(r["n"])])
    _w({"clfs": cube_clfs, "tipos": cube_tipos, "cities": cube_cities,
        "ents": cube_ents, "rows": rows_u}, "cube_unicos.json")

    # ── Copiar HTML ──
    print("📄 Generando index.html …")
    html_src = os.path.join(os.path.dirname(__file__), "_site_template.html")
    if os.path.exists(html_src):
        shutil.copy(html_src, os.path.join(DIST, "index.html"))
    else:
        print("   ⚠️  _site_template.html no encontrado, se generará desde el script")

    total_size = sum(os.path.getsize(os.path.join(DATA_DIR, f))
                     for f in os.listdir(DATA_DIR)) / 1024
    print(f"\n✅ Listo! dist/ generada ({total_size:.0f} KB en JSONs)")
    print(f"   Archivos: {', '.join(sorted(os.listdir(DATA_DIR)))}")
    print(f"\n🚀 Para probar localmente:")
    print(f"   cd dist && python -m http.server 8080")
    print(f"   Abrir http://localhost:8080")
    print(f"\n🌐 Para Netlify:")
    print(f"   Subir la carpeta dist/ o conectar con GitHub")


def _w(data, filename):
    """Escribe JSON compacto."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",",":"))
    size = os.path.getsize(path) / 1024
    print(f"   → {filename} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
