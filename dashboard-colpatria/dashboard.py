"""
Dashboard de Oficios – Colpatria
================================
Ejecutar:  streamlit run dashboard.py
"""

import re
import streamlit as st
import pandas as pd
import plotly.express as px
from unidecode import unidecode

# ─── Configuración ───────────────────────────────────────────────────────────
st.set_page_config(page_title="Oficios Colpatria", page_icon="📊", layout="wide")

# ─── Utilidades de texto ─────────────────────────────────────────────────────

def _limpia(texto):
    """Quita acentos, mayúsculas, puntuación y espacios extra."""
    if pd.isna(texto):
        return ""
    t = unidecode(str(texto)).upper().strip()
    t = re.sub(r"[.,;:!?'\"()\[\]{}/\\|@#$%^&*~`]", " ", t)
    t = re.sub(r"[–—]", "-", t)          # guiones largos → guion normal
    t = re.sub(r"\s+", " ", t).strip()
    return t

# ─── Ordinales → dígito ─────────────────────────────────────────────────────

_ORDINALES = {
    "PRIMERO": "1", "PRIMER": "1", "PRIMERA": "1",
    "SEGUNDO": "2", "SEGUNDA": "2",
    "TERCERO": "3", "TERCERA": "3", "TERCER": "3",
    "CUARTO": "4", "CUARTA": "4",
    "QUINTO": "5", "QUINTA": "5",
    "SEXTO": "6", "SEXTA": "6",
    "SEPTIMO": "7", "SEPTIMA": "7",
    "OCTAVO": "8", "OCTAVA": "8",
    "NOVENO": "9", "NOVENA": "9",
    "DECIMO": "10", "DECIMA": "10",
    "UNDECIMO": "11", "ONCE": "11",
    "DUODECIMO": "12", "DOCE": "12",
    "TRECE": "13", "DECIMOTERCERO": "13",
    "CATORCE": "14", "DECIMOCUARTO": "14",
    "QUINCE": "15", "DECIMOQUINTO": "15",
    "DIECISEIS": "16", "DECIMOSEXTO": "16",
    "DIECISIETE": "17", "DIECIOCHO": "18", "DIECINUEVE": "19",
    "VEINTE": "20", "VIGESIMO": "20",
    "VEINTIUNO": "21", "VEINTIUN": "21",
    "VEINTIDOS": "22", "VEINTITRES": "23", "VEINTICUATRO": "24",
    "VEINTICINCO": "25", "VEINTISEIS": "26", "VEINTISIETE": "27",
    "VEINTIOCHO": "28", "VEINTINUEVE": "29",
    "TREINTA": "30",
    "TREINTA Y UNO": "31", "TREINTA Y DOS": "32", "TREINTA Y TRES": "33",
    "TREINTA Y CUATRO": "34", "TREINTA Y CINCO": "35",
    "TREINTA Y SEIS": "36", "TREINTA Y SIETE": "37",
    "TREINTA Y OCHO": "38", "TREINTA Y NUEVE": "39",
    "CUARENTA": "40",
    "CUARENTA Y UNO": "41", "CUARENTA Y DOS": "42",
    "CUARENTA Y TRES": "43", "CUARENTA Y CUATRO": "44",
    "CUARENTA Y CINCO": "45", "CUARENTA Y SEIS": "46",
    "CUARENTA Y SIETE": "47", "CUARENTA Y OCHO": "48",
    "CUARENTA Y NUEVE": "49",
    "CINCUENTA": "50",
    "CINCUENTA Y UNO": "51", "CINCUENTA Y DOS": "52",
    "CINCUENTA Y TRES": "53", "CINCUENTA Y CUATRO": "54",
    "CINCUENTA Y CINCO": "55", "CINCUENTA Y SEIS": "56",
    "CINCUENTA Y SIETE": "57", "CINCUENTA Y OCHO": "58",
    "CINCUENTA Y NUEVE": "59",
    "SESENTA": "60", "SESENTA Y UNO": "61", "SESENTA Y DOS": "62",
    "SESENTA Y TRES": "63", "SESENTA Y CUATRO": "64",
    "SESENTA Y CINCO": "65", "SESENTA Y SEIS": "66",
    "SESENTA Y SIETE": "67", "SESENTA Y OCHO": "68",
    "SESENTA Y NUEVE": "69",
    "SETENTA": "70", "SETENTA Y UNO": "71", "SETENTA Y DOS": "72",
    "SETENTA Y TRES": "73", "SETENTA Y CUATRO": "74",
    "SETENTA Y CINCO": "75", "SETENTA Y SEIS": "76",
    "SETENTA Y SIETE": "77", "SETENTA Y OCHO": "78",
    "SETENTA Y NUEVE": "79",
    "OCHENTA": "80", "OCHENTA Y UNO": "81", "OCHENTA Y DOS": "82",
    "OCHENTA Y TRES": "83", "OCHENTA Y CUATRO": "84",
    "OCHENTA Y CINCO": "85",
    "NOVENTA": "90",
}

# ─── Departamentos de Colombia (para limpiar sufijos) ────────────────────────

_DEPTOS_LIST = [
    "VALLE DEL CAUCA", "NORTE DE SANTANDER",
    "SAN ANDRES PROVIDENCIA Y SANTA CATALINA", "SAN ANDRES Y PROVIDENCIA",
    "AMAZONAS", "ANTIOQUIA", "ANTIQUIA", "ANTRIOQUIA", "ARAUCA", "ATLANTICO",
    "BOLIVAR", "BOYACA", "CALDAS", "CAQUETA", "CASANARE", "CAUCA", "CESAR",
    "CHOCO", "CORDOBA", "CUNDINAMARCA", "CUMDINAMARCA", "CUNIDINAMARCA",
    "GUAINIA", "GUAJIRA", "LA GUAJIRA", "GUAVIARE", "HUILA", "MAGDALENA",
    "META", "NARINO", "PUTUMAYO", "QUINDIO", "Q7UINDIO", "RISARALDA",
    "SAN ANDRES", "SANTANDER", "SDER", "STDER", "SUCRE", "TOLIMA",
    "VALLE", "VAUPES", "VICHADA",
]
_DEPTOS_LIST.sort(key=len, reverse=True)

# ─── Diccionario maestro de alias de ciudades ───────────────────────────────
# Clave: texto limpio (o prefijo) → Valor: nombre normalizado.
# Se busca EXACTO primero, luego por prefijo más largo.
# ¡OJO! Municipios diferentes NUNCA se agrupan:
#   CALIMA ≠ CALI, CALIFORNIA ≠ CALI, CARTAGENA DEL CHAIRA ≠ CARTAGENA, etc.

