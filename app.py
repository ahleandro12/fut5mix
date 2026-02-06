import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import random
from itertools import combinations
import hashlib

# CONFIGURACIÓN ORIGINAL
st.set_page_config(
    page_title="Fútbol 5 Mix",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS ORIGINAL
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 0.75rem; font-size: 1.1rem; font-weight: bold; border-radius: 0.5rem; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        return df.to_dict('records')
    except:
        return []

def guardar_datos(lista_jugadores):
    df = pd.DataFrame(lista_jugadores)
    conn.update(worksheet="Sheet1", data=df)
    st.cache_data.clear()

# Inicializar sesión compartida
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos()

# --- FUNCIONES ORIGINALES ---
def encontrar_mejor_combinacion(jugadores_presentes):
    combos = list(combinations(jugadores_presentes, 5))
    mejor_combo = None
    menor_diferencia = float('inf')
    for equipo_a in combos:
        equipo_b = [j for j in jugadores_presentes if j not in equipo_a]
        suma_a = sum(j['nivel'] for j in equipo_a)
        suma_b = sum(j['nivel'] for j in equipo_b)
        diferencia = abs(suma_a - suma_b)
        if diferencia < menor_diferencia:
            menor_diferencia = diferencia
            mejor_combo = {'equipo_a': list(equipo_a), 'equipo_b': equipo_b, 'suma_a': suma_a, 'suma_b': suma_b, 'diferencia': diferencia}
    return mejor_combo

# --- INTERFAZ (Tu diseño original) ---
st.markdown("# ⚽ Fútbol 5 Mix")
tab1, tab2, tab3, tab4 = st.tabs(["👥 Jugadores", "🗳️ Votación", "⚽ Generar Equipos", "📊 Historial"])

with tab1:
    st.markdown("## Agregar Jugador")
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        nombre = st.text_input("Nombre del jugador")
    with col2:
        nivel = st.selectbox("Nivel", list(range(1, 11)), index=4)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar"):
            if nombre.strip():
                nuevo = {'id': len(st.session_state.jugadores)+1, 'nombre': nombre, 'nivel': nivel, 'presente': False, 
                         'partidos_ganados': 0, 'partidos_perdidos': 0, 'goles_favor': 0, 'goles_contra': 0}
                st.session_state.jugadores.append(nuevo)
                guardar_datos(st.session_state.jugadores) # GUARDAR EN EXCEL
                st.rerun()

    # Mostrar lista
    for idx, jugador in enumerate(st.session_state.jugadores):
        col1, col2 = st.columns([1, 5])
        with col1:
            pres = st.checkbox("✓", value=jugador['presente'], key=f"p_{idx}")
            if pres != jugador['presente']:
                st.session_state.jugadores[idx]['presente'] = pres
                guardar_datos(st.session_state.jugadores)
                st.rerun()
        with col2:
            st.write(f"**{jugador['nombre']}** - Nivel {jugador['nivel']}")

# (El resto de pestañas siguen igual, solo recuerda llamar a guardar_datos() cuando cambies niveles)
