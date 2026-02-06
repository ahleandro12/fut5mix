import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import random
from itertools import combinations
import hashlib

# 1. CONFIGURACIÓN Y ESTILO (TU DISEÑO ORIGINAL)
st.set_page_config(page_title="Fútbol 5 Mix", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 0.75rem; font-size: 1.1rem; font-weight: bold; border-radius: 0.5rem; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# 2. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos_db():
    try:
        # Busca la hoja "Jugadores"
        df = conn.read(worksheet="Jugadores", ttl=0)
        return df.to_dict('records')
    except:
        return []

def guardar_datos_db(lista_jugadores):
    if lista_jugadores:
        df = pd.DataFrame(lista_jugadores)
        conn.update(worksheet="Jugadores", data=df)
        st.cache_data.clear()

# Inicializar sesión compartida
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos_db()

# --- FUNCIONES DE LÓGICA (TUS FUNCIONES) ---
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
            mejor_combo = {'equipo_a': list(equipo_a), 'equipo_b': equipo_b, 'suma_a': suma_a, 'suma_b': suma_b}
    return mejor_combo

# --- INTERFAZ ---
st.title("⚽ Fútbol 5 Mix")

tab1, tab2, tab3 = st.tabs(["👥 Jugadores", "⚽ Equipos", "📊 Historial"])

with tab1:
    st.subheader("Gestión de Plantel")
    with st.expander("➕ Agregar Nuevo Jugador"):
        col1, col2 = st.columns(2)
        with col1: nombre = st.text_input("Nombre")
        with col2: nivel = st.slider("Nivel inicial", 1, 10, 5)
        if st.button("Guardar Jugador"):
            nuevo = {'nombre': nombre, 'nivel': nivel, 'presente': False}
            st.session_state.jugadores.append(nuevo)
            guardar_datos_db(st.session_state.jugadores)
            st.rerun()

    # Mostrar lista y permitir marcar "Presente"
    st.write("### ¿Quiénes juegan hoy?")
    for i, j in enumerate(st.session_state.jugadores):
        col_p, col_n = st.columns([1, 4])
        with col_p:
            pres = st.checkbox("", value=j.get('presente', False), key=f"p_{i}")
            if pres != j.get('presente'):
                st.session_state.jugadores[i]['presente'] = pres
                guardar_datos_db(st.session_state.jugadores)
        with col_n:
            st.write(f"{j['nombre']} (Nivel {j['nivel']})")

with tab2:
    presentes = [j for j in st.session_state.jugadores if j.get('presente')]
    st.write(f"Jugadores listos: {len(presentes)}/10")
    if len(presentes) == 10:
        if st.button("¡Generar Mix Equilibrado!"):
            res = encontrar_mejor_combinacion(presentes)
            col_a, col_b = st.columns(2)
            with col_a:
                st.success(f"Equipo A ({res['suma_a']} pts)")
                for p in res['equipo_a']: st.write(f"🏃 {p['nombre']}")
            with col_b:
                st.info(f"Equipo B ({res['suma_b']} pts)")
                for p in res['equipo_b']: st.write(f"🏃 {p['nombre']}")
    else:
        st.warning("Faltan jugadores para completar los 10.")

st.sidebar.button("🔄 Forzar Sincronización", on_click=lambda: st.cache_data.clear())