_ALIAS_CIUDAD = {
    # --- Bogotá ---
    "BOGOTA D C": "BOGOTA D.C.", "BOGOTA DC": "BOGOTA D.C.",
    "BOGOTA D": "BOGOTA D.C.", "BOGOTA": "BOGOTA D.C.", "BOGOT": "BOGOTA D.C.",
    "BOGOTASCOTIABANK -": "BOGOTA D.C.",
    # --- Cali (sólo verdaderas variantes) ---
    "SANTIAGO DE CALI": "CALI", "SANTIAGO DE CALI 15": "CALI",
    "SANTIAGO DECALI": "CALI", "SANTIAGO CALI": "CALI",
    "SANTIGO DE CALI": "CALI", "SNTIAGO DE CALI": "CALI",
    "SANIAGO DE CALI": "CALI", "SANTIAGHO DE CALI": "CALI",
    "DE SANTIAGO DE CALI": "CALI",
    "CALI SANTIAGO DE CALI": "CALI", "CALI VALE": "CALI",
    "CALI YUMBO": "CALI", "VALLE CALI": "CALI",
    "VALLE DEL CAUCA CALI": "CALI", "CALI": "CALI",
    # --- Calima El Darién (municipio diferente, NO es Cali) ---
    "CALIMA EL DARIEN": "CALIMA EL DARIEN", "CALIMA EL DARIEN -": "CALIMA EL DARIEN",
    "CALIMA EL DARIEN - -": "CALIMA EL DARIEN",
    "CALIMA EL DARIEN-": "CALIMA EL DARIEN",
    "CALIMA-": "CALIMA", "CALIMA": "CALIMA",
    # --- California (municipio en Santander, NO es Cali) ---
    "CALIFORNIA": "CALIFORNIA",
    # --- Calica (NO es Cali) ---
    "CALICA": "CALICA",
    # --- San Calixto (NO es Cali) ---
    "SAN CALIXTO": "SAN CALIXTO",
    # --- Barranquilla ---
    "BARRANQUIILA": "BARRANQUILLA", "BARRANQUILA": "BARRANQUILLA",
    "BARRANQUILLAB": "BARRANQUILLA", "BARRAQUILLA": "BARRANQUILLA",
    "BARRANQUILLA D E I Y P": "BARRANQUILLA",
    "BARRANQUILLA SENORES": "BARRANQUILLA",
    "BARRANQUILLA": "BARRANQUILLA",
    # --- Medellín ---
    "MEDELLIN CARRERA 52": "MEDELLIN", "MEDELIN": "MEDELLIN",
    "SAN CRISTOBAL MEDELLIN": "MEDELLIN", "MEDELLIN": "MEDELLIN",
    # --- Cartagena / Cartagena del Chairá / Cartago ---
    "CARTAGENA DEL CHAIRA": "CARTAGENA DEL CHAIRA",
    "CARTAGENA DE INDIAS D T Y C": "CARTAGENA",
    "CARTAGENA DE INDIAS D T": "CARTAGENA",
    "CARTAGENA DE INDIAS": "CARTAGENA", "CARTAGENA DE INDAS": "CARTAGENA",
    "CARTAGENA D T Y C": "CARTAGENA", "CARTAGENA D T": "CARTAGENA",
    "CARTAGENA": "CARTAGENA",
    "CARTAGO": "CARTAGO",
    # --- Cúcuta ---
    "SAN JOSE DE CUCUTA": "CUCUTA", "SAN JOSE CUCUTA": "CUCUTA",
    "CUCUTA": "CUCUTA",
    # --- Floridablanca vs Florida ---
    "FLORIDA BLANCA": "FLORIDABLANCA", "FLORIDABLANCA": "FLORIDABLANCA",
    "FLORIDA": "FLORIDA",
    # --- Girardot vs Girardota ---
    "GIRARDOTA": "GIRARDOTA", "GIRARDOT": "GIRARDOT",
    # --- Ciudades principales ---
    "BUCARAMANGA SDER": "BUCARAMANGA", "BUCARAMANGA": "BUCARAMANGA",
    "VILLAVICENCIO": "VILLAVICENCIO",
    "IBAGUE": "IBAGUE", "MUNICIPIO DE IBAGUE": "IBAGUE",
    "COBROCOACTIVO IBAGUE GOV CO": "IBAGUE",
    "NEIVA": "NEIVA", "MUNICIPIO DE NEIVA": "NEIVA",
    "VALLEDUPAR": "VALLEDUPAR",
    "MONTERIA": "MONTERIA",
    "PEREIRA PEREIRA": "PEREIRA", "PEREIRA PUEBLO RICO": "PEREIRA",
    "PEREIRA": "PEREIRA", "MANIZALES": "MANIZALES",
    "ARMENIA Q7UINDIO": "ARMENIA", "ARMENIA": "ARMENIA",
    "SANTA MARTA D T C H": "SANTA MARTA", "SANTA MARTA": "SANTA MARTA",
    "IMPUESTOSOLEDAD": "SOLEDAD", "SOLEDAD0": "SOLEDAD", "SOLEDAD": "SOLEDAD",
    "POPAYAN": "POPAYAN",
    "SAN JUAN DE PASTO": "PASTO", "PASTO": "PASTO",
    "SINCELEJO": "SINCELEJO", "FLORENCIA": "FLORENCIA", "TUNJA": "TUNJA",
    "RIOHACHA": "RIOHACHA", "RIOACHA": "RIOHACHA",
    "QUIBDO": "QUIBDO", "YOPAL": "YOPAL", "ARAUCA": "ARAUCA",
    "SAN MIGUEL AGREDA DE MOCOA": "MOCOA",
    "SAN MIGUEL DE AGREDA DE MOCOA": "MOCOA",
    "SAN MIGUEL DE AGREDA MOCOA": "MOCOA", "MOCOA": "MOCOA",
    "LETICIA": "LETICIA", "MITU": "MITU", "INIRIDA": "INIRIDA",
    "PUERTO CARRENO": "PUERTO CARRENO",
    # --- Palmira (no confundir con SAN ANTONIO DE PALMITO) ---
    "SAN ANTONIO DE PALMIRA": "PALMIRA",
    "COMPETENCIA MULTIPLE PALMIRA": "PALMIRA",
    "PALMIRA V": "PALMIRA", "PALMIRA": "PALMIRA",
    # --- Espinal ---
    "EL ESPINAL": "ESPINAL", "ESPINAL": "ESPINAL",
    # --- Buga ---
    "GUADALAJARA DE BUGA": "BUGA", "GUADALAJARA BUGA": "BUGA",
    "GUADALAJARA": "BUGA", "BUGA": "BUGA",
    # --- La Dorada ---
    "LA DORA": "LA DORADA", "LA DORADA": "LA DORADA", "DORADA": "LA DORADA",
    # --- Dosquebradas ---
    "DE DOSQUEBRADAS": "DOSQUEBRADAS", "DOSQUEBRADAS": "DOSQUEBRADAS",
    # --- Rionegro ---
    "RIONEGRO ANT": "RIONEGRO", "RIONEGRO ANTIOQUA": "RIONEGRO",
    "RIO NEGRO": "RIONEGRO", "RIONEGRO": "RIONEGRO",
    # --- Apartadó ---
    "APARATADO": "APARTADO", "APARTADO": "APARTADO",
    # --- Jamundí ---
    "JAMUNDI VALLE DEL CUACA": "JAMUNDI", "JAMUNIDI": "JAMUNDI",
    "JAMUNDI": "JAMUNDI",
    # --- Soacha ---
    "SOACHA CUMDINAMARCA": "SOACHA", "SOACHA": "SOACHA",
    # --- Chía ---
    "CHIA CUMDINAMARCA": "CHIA", "CHIA": "CHIA",
    # --- Carmen de Bolívar ---
    "EL CARMEN DE BOLIVAR": "CARMEN DE BOLIVAR",
    "CARMEN DEL BOLIVAR": "CARMEN DE BOLIVAR",
    "CARMEN DE BOLIVAR": "CARMEN DE BOLIVAR",
    # --- Lorica ---
    "SANTA CRUZ DE LORICA": "LORICA", "LORICA": "LORICA",
    # --- Ciénaga ---
    "CIENAGA MAGADALENA": "CIENAGA", "INTRACIENAGA": "CIENAGA",
    "CIENAGA DE ORO": "CIENAGA DE ORO", "CIENAGA": "CIENAGA",
    # --- Los Patios ---
    "LOS PATIOS NTE DE SANTANDER": "LOS PATIOS",
    "LOS PATIOS N S": "LOS PATIOS", "LOS PATIOS": "LOS PATIOS",
    # --- El Zulia ---
    "EL ZULIA N DE S": "EL ZULIA", "EL ZULIA": "EL ZULIA", "ZULIA": "EL ZULIA",
    # --- Puerto Colombia ---
    "PUERTOCOLOMBIA": "PUERTO COLOMBIA", "PUERTO COLOMBIA": "PUERTO COLOMBIA",
    # --- Villa del Rosario ---
    "VILLA DE ROSARIO": "VILLA DEL ROSARIO",
    "VILLA DEL ROSARIO": "VILLA DEL ROSARIO",
    # --- Santander de Quilichao ---
    "SANTANDER DE QUILOCHAO": "SANTANDER DE QUILICHAO",
    "QUILICHAO": "SANTANDER DE QUILICHAO",
    "SANTANDER DE QUILICHAO": "SANTANDER DE QUILICHAO",
    # --- Agustín Codazzi ---
    "AGUSTIN CODAZZI": "AGUSTIN CODAZZI",
    "CODAZZI": "AGUSTIN CODAZZI",
    # --- Facatativá ---
    "FACATATIVA CUND": "FACATATIVA", "FACATATIVA": "FACATATIVA",
    # --- Tocancipá ---
    "TOCANCIPA": "TOCANCIPA",
    # --- La Calera ---
    "LA CALERA CUND": "LA CALERA", "LA CALERA": "LA CALERA",
    # --- Guamo ---
    "EL GUAMO": "GUAMO", "DEL GUAMO": "GUAMO", "GUAMO": "GUAMO",
    # --- Ipiales ---
    "IPIALES SANTANDER": "IPIALES", "IPIALES": "IPIALES",
    # --- Tumaco ---
    "SAN ANDRES DE TUMACO": "TUMACO", "TUMACO": "TUMACO",
    # --- Santiago de Tolú ---
    "SANTIAGO DE TOLU": "TOLU",
    # --- Socorro ---
    "EL SOCORRO": "SOCORRO", "SOCORRO": "SOCORRO",
    # --- Ariguaní ---
    "EL DIFICIL ARIGUANI": "ARIGUANI", "ARIGUANI": "ARIGUANI",
    # --- Pijino del Carmen ---
    "PIJINO DEL CARMEN": "PIJINO DEL CARMEN", "PIJINO": "PIJINO DEL CARMEN",
    # --- La Virginia ---
    "VIRGINIA": "LA VIRGINIA", "LA VIRGINIA": "LA VIRGINIA",
    # --- Valle del Guamuez ---
    "VALLE DEL GUAMUEZ LA HORMIGA": "VALLE DEL GUAMUEZ",
    "VALLE DEL GUAMUEZ": "VALLE DEL GUAMUEZ",
    # --- Belén de Umbría ---
    "BELEN DE UMBRIA": "BELEN DE UMBRIA", "UMBRIA": "BELEN DE UMBRIA",
    # --- Paz de Ariporo ---
    "PAZ DE ARIPORO": "PAZ DE ARIPORO", "ARIPORO": "PAZ DE ARIPORO",
    # --- Barranca de Upía ---
    "BARRANCA DE UPIA": "BARRANCA DE UPIA",
    # --- San José del Guaviare ---
    "SAN JOSE DEL GUAVIARE": "SAN JOSE DEL GUAVIARE",
    # --- San Vicente ---
    "SAN VICENTE DE CHUCURI": "SAN VICENTE DE CHUCURI",
    "SAN VICENTE DEL CAGUAN": "SAN VICENTE DEL CAGUAN",
    # --- San Marcos ---
    "SAN MARCOS": "SAN MARCOS",
    # --- San Juan del Cesar ---
    "SAN JUAN DEL CESAR": "SAN JUAN DEL CESAR",
    # --- San Juan Nepomuceno ---
    "SAN JUAN NEPOMUCENO": "SAN JUAN NEPOMUCENO",
    # --- San Martín ---
    "SAN MARTIN DE LOS LLANOS": "SAN MARTIN", "SAN MARTIN": "SAN MARTIN",
    "MARTIN CESAR": "SAN MARTIN",
    # --- San Carlos de Guaroa ---
    "SAN CARLOS DE GUAROA": "SAN CARLOS DE GUAROA", "SAN CARLOS": "SAN CARLOS",
    # --- San Gil ---
    "SAN GIL - STDER": "SAN GIL", "SAN GIL STDER": "SAN GIL",
    "SAN GIL": "SAN GIL",
    # --- San Andrés ---
    "SAN ANDRES ISLAS": "SAN ANDRES",
    "SAN ANDRES DE SOTAVENTO": "SAN ANDRES DE SOTAVENTO",
    "SAN ANDRES": "SAN ANDRES",
    # --- San Luis ---
    "SAN LUIS DE CUBARRAL": "CUBARRAL", "SAN LUIS DE PALENQUE": "SAN LUIS DE PALENQUE",
    "SAN LUIS": "SAN LUIS",
    # --- San Pedro ---
    "SAN PEDRO DE LOS MILAGROS": "SAN PEDRO DE LOS MILAGROS", "SAN PEDRO": "SAN PEDRO",
    # --- San Antonio ---
    "SAN ANTONIO DE PALMITO": "SAN ANTONIO DE PALMITO",
    "SAN ANTONIO DEL TEQUENDAMA": "SAN ANTONIO DEL TEQUENDAMA",
    "SAN ANTONIO": "SAN ANTONIO",
    # --- San Bernardo del Viento ---
    "SAN BERNARDO DEL VIENTO": "SAN BERNARDO DEL VIENTO",
    # --- San Juan de Girón ---
    "SAN JUAN DE GIRON": "GIRON", "SAN JUAN GIRON": "GIRON", "GIRON": "GIRON",
    # --- San Juan de Arama ---
    "SAN JUAN DE ARAMA": "SAN JUAN DE ARAMA",
    # --- San Sebastián de Buenavista ---
    "SAN SEBASTIAN DE BUENAVISTA": "SAN SEBASTIAN DE BUENAVISTA",
    # --- Otros San / Santa ---
    "SAN JERONIMO": "SAN JERONIMO", "SAN AGUSTIN": "SAN AGUSTIN",
    "SAN ALBERTO": "SAN ALBERTO", "SAN DIEGO": "SAN DIEGO",
    "SAN PELAYO": "SAN PELAYO", "SAN PABLO": "SAN PABLO",
    "SAN MIGUEL": "SAN MIGUEL", "SAN EDUARDO": "SAN EDUARDO",
    "SAN JOAQUIN": "SAN JOAQUIN", "SAN JOSE": "SAN JOSE",
    "SAN CAYETANO": "SAN CAYETANO", "SAN VICENTE": "SAN VICENTE",
    "SANTA ROSA DE CABAL": "SANTA ROSA DE CABAL",
    "SANTA ROSA DEL SUR DE BOLIVAR": "SANTA ROSA DEL SUR",
    "SANTA ROSA DEL SUR": "SANTA ROSA DEL SUR",
    "SANTA ROSA DE VITERBO": "SANTA ROSA DE VITERBO",
    "SANTA ROSA DE LIMA": "SANTA ROSA DE LIMA",
    "SANTA LUCIA": "SANTA LUCIA", "SANTA CATALINA": "SANTA CATALINA",
    "SANTA BARBARA DE PINTO": "SANTA BARBARA DE PINTO",
    "SANTA ANA": "SANTA ANA",
    # --- El ... ---
    "EL SANTUARIO": "EL SANTUARIO", "EL RETIRO": "EL RETIRO",
    "EL CERRITO": "EL CERRITO", "EL BANCO": "EL BANCO",
    "EL COPEY": "EL COPEY", "COPEY": "EL COPEY",
    "EL RETEN": "EL RETEN", "EL BAGRE": "EL BAGRE",
    "EL COLEGIO": "EL COLEGIO", "EL ROSAL": "EL ROSAL",
    "EL AGRADO": "EL AGRADO", "EL CARMEN DE CHUCURI": "EL CARMEN DE CHUCURI",
    "EL CARMEN": "EL CARMEN", "EL DOVIO": "EL DOVIO",
    "EL AGUILA": "EL AGUILA", "EL TAMBO": "EL TAMBO",
    "EL PLAYON": "EL PLAYON",
    # --- La ... ---
    "LA JAGUA DE IBIRICO": "LA JAGUA DE IBIRICO", "LA JAGUA": "LA JAGUA",
    "LA PLATA": "LA PLATA", "LA ESTRELLA": "LA ESTRELLA",
    "LA CEJA TAMBO": "LA CEJA", "LA CEJA": "LA CEJA",
    "LA MESA": "LA MESA", "LA VEGA": "LA VEGA",
    "LA UNION": "LA UNION", "LA BELLEZA": "LA BELLEZA",
    "LA PAZ": "LA PAZ", "LA GLORIA": "LA GLORIA",
    "LA CRUZ": "LA CRUZ", "LA MACARENA": "LA MACARENA",
    "LA CUMBRE": "LA CUMBRE", "LA VICTORIA": "LA VICTORIA",
    "LA ARGENTINA": "LA ARGENTINA", "LA MERCED": "LA MERCED",
    "LA PENA": "LA PENA", "LA CELIA": "LA CELIA",
    # --- Los ... ---
    "LOS SANTOS": "LOS SANTOS", "LOS PALMITOS": "LOS PALMITOS",
    "LOS CORDOBAS": "LOS CORDOBAS",
    # --- Carmen ... ---
    "CARMEN DE VIBORAL": "CARMEN DE VIBORAL",
    "CARMEN DE APICALA": "CARMEN DE APICALA",
    # --- Puerto ... ---
    "PUERTO BOYACA": "PUERTO BOYACA", "PUERTO LOPEZ": "PUERTO LOPEZ",
    "PUERTO BERRIO": "PUERTO BERRIO", "PUERTO SALGAR": "PUERTO SALGAR",
    "PUERTO GAITAN": "PUERTO GAITAN", "PUERTO ASIS": "PUERTO ASIS",
    "PUERTO TEJADA": "PUERTO TEJADA", "PUERTO LLERAS": "PUERTO LLERAS",
    "PUERTO ESCONDIDO": "PUERTO ESCONDIDO",
    "PUERTO WILCHES": "PUERTO WILCHES",
    "PUERTO LIBERTADOR": "PUERTO LIBERTADOR",
    "PUERTO TRIUNFO": "PUERTO TRIUNFO", "PUERTO RICO": "PUERTO RICO",
    "PUERTO LEGUIZAMO": "PUERTO LEGUIZAMO",
    "PUERTO PARRA": "PUERTO PARRA",
    # --- Zona ---
    "ZONA BANANERA": "ZONA BANANERA",
    # --- Villa ---
    "VILLA DE LEYVA": "VILLA DE LEYVA", "VILLA RICA": "VILLA RICA",
    "VILLAMARIA": "VILLAMARIA",
    # --- Sabana ---
    "SABANA DE TORRES": "SABANA DE TORRES",
    "SABANAGRANDE": "SABANAGRANDE",
    "MUNICIPIO DE SABANALARGA": "SABANALARGA", "SABANALARGA": "SABANALARGA",
    # --- Otros municipios frecuentes (alfabético) ---
    "ACACIAS": "ACACIAS", "ACEVEDO": "ACEVEDO",
    "ACHI": "ACHI", "AGUA DE DIOS": "AGUA DE DIOS",
    "AGUACHICA": "AGUACHICA", "AGUADAS": "AGUADAS",
    "AGUAZUL": "AGUAZUL", "AIPE": "AIPE",
    "ALBANIA": "ALBANIA", "ALCALA": "ALCALA",
    "ALGECIRAS": "ALGECIRAS", "ALPUJARRA": "ALPUJARRA",
    "ALTOS DEL ROSARIO": "ALTOS DEL ROSARIO", "ALVARADO": "ALVARADO",
    "AMBALEMA": "AMBALEMA", "ANAPOIMA": "ANAPOIMA",
    "ANCUYA": "ANCUYA", "ANDALUCIA": "ANDALUCIA",
    "ANDES": "ANDES", "ANSERMA": "ANSERMA",
    "APIA": "APIA", "ARACATACA": "ARACATACA",
    "ARATOCA": "ARATOCA", "ARAUQUITA": "ARAUQUITA",
    "ARBELAEZ": "ARBELAEZ", "ARBOLETES": "ARBOLETES",
    "ARGELIA": "ARGELIA", "ARJONA": "ARJONA",
    "ASTREA": "ASTREA",
    "BANCO": "EL BANCO",
    "BARANOA": "BARANOA", "BARAYA": "BARAYA",
    "BARBACOAS": "BARBACOAS", "BARBOSA": "BARBOSA",
    "BARICHARA": "BARICHARA",
    "BARRANCABERMEJA": "BARRANCABERMEJA", "BARRANCAS": "BARRANCAS",
    "BECERRIL": "BECERRIL", "BELALCAZAR": "BELALCAZAR",
    "BELEN": "BELEN", "BELLO": "BELLO",
    "BETULIA": "BETULIA", "BOJACA": "BOJACA",
    "BOLIVAR": "BOLIVAR", "BOSCONIA": "BOSCONIA",
    "BUENAVENTURA": "BUENAVENTURA", "BUENAVISTA": "BUENAVISTA",
    "BUESACO": "BUESACO", "BUGALAGRANDE": "BUGALAGRANDE",
    "BUENOS AIRES": "BUENOS AIRES",
    "CAICEDONIA": "CAICEDONIA", "CAIMITO": "CAIMITO",
    "CAJAMARCA": "CAJAMARCA", "CAJICA": "CAJICA",
    "CALARCA": "CALARCA", "CALOTO": "CALOTO",
    "CAMPOALEGRE": "CAMPOALEGRE", "CANALETE": "CANALETE",
    "CANDELARIA": "CANDELARIA", "CANTAGALLO": "CANTAGALLO",
    "CAPARRAPI": "CAPARRAPI", "CAQUEZA": "CAQUEZA",
    "CAREPA": "CAREPA", "CAROLINA DEL PRINCIPE": "CAROLINA DEL PRINCIPE",
    "CASABIANCA": "CASABIANCA", "CASTILLA": "CASTILLA",
    "CAUCASIA": "CAUCASIA", "CEPITA": "CEPITA",
    "CERETE": "CERETE", "CHAPARRAL": "CHAPARRAL",
    "CHARALA": "CHARALA", "CHIGORODO": "CHIGORODO",
    "CHIMA": "CHIMA", "CHIMICHAGUA": "CHIMICHAGUA",
    "CHINCHINA": "CHINCHINA", "CHINU": "CHINU",
    "CHIQUINQUIRA": "CHIQUINQUIRA",
    "CHIRIGUANA": "CHIRIGUANA", "CHOACHI": "CHOACHI",
    "CHOCONTA": "CHOCONTA", "CIMITARRA": "CIMITARRA",
    "CIRCASIA": "CIRCASIA", "CLEMENCIA": "CLEMENCIA",
    "COGUA": "COGUA", "COLON": "COLON", "COLOSO": "COLOSO",
    "COMBITA": "COMBITA", "CONCORDIA": "CONCORDIA",
    "CONSACA": "CONSACA", "COPACABANA": "COPACABANA",
    "CORINTO": "CORINTO", "COROZAL": "COROZAL",
    "COTA": "COTA", "COTORRA": "COTORRA",
    "COVENAS": "COVENAS", "COYAIMA": "COYAIMA",
    "CUBARRAL": "CUBARRAL", "CUCUNUBA": "CUCUNUBA",
    "CUMARAL": "CUMARAL", "CUMBAL": "CUMBAL",
    "CURITI": "CURITI", "CURUMANI": "CURUMANI",
    "DAGUA": "DAGUA", "DIBULLA": "DIBULLA",
    "DISTRACCION": "DISTRACCION", "DUITAMA": "DUITAMA",
    "ENCISO": "ENCISO", "ENVIGADO": "ENVIGADO",
    "FACATATIVA": "FACATATIVA",
    "FILANDIA": "FILANDIA", "FLANDES": "FLANDES",
    "FOMEQUE": "FOMEQUE", "FONSECA": "FONSECA",
    "FORTUL": "FORTUL", "FOSCA": "FOSCA", "FRESNO": "FRESNO",
    "FUENTEDEORO": "FUENTEDEORO", "FUNDACION": "FUNDACION",
    "FUNZA": "FUNZA", "FUSAGASUGA": "FUSAGASUGA",
    "GALAPA": "GALAPA", "GALERAS": "GALERAS",
    "GAMARRA": "GAMARRA", "GARAGOA": "GARAGOA",
    "GARZON": "GARZON", "GENOVA": "GENOVA",
    "GIGANTE": "GIGANTE", "GINEBRA": "GINEBRA",
    "GRANADA": "GRANADA", "GUACARI": "GUACARI",
    "GUACHENE": "GUACHENE", "GUADUAS": "GUADUAS",
    "GUALMATAN": "GUALMATAN", "GUAMAL": "GUAMAL",
    "GUARANDA": "GUARANDA", "GUARNE": "GUARNE",
    "GUATEQUE": "GUATEQUE", "GUATICA": "GUATICA",
    "GUAYABETAL": "GUAYABETAL",
    "HATONUEVO": "HATONUEVO", "HERVEO": "HERVEO",
    "HONDA": "HONDA", "MUNICIPIO DE HONDA": "HONDA",
    "ICONONZO": "ICONONZO", "INZA": "INZA",
    "IQUIRA": "IQUIRA", "ISTMINA": "ISTMINA",
    "ITAGUI": "ITAGUI",
    "JAMBALO": "JAMBALO", "JARDIN": "JARDIN",
    "JUAN DE ACOSTA": "JUAN DE ACOSTA",
    "LEBRIJA": "LEBRIJA", "LEJANIAS": "LEJANIAS",
    "LENGUAZAQUE": "LENGUAZAQUE", "LERIDA": "LERIDA",
    "LIBANO": "LIBANO", "LOPEZ DE MICAY": "LOPEZ DE MICAY",
    "LURUACO": "LURUACO",
    "MADRID": "MADRID", "MAGANGUE": "MAGANGUE",
    "MAHATES": "MAHATES", "MAICAO": "MAICAO",
    "MAJAGUAL": "MAJAGUAL", "MALAGA": "MALAGA",
    "MALAMBO": "MALAMBO", "MANAURE BALCON DEL CESAR": "MANAURE",
    "MANAURE": "MANAURE", "MANATI": "MANATI",
    "MANI": "MANI", "MANTA": "MANTA",
    "MANZANARES": "MANZANARES", "MARIA LA BAJA": "MARIA LA BAJA",
    "MARINILLA": "MARINILLA", "MARIQUITA": "MARIQUITA",
    "MARMATO": "MARMATO", "MARQUETALIA": "MARQUETALIA",
    "MARSELLA": "MARSELLA", "MEDINA": "MEDINA",
    "MELGAR": "MELGAR", "MESETAS": "MESETAS",
    "MIRANDA": "MIRANDA", "MISTRATO": "MISTRATO",
    "MOLAGAVITA": "MOLAGAVITA", "MOMPOX": "MOMPOX",
    "MOMIL": "MOMIL", "MONIQUIRA": "MONIQUIRA",
    "MONTECRISTO": "MONTECRISTO", "MONTELIBANO": "MONTELIBANO",
    "MONTENEGRO": "MONTENEGRO", "MONTERREY": "MONTERREY",
    "MONITOS": "MONITOS", "MORALES": "MORALES",
    "MOSQUERA": "MOSQUERA", "MUTATA": "MUTATA",
    "NEIRA": "NEIRA", "NEMOCON": "NEMOCON",
    "NILO": "NILO", "NOCAIMA": "NOCAIMA",
    "NUEVA GRANADA": "NUEVA GRANADA", "NUNCHIA": "NUNCHIA",
    "OBANDO": "OBANDO", "OCAMONTE": "OCAMONTE",
    "OCANA": "OCANA", "OIBA": "OIBA",
    "OICATA": "OICATA", "ORITO": "ORITO",
    "OROCUE": "OROCUE", "ORTEGA": "ORTEGA",
    "PACORA": "PACORA", "PAICOL": "PAICOL",
    "PAILITAS": "PAILITAS", "PAIPA": "PAIPA",
    "PALESTINA": "PALESTINA", "PALERMO": "PALERMO",
    "PALOCABILDO": "PALOCABILDO",
    "PALMAR DE VARELA": "PALMAR DE VARELA",
    "PAMPLONA": "PAMPLONA", "PANQUEBA": "PANQUEBA",
    "PARATEBUENO": "PARATEBUENO", "PATIA": "PATIA",
    "PAUNA": "PAUNA", "PELAYA": "PELAYA",
    "PENOL": "PENOL", "PENSILVANIA": "PENSILVANIA",
    "PIEDECUESTA": "PIEDECUESTA", "PIENDAMO": "PIENDAMO",
    "PIJAO": "PIJAO", "PINILLOS": "PINILLOS",
    "PIOJO": "PIOJO", "PITALITO": "PITALITO",
    "PLANETA RICA": "PLANETA RICA", "PLANETA": "PLANETA RICA",
    "PLATO": "PLATO", "POLICARPA": "POLICARPA",
    "PONEDERA": "PONEDERA", "PRADERA": "PRADERA",
    "PROVIDENCIA": "PROVIDENCIA", "PUEBLO NUEVO": "PUEBLO NUEVO",
    "PUEBLO RICO": "PUEBLO RICO", "PUPIALES": "PUPIALES",
    "PURIFICACION": "PURIFICACION",
    "QUIMBAYA": "QUIMBAYA",
    "RAMIRIQUI": "RAMIRIQUI", "RECETOR": "RECETOR",
    "REMOLINO": "REMOLINO", "REPELON": "REPELON",
    "RESTREPO": "RESTREPO", "RICAURTE": "RICAURTE",
    "RIOBLANCO": "RIOBLANCO", "RIOFRIO": "RIOFRIO",
    "RIOSUCIO": "RIOSUCIO", "RIVERA": "RIVERA",
    "ROLDANILLO": "ROLDANILLO",
    "SABANALARGA": "SABANALARGA", "SABANETA": "SABANETA",
    "SAHAGUN": "SAHAGUN", "SALDANA": "SALDANA",
    "SALAMINA": "SALAMINA", "SALENTO": "SALENTO",
    "SALGAR": "SALGAR", "SAMANIEGO": "SAMANIEGO",
    "SAMPUES": "SAMPUES", "SANDONA": "SANDONA",
    "SANTUARIO": "SANTUARIO", "SARAVENA": "SARAVENA",
    "SARDINATA": "SARDINATA", "SASAIMA": "SASAIMA",
    "SEGOVIA": "SEGOVIA", "SESQUILE": "SESQUILE",
    "SEVILLA": "SEVILLA", "SIACHOQUE": "SIACHOQUE",
    "SIBATE": "SIBATE", "SIBUNDOY": "SIBUNDOY",
    "SILVANIA": "SILVANIA", "SIMITI": "SIMITI",
    "SINCE": "SINCE", "SITIONUEVO": "SITIONUEVO",
    "SOATA": "SOATA", "SOCHA": "SOCHA",
    "SOGAMOSO": "SOGAMOSO", "SOPO": "SOPO",
    "SOPLAVIENTO": "SOPLAVIENTO", "SORACA": "SORACA",
    "SOTAQUIRA": "SOTAQUIRA", "SUAN": "SUAN",
    "SUAREZ": "SUAREZ", "SUAZA": "SUAZA",
    "SUBACHOQUE": "SUBACHOQUE", "SUESCA": "SUESCA",
    "SUPIA": "SUPIA", "SUSA": "SUSA",
    "SUTAMARCHAN": "SUTAMARCHAN",
    "TABIO": "TABIO", "TAMALAMEQUE": "TAMALAMEQUE",
    "TAME": "TAME", "TARQUI": "TARQUI",
    "TAURAMENA": "TAURAMENA", "TELLO": "TELLO",
    "TENA": "TENA", "TENJO": "TENJO",
    "TIBASOSA": "TIBASOSA", "TIERRALTA": "TIERRALTA",
    "TIMBIO": "TIMBIO", "TIPACOQUE": "TIPACOQUE",
    "TIQUISIO": "TIQUISIO", "TOCAIMA": "TOCAIMA",
    "TOLUVIEJO": "TOLUVIEJO", "TONA": "TONA",
    "TOPAIPI": "TOPAIPI", "TORO": "TORO",
    "TRUJILLO": "TRUJILLO", "TUBARA": "TUBARA",
    "TULUA": "TULUA", "TUMACO": "TUMACO",
    "TUQUERRES": "TUQUERRES", "TURBACO": "TURBACO",
    "TURBANA": "TURBANA", "TURBO": "TURBO",
    "TUTA": "TUTA",
    "UBALA": "UBALA", "UBAQUE": "UBAQUE", "UBATE": "UBATE",
    "URIBIA": "URIBIA", "URRAO": "URRAO",
    "USIACURI": "USIACURI",
    "VALENCIA": "VALENCIA", "VELEZ": "VELEZ",
    "VENADILLO": "VENADILLO", "VIJES": "VIJES",
    "VILLAGARZON": "VILLAGARZON", "VILLANUEVA": "VILLANUEVA",
    "VILLAPINZON": "VILLAPINZON", "VILLETA": "VILLETA",
    "VIOTA": "VIOTA", "VISTA HERMOSA": "VISTA HERMOSA",
    "VITERBO": "VITERBO",
    "YACOPI": "YACOPI", "YAGUARA": "YAGUARA",
    "YONDO": "YONDO", "YOTOCO": "YOTOCO", "YUMBO": "YUMBO",
    "ZAPATOCA": "ZAPATOCA", "ZARZAL": "ZARZAL",
    "ZETAQUIRA": "ZETAQUIRA", "ZIPAQUIRA": "ZIPAQUIRA",
    "ABEJORRAL": "ABEJORRAL", "ABREGO": "ABREGO",
    "SANTIAGO": "SANTIAGO", "SANTO TOMAS": "SANTO TOMAS",
    "PIAMONTE": "PIAMONTE",
    "GACHANCIPA": "GACHANCIPA",
    "SALETO": "SALENTO",
}

