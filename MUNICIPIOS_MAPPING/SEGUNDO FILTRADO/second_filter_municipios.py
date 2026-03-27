import os
import re
import unicodedata
from collections import defaultdict, Counter

import pandas as pd
from rapidfuzz import fuzz, process

PEND_PATH = '/home/user/data/pendientes_con_sugerencias.csv'
DIM_PATH = '/home/user/data/dim_municipios_final.csv'
OUT_DIR = '/mnt/user-data/outputs/segundo_filtrado_municipios'
os.makedirs(OUT_DIR, exist_ok=True)


def norm(s: str) -> str:
    s = '' if pd.isna(s) else str(s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.upper()
    s = re.sub(r'[^A-Z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    replacements = {
        'VALLEDEL': 'VALLE DEL',
        'LAGUAJIRA': 'LA GUAJIRA',
        'NORTEDESANTANDER': 'NORTE DE SANTANDER',
        'NORTEDESANTANDER': 'NORTE DE SANTANDER',
        'DESANTANDER': 'DE SANTANDER',
        'BOGOTADC': 'BOGOTA D C',
        'BOGOTAD C': 'BOGOTA D C',
        'SANJOSE': 'SAN JOSE',
        'SANTAFE': 'SANTA FE',
        'VALLEDELGUAMUEZ': 'VALLE DEL GUAMUEZ',
        'NDE': 'N DE',
    }
    for a, b in replacements.items():
        s = s.replace(a, b)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


STOPWORDS = {
    'DE', 'DEL', 'LA', 'EL', 'LOS', 'LAS', 'Y', 'D', 'C', 'DC', 'DT', 'TYC',
    'MUNICIPIO', 'MUNICIPAL', 'DISTRITO', 'CIUDAD', 'NO', 'NRO', 'NUMERO'
}


def core_tokens(s: str):
    return [t for t in norm(s).split() if t not in STOPWORDS]


def core(s: str) -> str:
    return ' '.join(core_tokens(s))


def alpha_token_count(s: str) -> int:
    return sum(1 for t in s.split() if re.search(r'[A-Z]', t))


pend = pd.read_csv(PEND_PATH)
dim = pd.read_csv(DIM_PATH, dtype={'codigo_dane': str})
dim['codigo_dane'] = dim['codigo_dane'].astype(str).str.zfill(5)
dim['norm_nombre'] = dim['nombre_normalizado'].fillna(dim['nombre']).map(norm)
dim['norm_departamento'] = dim['departamento'].map(norm)
dim['core_nombre'] = dim['nombre_normalizado'].fillna(dim['nombre']).map(core)

DEPT_ALIASES = {
    'VALLE': 'VALLE DEL CAUCA',
    'VALLE DELCAUCA': 'VALLE DEL CAUCA',
    'VALLEDEL CAUCA': 'VALLE DEL CAUCA',
    'NORTE DESANTANDER': 'NORTE DE SANTANDER',
    'N DE SANTANDER': 'NORTE DE SANTANDER',
    'N S': 'NORTE DE SANTANDER',
    'NS': 'NORTE DE SANTANDER',
    'GUAJIRA': 'LA GUAJIRA',
    'LAGUAJIRA': 'LA GUAJIRA',
    'BOGOTA DC': 'BOGOTA D C',
    'BOGOTA D C': 'BOGOTA D C',
    'D C': 'BOGOTA D C',
    'ARCHIPIELAGO': 'ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA',
}
DEPT_ALIASES = {norm(k): norm(v) for k, v in DEPT_ALIASES.items()}
OFFICIAL_DEPTS = sorted(set(dim['norm_departamento']), key=len, reverse=True)
DEPT_PATTERNS_BY_CANON = defaultdict(set)
for d in OFFICIAL_DEPTS:
    DEPT_PATTERNS_BY_CANON[d].add(d)
for patt, canon in DEPT_ALIASES.items():
    DEPT_PATTERNS_BY_CANON[canon].add(patt)
    DEPT_PATTERNS_BY_CANON[canon].add(canon)

BLOCKERS = [
    'JUZG', 'JUDICIAL', 'RAMA JUDICIAL', 'TRIBUNAL', 'FISCALIA', 'NOTARIA',
    'INSPECCION', 'COMISARIA', 'ALCALD', 'GOBERNACION', 'SECRETARIA',
    'HOSPITAL', 'UNIVERSIDAD', 'COLEGIO', 'SMJC', 'WEB', 'CAUTELAR', 'RADICADO',
    'EXPEDIENTE', 'EMBARGO', 'CONSEJO SUPERIOR DE LA JUDICATURA',
    'CONSEJO SECCIONAL DE LA JUDICATURA', 'DESPACHO', 'CIRCUITO', 'PROMISCUO',
    'LABORAL', 'CIVIL', 'PENAL', 'ADMINISTRATIVO', 'SAS', 'LTDA', 'S A S'
]

MANUAL_ALIASES_RAW = {
    'BOGOTA': '11001',
    'BGOTA': '11001',
    'BGOTA': '11001',
    'BOGOTA D C': '11001',
    'BOGOTAD': '11001',
    'BOGOTAD C': '11001',
    'BOGOT A': '11001',
    'BUGA': '76113',  # regla de negocio indicada por el usuario
    'GUADALAJARA BUGA': '76111',
    'GUADALAJARA DE BUGA': '76111',
    'GUADALAJARA': '76111',
    'CALIMA DARIEN': '76126',
    'CALIMA EL DARIEN': '76126',
    'AGUACAL': '85010',
    'AGUAM': '85010',
    'CUCUTA': '54001',
    'SAN JOSE CUCUTA': '54001',
    'CALI': '76001',
    'SANTIAGO CALI': '76001',
    'PASTO': '52001',
    'SAN JUAN PASTO': '52001',
    'UBATE': '25843',
    'MOMPOX': '13468',
    'MOMPOS': '13468',
    'DORADA': '17380',
    'MARIQUITA': '73443',
    'HORMIGA': '86865',
    'LA HORMIGA': '86865',
    'VALLE GUAMUEZ': '86865',
    'EL DIFICIL': '47058',
    'DIFICIL': '47058',
    'RONALDILLO': '76622',
    'CALENDARIA': '76130',
    'CARMEN CHUCURI': '68235',
    'CARMEN DE CHUCURI': '68235',
    'CARMEN VIBORAL': '05148',
    'CARMEN DE VIBORAL': '05148',
    'CAROLINA PRINCIPE': '05150',
    'CAROLINA DEL PRINCIPE': '05150',
    'CODAZZI': '20013',
    'SAN ANDRES ISLA': '88001',
    'SAN ANDRES ISLAS': '88001',
    'PROVIDENCIA ISLA': '88564',
    'PROVIDENCIA ISLAS': '88564',
    'TABAIDA': '63401',
    'PLAMIRA': '76520',
    'ZARAZAL': '76895',
    'CAUCACIA': '05154',
    'AIPE JUILA': '41016',
    'AGUAZUL CASANRE': '85010',
}
MANUAL_ALIASES = {core(k): str(v).zfill(5) for k, v in MANUAL_ALIASES_RAW.items()}

code_meta = {
    row.codigo_dane: {
        'nombre': row.nombre,
        'departamento': row.departamento,
        'norm_nombre': row.norm_nombre,
        'norm_departamento': row.norm_departamento,
        'core_nombre': row.core_nombre,
    }
    for row in dim.itertuples()
}

# exact core map
core_map = defaultdict(list)
for row in dim.itertuples():
    core_map[row.core_nombre].append(row.codigo_dane)

# alias catalog for ranking suggestions
code_to_aliases = defaultdict(set)
for row in dim.itertuples():
    code_to_aliases[row.codigo_dane].update({row.core_nombre, row.norm_nombre})
for alias_core, code in MANUAL_ALIASES.items():
    code_to_aliases[code].add(alias_core)

alias_choices = []
alias_choice_to_code = {}
for code, aliases in code_to_aliases.items():
    for alias in aliases:
        if alias:
            alias_choices.append(alias)
            alias_choice_to_code[alias] = code


def detect_dept(txt: str):
    found = []
    for d in OFFICIAL_DEPTS:
        if re.search(rf'\b{re.escape(d)}\b', txt):
            found.append(d)
    for k, v in DEPT_ALIASES.items():
        if re.search(rf'\b{re.escape(k)}\b', txt):
            found.append(v)
    if not found:
        return None
    found = sorted(set(found), key=len, reverse=True)
    return found[0]


def strip_departments(txt: str, dept: str | None):
    out = txt
    if dept:
        for patt in sorted(DEPT_PATTERNS_BY_CANON.get(dept, {dept}), key=len, reverse=True):
            out = re.sub(rf'\b{re.escape(patt)}\b', ' ', out)
    out = re.sub(r'\s+', ' ', out).strip()
    return out


def has_blocker(txt: str) -> bool:
    return any(b in txt for b in BLOCKERS)


def dept_is_consistent(code: str, dept: str | None) -> bool:
    if not dept:
        return True
    return code_meta[code]['norm_departamento'] == dept


def should_force_bogota(raw_norm: str, core_txt: str, dept: str | None):
    if 'BOGOT' in raw_norm or core_txt in {'BGOTA', 'BGOTA', 'BOGOTA', 'BOGOTA D C', 'BOGOT A'}:
        return dept in (None, 'BOGOTA D C')
    return False


def resolve_exact_and_fuzzy(raw_txt: str, dept: str | None, clean_txt: str, core_txt: str):
    # 1) regla especial Bogotá
    if should_force_bogota(raw_txt, core_txt, dept):
        return '11001', 'manual_bogota', 99.5, 'regla manual para variantes de Bogotá'

    # 2) aliases manuales exactos
    if core_txt in MANUAL_ALIASES:
        code = MANUAL_ALIASES[core_txt]
        if dept_is_consistent(code, dept):
            return code, 'alias_manual_exacto', 99.0, f'alias manual exacto: {core_txt}'
        return None, None, None, f'alias manual contradice departamento detectado ({dept})'

    # 3) match exacto por nombre core oficial
    if core_txt in core_map:
        codes = core_map[core_txt]
        if len(codes) == 1:
            code = codes[0]
            if dept_is_consistent(code, dept):
                return code, 'core_oficial_exacto', 100.0, 'coincidencia exacta con nombre oficial normalizado'
            return None, None, None, f'coincidencia exacta pero contradice departamento detectado ({dept})'
        if dept:
            dept_codes = [c for c in codes if dept_is_consistent(c, dept)]
            if len(dept_codes) == 1:
                return dept_codes[0], 'core_oficial_exacto_depto', 100.0, 'coincidencia exacta resuelta por departamento'
            return None, None, None, 'nombre exacto pero ambiguo entre varios municipios'

    # 4) fuzzy conservador para strings cortos/limpios
    if not core_txt:
        return None, None, None, 'texto limpio vacío tras normalización'

    token_n = alpha_token_count(core_txt)
    if token_n > 4 or len(core_txt) > 26:
        return None, None, None, 'texto demasiado largo para autoaprobación segura'

    matches = process.extract(core_txt, alias_choices, scorer=fuzz.ratio, limit=12)
    if not matches:
        return None, None, None, 'sin candidatos fuzzy'

    best_by_code = {}
    for alias, score, _ in matches:
        code = alias_choice_to_code[alias]
        final_score = float(score)
        if dept and dept_is_consistent(code, dept):
            final_score += 8.0
        if code not in best_by_code or final_score > best_by_code[code]['score']:
            best_by_code[code] = {
                'score': final_score,
                'base_score': float(score),
                'alias': alias,
            }

    ranked = sorted(best_by_code.items(), key=lambda kv: kv[1]['score'], reverse=True)
    if not ranked:
        return None, None, None, 'sin ranking fuzzy'

    best_code, best_meta = ranked[0]
    second_score = ranked[1][1]['score'] if len(ranked) > 1 else 0.0
    margin = best_meta['score'] - second_score

    if not dept_is_consistent(best_code, dept):
        return None, None, None, 'mejor fuzzy contradice departamento detectado'

    # umbral fuerte
    if best_meta['score'] >= 96 and margin >= 5:
        return best_code, 'fuzzy_corto_fuerte', round(min(best_meta['score'], 99.0), 2), f"fuzzy fuerte con alias '{best_meta['alias']}' y margen {margin:.2f}"

    # umbral medio sólo para alias manuales muy conocidos o depto consistente
    if best_meta['score'] >= 92 and margin >= 8 and (best_meta['alias'] in MANUAL_ALIASES or dept is not None):
        return best_code, 'fuzzy_corto_con_depto', round(min(best_meta['score'], 98.0), 2), f"fuzzy con contexto de departamento/alias '{best_meta['alias']}'"

    return None, None, None, f"mejor fuzzy insuficiente ({best_meta['score']:.2f}, margen {margin:.2f})"


def rank_candidates(raw_txt: str, dept: str | None, core_txt: str, limit: int = 3):
    query = core_txt or raw_txt
    if not query:
        return []
    matches = process.extract(query, alias_choices, scorer=fuzz.token_sort_ratio, limit=25)
    best_by_code = {}
    for alias, score, _ in matches:
        code = alias_choice_to_code[alias]
        final_score = float(score)
        if dept and dept_is_consistent(code, dept):
            final_score += 8.0
        if code not in best_by_code or final_score > best_by_code[code]['score']:
            best_by_code[code] = {
                'score': round(min(final_score, 100.0), 2),
                'alias': alias,
            }
    ranked = sorted(best_by_code.items(), key=lambda kv: kv[1]['score'], reverse=True)[:limit]
    out = []
    for code, meta in ranked:
        cm = code_meta[code]
        out.append({
            'codigo': code,
            'nombre': cm['nombre'],
            'departamento': cm['departamento'],
            'score': meta['score'],
            'alias': meta['alias'],
        })
    return out


records = []
for row in pend.itertuples(index=False):
    raw_norm = norm(row.valor_original)
    dept = detect_dept(raw_norm)
    stripped_no_dept = strip_departments(raw_norm, dept)
    core_txt = core(stripped_no_dept)

    final_status = 'PENDIENTE'
    final_code = None
    final_method = None
    final_conf = None
    final_reason = None

    if has_blocker(raw_norm):
        final_status = 'IGNORAR'
        final_reason = 'contiene términos institucionales/judiciales/administrativos; no debe mapearse a municipio'
    else:
        code, method, conf, reason = resolve_exact_and_fuzzy(raw_norm, dept, stripped_no_dept, core_txt)
        if code:
            final_status = 'AUTOAPROBADO'
            final_code = code
            final_method = method
            final_conf = conf
            final_reason = reason
        else:
            final_reason = reason

    candidates = rank_candidates(raw_norm, dept, core_txt, limit=3)
    flat_candidates = {}
    for i in range(3):
        if i < len(candidates):
            c = candidates[i]
            flat_candidates[f'final_top_{i+1}_codigo'] = c['codigo']
            flat_candidates[f'final_top_{i+1}_nombre'] = c['nombre']
            flat_candidates[f'final_top_{i+1}_departamento'] = c['departamento']
            flat_candidates[f'final_top_{i+1}_score'] = c['score']
            flat_candidates[f'final_top_{i+1}_alias'] = c['alias']
        else:
            flat_candidates[f'final_top_{i+1}_codigo'] = None
            flat_candidates[f'final_top_{i+1}_nombre'] = None
            flat_candidates[f'final_top_{i+1}_departamento'] = None
            flat_candidates[f'final_top_{i+1}_score'] = None
            flat_candidates[f'final_top_{i+1}_alias'] = None

    cm = code_meta.get(final_code, {}) if final_code else {}

    rec = row._asdict()
    rec.update({
        'raw_norm_2': raw_norm,
        'departamento_detectado': dept,
        'texto_sin_departamento': stripped_no_dept,
        'core_filtrado_2': core_txt,
        'estado_final_2': final_status,
        'codigo_dane_final_2': final_code,
        'nombre_dane_final_2': cm.get('nombre'),
        'departamento_final_2': cm.get('departamento'),
        'metodo_final_2': final_method,
        'confianza_final_2': final_conf,
        'motivo_final_2': final_reason,
    })
    rec.update(flat_candidates)
    records.append(rec)

full = pd.DataFrame(records)

mapping = full[full['estado_final_2'] == 'AUTOAPROBADO'][[
    'valor_original', 'valor_normalizado', 'codigo_dane_final_2', 'metodo_final_2', 'confianza_final_2'
]].copy()
mapping.columns = ['valor_original', 'valor_normalizado', 'codigo_dane', 'metodo', 'confianza']
mapping['revisado'] = True
mapping = mapping.sort_values(['codigo_dane', 'valor_original']).reset_index(drop=True)

approved_detail = full[full['estado_final_2'] == 'AUTOAPROBADO'].copy()
ignored_detail = full[full['estado_final_2'] == 'IGNORAR'].copy()
pending_suggestions = full[full['estado_final_2'] == 'PENDIENTE'].copy()

summary_rows = []
summary_rows.append({'tipo': 'total_registros', 'valor': int(len(full))})
summary_rows.append({'tipo': 'autoaprobados', 'valor': int((full['estado_final_2'] == 'AUTOAPROBADO').sum())})
summary_rows.append({'tipo': 'ignorados', 'valor': int((full['estado_final_2'] == 'IGNORAR').sum())})
summary_rows.append({'tipo': 'pendientes_finales', 'valor': int((full['estado_final_2'] == 'PENDIENTE').sum())})
for method, cnt in full['metodo_final_2'].fillna('sin_metodo').value_counts().items():
    summary_rows.append({'tipo': f'metodo::{method}', 'valor': int(cnt)})
for dept, cnt in approved_detail['departamento_final_2'].fillna('SIN_DEPTO').value_counts().head(20).items():
    summary_rows.append({'tipo': f'autoaprobados_depto::{dept}', 'valor': int(cnt)})
summary = pd.DataFrame(summary_rows)

mapping.to_csv(os.path.join(OUT_DIR, 'mappingmunicipios_listo.csv'), index=False)
approved_detail.to_csv(os.path.join(OUT_DIR, 'auto_aprobados_detalle.csv'), index=False)
pending_suggestions.to_csv(os.path.join(OUT_DIR, 'pendientes_con_sugerencias.csv'), index=False)
full.to_csv(os.path.join(OUT_DIR, 'reclasificacion_completa.csv'), index=False)
summary.to_csv(os.path.join(OUT_DIR, 'resumen_estadistico.csv'), index=False)

# Extra útil: ignorados separados
ignored_detail.to_csv(os.path.join(OUT_DIR, 'ignorados_detectados.csv'), index=False)

print('Archivos generados en:', OUT_DIR)
print('Total:', len(full))
print(full['estado_final_2'].value_counts().to_string())
print('\nTop métodos:')
print(full['metodo_final_2'].fillna('sin_metodo').value_counts().head(10).to_string())
print('\nMuestra autoaprobados:')
cols = ['valor_original', 'codigo_dane_final_2', 'nombre_dane_final_2', 'departamento_final_2', 'metodo_final_2', 'confianza_final_2', 'motivo_final_2']
print(approved_detail[cols].head(20).to_string(index=False))
print('\nMuestra pendientes:')
cols2 = ['valor_original', 'core_filtrado_2', 'motivo_final_2', 'final_top_1_codigo', 'final_top_1_nombre', 'final_top_1_departamento', 'final_top_1_score']
print(pending_suggestions[cols2].head(20).to_string(index=False))
