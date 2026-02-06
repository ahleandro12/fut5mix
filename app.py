import streamlit as st
import pandas as pd
from datetime import datetime
from itertools import combinations
import hashlib

# CONFIGURACIÓN ORIGINAL
st.set_page_config(page_title="Fútbol 5 Mix", page_icon="⚽", layout="wide")

# EL LINK QUE ME PASASTE
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZa2h4NTGFYauxD_7TufjMcQTCYUK_pxaaHUWAre4oDPedzmXjOWbHFRzzSWn6t7BJdLsxc_2F0lYc/pub?output=csv"

# Estilo CSS original
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border-radius: 0.5rem; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos desde el Excel
@st.cache_data(ttl=60) # Se actualiza cada 60 segundos
def cargar_desde_excel():
    try:
        df = pd.read_csv(SHEET_URL)
        # Asegurarnos de que las columnas existan, si no, crearlas
        for col in ['nombre', 'nivel']:
            if col not in df.columns:
                df[col] = "Jugador" if col == 'nombre' else 5
        return df.to_dict('records')
    except:
        return []

# Inicializar sesión
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_desde_excel()

if 'votos' not in st.session_state:
    st.session_state.votos = {}

# --- LÓGICA DE BALANCEO ---
def encontrar_mejor_combinacion(jugadores_presentes):
    combos = list(combinations(jugadores_presentes, 5))
    mejor_combo = None
    menor_diferencia = float('inf')
    for equipo_a in combos:
        equipo_b = [j for j in jugadores_presentes if j not in equipo_a]
        suma_a = sum(float(j['nivel']) for j in equipo_a)
        suma_b = sum(float(j['nivel']) for j in equipo_b)
        diferencia = abs(suma_a - suma_b)
        if diferencia < menor_diferencia:
            menor_diferencia = diferencia
            mejor_combo = {'equipo_a': list(equipo_a), 'equipo_b': equipo_b, 'suma_a': suma_a, 'suma_b': suma_b}
    return mejor_combo

# --- INTERFAZ ---
st.title("⚽ Fútbol 5 Mix")

tab1, tab2, tab3 = st.tabs(["👥 Jugadores", "🗳️ Votar", "⚽ Equipos"])

with tab1:
    st.subheader("Lista de Jugadores (Desde Excel)")
    if st.button("🔄 Actualizar lista del Excel"):
        st.cache_data.clear()
        st.session_state.jugadores = cargar_desde_excel()
        st.rerun()

    # Mostrar jugadores y selección de presentes
    jugadores_db = st.session_state.jugadores
    for i, j in enumerate(jugadores_db):
        col1, col2 = st.columns([1, 4])
        with col1:
            # La presencia es local de la sesión para que cada uno arme su equipo
            j['presente'] = st.checkbox("", key=f"pres_{i}")
        with col2:
            st.write(f"**{j['nombre']}** - Nivel: {j['nivel']}")

with tab3:
    presentes = [j for j in st.session_state.jugadores if j.get('presente')]
    st.write(f"Seleccionados: {len(presentes)}/10")
    
    if len(presentes) == 10:
        if st.button("Generar Mix Equilibrado"):
            res = encontrar_mejor_combinacion(presentes)
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"Equipo A ({res['suma_a']} pts)")
                for p in res['equipo_a']: st.write(f"🏃 {p['nombre']}")
            with c2:
                st.info(f"Equipo B ({res['suma_b']} pts)")
                for p in res['equipo_b']: st.write(f"🏃 {p['nombre']}")
    else:
        st.warning("Debes marcar exactamente 10 jugadores en la pestaña Jugadores.")