# Pre-calcular las claves ordenadas de mayor a menor longitud para prefijo
_ALIAS_KEYS_SORTED = sorted(_ALIAS_CIUDAD.keys(), key=len, reverse=True)

# Textos que NO son ciudades (basura en los datos)
_NO_ES_CIUDAD = {
    "SENTENCIA", "DESCONGESTION", "PEQUENAS", "NO ENCONTRADA", "NO ENCONTRADO",
    "ESTA", "VERSION", "JUZGADO", "GOBERNACION", "ALCALDIA", "DEPARTAMENTO",
    "CONSEJO SECCIONAL", "CONSEJO SUPERIOR", "DIRECCION", "ATENTAMENTE",
    "DISTRITO JUDICIAL", "MUNICIPAL", "DE SANTANDER", "DE BOLIVAR",
    "DE GALAPA", "PARQUE SANTANDER", "CORRESPONDENCIA",
    "CESAR ANDRES ARDILA SANCHEZ", "CREDIFINANCIERA", "SCOTIABANK",
    "LA LOCALIDAD", "LA PARTE",
    "GOBERNACION DE BOLIVAR", "ALCALDIA MUNICIPAL",
    "DEPARTAMENTO DE", "DEPARTAMENTO DEL",
    "JUZGADO PRIMERO", "JUZGADO SEGUNDO",
}


