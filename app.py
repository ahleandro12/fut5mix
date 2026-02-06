import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from itertools import combinations
import hashlib
import random

# Configuración y Estilo Original
st.set_page_config(page_title="Fútbol 5 Mix", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border-radius: 0.5rem; font-weight: bold; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos_db():
    try:
        df = conn.read(ttl=0)
        return df.to_dict('records')
    except:
        return []

def guardar_datos_db(datos):
    df = pd.DataFrame(datos)
    conn.update(data=df)
    st.cache_data.clear()

# Inicializar datos
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos_db()

# --- TABS ORIGINALES ---
st.title("⚽ Fútbol 5 Mix")
tab1, tab2, tab3 = st.tabs(["👥 Jugadores", "🗳️ Votación Anónima", "⚽ Equipos"])

with tab1:
    st.subheader("Agregar Jugador")
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1: nombre = st.text_input("Nombre")
    with col2: nivel = st.slider("Nivel", 1, 10, 5)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar"):
            if nombre:
                st.session_state.jugadores.append({'nombre': nombre, 'nivel': nivel, 'presente': False})
                guardar_datos_db(st.session_state.jugadores)
                st.rerun()

    st.markdown("---")
    for i, j in enumerate(st.session_state.jugadores):
        col_c, col_t = st.columns([1, 9])
        with col_c:
            pres = st.checkbox("", value=j.get('presente', False), key=f"p_{i}")
            if pres != j.get('presente'):
                st.session_state.jugadores[i]['presente'] = pres
                guardar_datos_db(st.session_state.jugadores)
        with col_t:
            st.write(f"**{j['nombre']}** - Nivel: {j['nivel']}")