def _quitar_depto(texto):
    """Quita sufijos de departamento del texto."""
    resultado = texto
    for depto in _DEPTOS_LIST:
        resultado = re.sub(r"\s*-?\s*" + re.escape(depto) + r"\s*$", "", resultado).strip()
    return resultado


def normalizar_ciudad(raw):
    n = _limpia(raw)
    if not n:
        return "SIN CIUDAD"

    # Quitar números sueltos al final ("Santiago de Cali , 15")
    n = re.sub(r"\s+\d+\s*$", "", n).strip()

    # Separar por guion, tomar la primera parte
    partes = re.split(r"\s*-\s*", n)
    n_base = partes[0].strip()

    # Quitar departamento del final
    n_base = _quitar_depto(n_base)
    if not n_base:
        # Era solo un departamento, devolver como tal
        return n.replace("-", "").strip() if n.strip() else "SIN CIUDAD"

    # Verificar si es basura (no es ciudad)
    for no_city in _NO_ES_CIUDAD:
        if n_base == no_city or n_base.startswith(no_city + " "):
            return "SIN CIUDAD"

    # 1) Match exacto
    if n_base in _ALIAS_CIUDAD:
        return _ALIAS_CIUDAD[n_base]

    # 2) Buscar el prefijo más largo que haga match
    for alias in _ALIAS_KEYS_SORTED:
        if n_base.startswith(alias):
            rest = n_base[len(alias):]
            if rest == "" or rest[0] in " -":
                return _ALIAS_CIUDAD[alias]

    # 3) Sin match → devolver el texto base limpio
    return n_base if n_base else "SIN CIUDAD"


# ─── Normalización de ENTIDADES ──────────────────────────────────────────────

def _extraer_numero(texto):
    for ordinal in sorted(_ORDINALES.keys(), key=len, reverse=True):
        if ordinal in texto:
            return _ORDINALES[ordinal]
    m = re.search(r"\b0*(\d{1,3})\b", texto)
    if m:
        return m.group(1)
    return ""


def _extraer_ciudad_de_entidad(texto_entidad):
    """Intenta extraer la ciudad al final del nombre de una entidad."""
    ciudades_buscar = [
        ("BOGOTA D C", "BOGOTA D.C."), ("BOGOTA DC", "BOGOTA D.C."),
        ("BOGOTA", "BOGOTA D.C."),
        ("SANTIAGO DE CALI", "CALI"), ("CALI", "CALI"),
        ("BARRANQUILLA", "BARRANQUILLA"),
        ("CARTAGENA DE INDIAS", "CARTAGENA"), ("CARTAGENA", "CARTAGENA"),
        ("MEDELLIN", "MEDELLIN"), ("BUCARAMANGA", "BUCARAMANGA"),
        ("CUCUTA", "CUCUTA"), ("IBAGUE", "IBAGUE"),
        ("VILLAVICENCIO", "VILLAVICENCIO"),
        ("NEIVA", "NEIVA"), ("VALLEDUPAR", "VALLEDUPAR"),
        ("MONTERIA", "MONTERIA"), ("PEREIRA", "PEREIRA"),
        ("MANIZALES", "MANIZALES"), ("ARMENIA", "ARMENIA"),
        ("POPAYAN", "POPAYAN"), ("PASTO", "PASTO"),
        ("SINCELEJO", "SINCELEJO"), ("FLORENCIA", "FLORENCIA"),
        ("TUNJA", "TUNJA"), ("YOPAL", "YOPAL"),
        ("SANTA MARTA", "SANTA MARTA"),
        ("PALMIRA", "PALMIRA"), ("DOSQUEBRADAS", "DOSQUEBRADAS"),
        ("TULUA", "TULUA"), ("BUENAVENTURA", "BUENAVENTURA"),
        ("ITAGUI", "ITAGUI"), ("ENVIGADO", "ENVIGADO"),
        ("BELLO", "BELLO"), ("SOACHA", "SOACHA"),
        ("SOLEDAD", "SOLEDAD"), ("TURBACO", "TURBACO"),
        ("SOGAMOSO", "SOGAMOSO"), ("DUITAMA", "DUITAMA"),
        ("GIRARDOT", "GIRARDOT"), ("BARRANCABERMEJA", "BARRANCABERMEJA"),
        ("RIOHACHA", "RIOHACHA"), ("QUIBDO", "QUIBDO"),
        ("MOCOA", "MOCOA"), ("LETICIA", "LETICIA"),
        ("ARAUCA", "ARAUCA"), ("ESPINAL", "ESPINAL"),
        ("GARZON", "GARZON"), ("COROZAL", "COROZAL"),
        ("ORITO", "ORITO"), ("AGUSTIN CODAZZI", "AGUSTIN CODAZZI"),
        ("LA DORADA", "LA DORADA"),
    ]
    txt = _quitar_depto(texto_entidad).strip()
    for patron, ciudad in ciudades_buscar:
        if txt.endswith(patron):
            return ciudad
        if f" DE {patron}" in txt or f" - {patron}" in txt:
            return ciudad
    return ""


def normalizar_entidad(raw, ciudad_norm):
    n = _limpia(raw)
    if not n:
        return "SIN ENTIDAD"

    # ── JUZGADOS ──
    if "JUZGADO" in n or "DESPACHO JUDICIAL" in n:
        num = _extraer_numero(n)
        num_str = f" {num}" if num else ""

        if "PEQUENAS CAUSAS" in n or "COMPETENCIA MULTIPLE" in n:
            espec = "DE PEQUENAS CAUSAS Y COMP. MULTIPLE"
        elif "EJECUCION" in n and "SENTENCIA" in n:
            espec = "CIVIL MUN. DE EJECUCION DE SENTENCIAS"
        elif "PROMISCUO" in n and "FAMILIA" in n:
            espec = "PROMISCUO DE FAMILIA"
        elif "PROMISCUO" in n:
            espec = "PROMISCUO MUNICIPAL"
        elif "FAMILIA" in n and "CIRCUITO" in n:
            espec = "DE FAMILIA DEL CIRCUITO"
        elif "FAMILIA" in n:
            espec = "DE FAMILIA"
        elif "LABORAL" in n and "CIRCUITO" in n:
            espec = "LABORAL DEL CIRCUITO"
        elif "LABORAL" in n:
            espec = "LABORAL"
        elif "PENAL" in n and "CIRCUITO" in n:
            espec = "PENAL DEL CIRCUITO"
        elif "PENAL" in n:
            espec = "PENAL MUNICIPAL"
        elif "ADMINISTRATIVO" in n and "CIRCUITO" in n:
            espec = "ADMINISTRATIVO DEL CIRCUITO"
        elif "ADMINISTRATIVO" in n:
            espec = "ADMINISTRATIVO"
        elif "CIVIL" in n and "CIRCUITO" in n:
            espec = "CIVIL DEL CIRCUITO"
        elif "CIVIL" in n and "MUNICIPAL" in n:
            espec = "CIVIL MUNICIPAL"
        elif "CIVIL" in n:
            espec = "CIVIL"
        else:
            espec = "MUNICIPAL"

        ciudad_ent = _extraer_ciudad_de_entidad(n)
        ciudad_final = ciudad_ent if ciudad_ent else ciudad_norm
        return f"JUZGADO{num_str} {espec} - {ciudad_final}"

    # ── TRIBUNAL ──
    if "TRIBUNAL" in n:
        if "ADMINISTRATIVO" in n:
            return f"TRIBUNAL ADMINISTRATIVO - {ciudad_norm}"
        if "SUPERIOR" in n:
            return f"TRIBUNAL SUPERIOR - {ciudad_norm}"
        return f"TRIBUNAL - {ciudad_norm}"

    # ── OFICINA DE APOYO ──
    if "OFICINA DE APOYO" in n:
        ciudad_ent = _extraer_ciudad_de_entidad(n)
        ciudad_final = ciudad_ent if ciudad_ent else ciudad_norm
        return f"OFICINA DE APOYO JUDICIAL - {ciudad_final}"

    # ── DIAN ──
    if re.search(r"\bDIAN\b", n):
        return "DIAN"

    # ── SENA ──
    if re.search(r"\bSENA\b", n) and "SENTENCIA" not in n:
        return "SENA"

    # ── SUPERINTENDENCIAS ──
    if "SUPERINTENDENCIA" in n or "SUPERTRANSPORTE" in n:
        if "SOCIEDADES" in n:      return "SUPERINTENDENCIA DE SOCIEDADES"
        if "SALUD" in n:           return "SUPERSALUD"
        if "NOTARIADO" in n:       return "SUPERNOTARIADO Y REGISTRO"
        if "TRANSPORTE" in n:      return "SUPERTRANSPORTE"
        if "INDUSTRIA" in n:       return "SIC"
        return n[:70]

    # ── ALCALDÍAS ──
    if "ALCALD" in n:
        m = re.search(
            r"ALCALD\w*\s+(?:MAYOR\s+|DISTRITAL\s+|MUNICIPAL\s+)*(?:DE\s+|DEL\s+)?(.+)", n
        )
        if m:
            c_alc = m.group(1).strip()
            c_alc = _quitar_depto(c_alc)
            c_alc = re.sub(r"\s*D\s*C\s*$", "", c_alc).strip()
            if c_alc:
                return f"ALCALDIA DE {normalizar_ciudad(c_alc)}"
        return f"ALCALDIA DE {ciudad_norm}"

    # ── GOBERNACIONES / GOBIERNO ──
    if "GOBERNACION" in n or n.startswith("GOBIERNO"):
        m = re.search(r"(?:GOBERNACION|GOBIERNO)\s+(?:DE\s+|DEL\s+)?(.+)", n)
        if m:
            d = re.sub(r"\s*-\s*.*$", "", m.group(1)).strip()
            return f"GOBERNACION DE {d}"
        return "GOBERNACION"

    # ── DEPARTAMENTO (equivale a gobernación) ──
    if n.startswith("DEPARTAMENTO DE") or n.startswith("DEPARTAMENTO DEL"):
        m = re.search(r"DEPARTAMENTO\s+(?:DE\s+|DEL\s+)?(.+)", n)
        if m:
            return f"GOBERNACION DE {m.group(1).strip()}"

    # ── SECRETARÍAS ──
    if "SECRETARIA" in n:
        if "TRANSITO" in n or "MOVILIDAD" in n:
            return f"SECRETARIA DE TRANSITO - {ciudad_norm}"
        if "HACIENDA" in n:
            return f"SECRETARIA DE HACIENDA - {ciudad_norm}"
        if "EDUCACION" in n:
            return f"SECRETARIA DE EDUCACION - {ciudad_norm}"
        return f"SECRETARIA - {ciudad_norm}"

    # ── DATT / Tránsito ──
    if re.search(r"\bDATT\b", n) or ("TRANSITO" in n and "TRANSPORTE" in n):
        return f"DPTO TRANSITO Y TRANSPORTE - {ciudad_norm}"

    # ── IDU (sólo Instituto de Desarrollo Urbano de Bogotá) ──
    if re.search(r"\bIDU\b", n) and "EDUMAS" not in n:
        return "IDU"
    if "INSTITUTO" in n and "DESARROLLO URBANO" in n:
        return "IDU"

    # ── EDUMAS (Soledad) ──
    if "EDUMAS" in n or ("ESTABLECIMIENTO" in n and "DESARROLLO URBANO" in n):
        return "EDUMAS - SOLEDAD"

    # ── Corporaciones Autónomas ──
    if "CORPORACION AUTONOMA" in n:
        return f"CAR - {ciudad_norm}"
    for corp in ["CORPOCALDAS","CORNARE","CORPONOR","CORPOGUAJIRA","CVC",
                 "CORPOBOYACA","CORPOCHIVOR","CORTOLIMA","CRC","CRQ",
                 "CDMB","CORPOURABA","CORPAMAG","CORANTIOQUIA"]:
        if corp in n:
            return corp

    # ── FISCALÍA ──
    if "FISCALIA" in n:
        return f"FISCALIA - {ciudad_norm}"

    # ── UGPP ──
    if "UGPP" in n or "GESTION PENSIONAL" in n or ("UNIDAD" in n and "PARAFISCALES" in n):
        return "UGPP"

    # ── ICBF ──
    if re.search(r"\bICBF\b|BIENESTAR FAMILIAR", n):
        return "ICBF"

    # ── COLPENSIONES ──
    if "COLPENSIONES" in n:
        return "COLPENSIONES"

    # ── MINISTERIO ──
    if "MINISTERIO" in n:
        if "TRABAJO" in n: return "MINISTERIO DEL TRABAJO"
        if "DEFENSA" in n: return "MINISTERIO DE DEFENSA"
        if "HACIENDA" in n: return "MINISTERIO DE HACIENDA"
        return n[:70]

    # ── CONTRALORÍA ──
    if "CONTRALORIA" in n:
        if "GENERAL" in n:
            return "CONTRALORIA GENERAL DE LA REPUBLICA"
        return f"CONTRALORIA - {ciudad_norm}"

    # ── PROCURADURÍA ──
    if "PROCURADURIA" in n:
        return "PROCURADURIA"

    # ── POLICÍA ──
    if "POLICIA" in n or re.search(r"\bCTI\b|\bSIJIN\b", n):
        return f"POLICIA / CTI - {ciudad_norm}"

    # ── MUNICIPIO ──
    if "MUNICIPIO" in n:
        m = re.search(r"MUNICIPIO\s+(?:DE\s+|DEL\s+)?(.+)", n)
        if m:
            mu = _quitar_depto(m.group(1).strip())
            return f"MUNICIPIO DE {normalizar_ciudad(mu)}"
        return f"MUNICIPIO DE {ciudad_norm}"

    # ── COMISARÍAS ──
    if "COMISARIA" in n:
        return f"COMISARIA DE FAMILIA - {ciudad_norm}"

    # ── ESP ──
    if re.search(r"\bE\s*S\s*P\b|ACUEDUCTO|ALCANTARILLADO|CEIBAS|EMSERPA|EMCALI|AGUAS DE|EMPRESAS PUBLICAS", n):
        return f"EMPRESA SERV. PUBLICOS - {ciudad_norm}"

    # ── COLJUEGOS ──
    if "COLJUEGOS" in n:
        return "COLJUEGOS"

    # ── DIR EJECUTIVA JUDICIAL ──
    if "DIRECCION EJECUTIVA" in n and "JUDICIAL" in n:
        return "DIR. EJECUTIVA ADMIN JUDICIAL"

    # ── DIR SECCIONAL JUDICIAL ──
    if "DIRECCION SECCIONAL" in n and "JUDICIAL" in n:
        return f"DIR. SECCIONAL ADMIN JUDICIAL - {ciudad_norm}"

    # ── FONDO PREVISION / PASIVO ──
    if "FONDO DE PREVISION" in n:
        return "FONDO DE PREVISION SOCIAL"
    if "FONDO" in n and "PASIVO" in n:
        return "FONDO DE PASIVO SOCIAL"

    # ── COMISION NAL SERVICIO CIVIL ──
    if "COMISION NACIONAL DEL SERVICIO CIVIL" in n:
        return "COMISION NACIONAL DEL SERVICIO CIVIL"

    # ── INSTITUTO / TRANSITO ──
    if "INSTITUTO" in n and ("TRANSITO" in n or "MOVILIDAD" in n or "TRASPORTE" in n or "TRANSPORTE" in n):
        return f"INSTITUTO DE TRANSITO - {ciudad_norm}"
    if "INSPECCION" in n and "TRANSITO" in n:
        return f"INSPECCION DE TRANSITO - {ciudad_norm}"

    # ── Default ──
    return n[:80] if len(n) > 80 else n


# ─── Carga y procesamiento ───────────────────────────────────────────────────

@st.cache_data(show_spinner="Cargando y procesando datos …")
def cargar_y_procesar():
    df = pd.read_csv("datos/embargos_colpatria.csv", low_memory=False)

    # 1. Normalizar ciudades
    df["ciudad_norm"] = df["ciudad"].apply(normalizar_ciudad)

    # 2. Normalizar entidades (usa ciudad ya normalizada)
    df["entidad_norm"] = df.apply(
        lambda r: normalizar_entidad(r["entidad_remitente"], r["ciudad_norm"]),
        axis=1,
    )

    # 3. Detectar duplicados
    dup_cols = ["entidad_norm", "tipo_documento", "tipo_embargo",
                "monto", "referencia", "ciudad_norm"]
    conteo = df.groupby(dup_cols, dropna=False).size().reset_index(name="veces_repetido")
    df = df.merge(conteo, on=dup_cols, how="left")
    df["es_duplicado"] = df["veces_repetido"] > 1

    # 4. DataFrame sin duplicados
    df_unicos = df.drop_duplicates(subset=dup_cols, keep="first").copy()

    return df, df_unicos


df_all, df_unicos = cargar_y_procesar()

# ─── DASHBOARD ───────────────────────────────────────────────────────────────

st.title("📊 Dashboard de Oficios – Colpatria")

# ── Sidebar ──
st.sidebar.header("Filtros")

usar_unicos = st.sidebar.toggle("Excluir duplicados", value=False)
df_w = df_unicos.copy() if usar_unicos else df_all.copy()

clf_opts = ["Todos"] + sorted(df_w["tipo_documento"].dropna().unique().tolist())
clf_sel = st.sidebar.selectbox("Clasificación", clf_opts)
if clf_sel != "Todos":
    df_w = df_w[df_w["tipo_documento"] == clf_sel]

tipo_opts = ["Todos"] + sorted(df_w["tipo_embargo"].dropna().unique().tolist())
tipo_sel = st.sidebar.selectbox("Tipo de oficio", tipo_opts)
if tipo_sel != "Todos":
    df_w = df_w[df_w["tipo_embargo"] == tipo_sel]

city_top = df_w["ciudad_norm"].value_counts().head(50).index.tolist()
city_opts = ["Todas"] + city_top
city_sel = st.sidebar.selectbox("Ciudad", city_opts)
if city_sel != "Todas":
    df_w = df_w[df_w["ciudad_norm"] == city_sel]

ent_top_sidebar = df_w["entidad_norm"].value_counts().head(50).index.tolist()
ent_opts = ["Todas"] + ent_top_sidebar
ent_sel = st.sidebar.selectbox("Entidad (top 50)", ent_opts)
if ent_sel != "Todas":
    df_w = df_w[df_w["entidad_norm"] == ent_sel]

# Recalcular duplicados filtrados
dup_cols_kpi = ["entidad_norm", "tipo_documento", "tipo_embargo",
                "monto", "referencia", "ciudad_norm"]
df_w_unicos = df_w.drop_duplicates(subset=dup_cols_kpi, keep="first")
df_w_dup_count = len(df_w) - len(df_w_unicos)

# ── KPIs ──
st.markdown("---")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total oficios", f"{len(df_w):,}")
c2.metric("Únicos", f"{len(df_w_unicos):,}")
c3.metric("Duplicados", f"{df_w_dup_count:,}")
c4.metric("Entidades", f"{df_w['entidad_norm'].nunique():,}")
c5.metric("Ciudades", f"{df_w['ciudad_norm'].nunique():,}")

# ── Gráficos ──
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Clasificación (Embargo / Desembargo / Requerimiento)")
    td = df_w["tipo_documento"].value_counts().reset_index()
    td.columns = ["Clasificación", "Cantidad"]
    fig1 = px.pie(td, names="Clasificación", values="Cantidad",
                  color="Clasificación",
                  color_discrete_map={"EMBARGO":"#e74c3c",
                                      "DESEMBARGO":"#2ecc71",
                                      "REQUERIMIENTO":"#f39c12"},
                  hole=0.4)
    fig1.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig1, key="pie_clasif")

with col_b:
    st.subheader("Tipo de Oficio (Judicial / Coactivo)")
    te = df_w["tipo_embargo"].value_counts().reset_index()
    te.columns = ["Tipo", "Cantidad"]
    fig2 = px.pie(te, names="Tipo", values="Cantidad",
                  color="Tipo",
                  color_discrete_map={"JUDICIAL":"#3498db","COACTIVO":"#9b59b6"},
                  hole=0.4)
    fig2.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig2, key="pie_tipo")

# ── Entidades top 25 ──
st.markdown("---")
st.subheader("Top 25 Entidades")
ent_top = df_w["entidad_norm"].value_counts().head(25).reset_index()
ent_top.columns = ["Entidad", "Oficios"]
fig3 = px.bar(ent_top, x="Oficios", y="Entidad", orientation="h",
              color="Oficios", color_continuous_scale="Reds")
fig3.update_layout(yaxis=dict(autorange="reversed"), height=650)
st.plotly_chart(fig3, key="bar_ent")

# ── Ciudades top 25 ──
st.markdown("---")
st.subheader("Top 25 Ciudades")
cit_top = df_w["ciudad_norm"].value_counts().head(25).reset_index()
cit_top.columns = ["Ciudad", "Oficios"]
fig4 = px.bar(cit_top, x="Oficios", y="Ciudad", orientation="h",
              color="Oficios", color_continuous_scale="Greens")
fig4.update_layout(yaxis=dict(autorange="reversed"), height=600)
st.plotly_chart(fig4, key="bar_city")

# ── Cruce ──
st.markdown("---")
st.subheader("Clasificación × Tipo de Oficio")
cross = pd.crosstab(df_w["tipo_documento"], df_w["tipo_embargo"],
                    margins=True, margins_name="TOTAL")
st.dataframe(cross, use_container_width=True)

# ── Duplicados ──
st.markdown("---")
st.subheader("Resumen de Duplicados")
dc1, dc2 = st.columns([1, 2])
with dc1:
    tr = len(df_w)
    tu = len(df_w_unicos)
    td2 = tr - tu
    pct = td2 / tr * 100 if tr > 0 else 0
    st.markdown(f"""
| Métrica | Valor |
|---|---|
| Total registros | **{tr:,}** |
| Oficios únicos | **{tu:,}** |
| Registros duplicados | **{td2:,}** |
| % duplicación | **{pct:.1f}%** |
""")
with dc2:
    dup_cols = ["entidad_norm","tipo_documento","tipo_embargo",
                "monto","referencia","ciudad_norm"]
    top_dup = (
        df_w[df_w["es_duplicado"]]
        .drop_duplicates(subset=dup_cols, keep="first")
        .nlargest(15, "veces_repetido")
        [["entidad_norm","tipo_documento","tipo_embargo","monto",
          "ciudad_norm","veces_repetido"]]
        .rename(columns={"entidad_norm":"Entidad","tipo_documento":"Clasif.",
                         "tipo_embargo":"Tipo","monto":"Monto",
                         "ciudad_norm":"Ciudad","veces_repetido":"Repeticiones"})
    )
    st.dataframe(top_dup, use_container_width=True, hide_index=True)

# ── Detalle entidad: variantes ──
st.markdown("---")
st.subheader("Detalle de Entidad: variantes originales")

ent_lista = df_w["entidad_norm"].value_counts().reset_index()
ent_lista.columns = ["entidad", "n"]
ent_labels = [f"{r['entidad']}  ({r['n']:,})" for _, r in ent_lista.iterrows()]
sel_ent = st.selectbox("Entidad", ent_labels, key="sel_ent")
ent_name = sel_ent.rsplit("  (", 1)[0]

df_ent = df_w[df_w["entidad_norm"] == ent_name]
var_ent = (
    df_ent.groupby("entidad_remitente", dropna=False)
    .agg(cantidad=("id","count"),
         ciudades=("ciudad_norm", lambda x: ", ".join(sorted(x.unique())[:5])))
    .reset_index()
    .sort_values("cantidad", ascending=False)
    .rename(columns={"entidad_remitente":"Nombre original",
                     "cantidad":"Cantidad","ciudades":"Ciudades"})
)
st.dataframe(var_ent, use_container_width=True, hide_index=True, height=350)

# ── Detalle ciudad: variantes ──
st.markdown("---")
st.subheader("Detalle de Ciudad: variantes originales")

city_lista = df_w["ciudad_norm"].value_counts().reset_index()
city_lista.columns = ["ciudad", "n"]
city_labels = [f"{r['ciudad']}  ({r['n']:,})" for _, r in city_lista.iterrows()]
sel_city = st.selectbox("Ciudad", city_labels, key="sel_city")
city_name = sel_city.rsplit("  (", 1)[0]

df_city = df_w[df_w["ciudad_norm"] == city_name]
var_city = (
    df_city.groupby("ciudad", dropna=False)
    .agg(cantidad=("id","count"),
         entidades=("entidad_norm","nunique"))
    .reset_index()
    .sort_values("cantidad", ascending=False)
    .rename(columns={"ciudad":"Nombre original",
                     "cantidad":"Cantidad","entidades":"Entidades distintas"})
)
st.dataframe(var_city, use_container_width=True, hide_index=True, height=350)

# ── Footer ──
st.markdown("---")
st.caption("Dashboard Oficios Colpatria · Normalización automática de entidades y ciudades")
