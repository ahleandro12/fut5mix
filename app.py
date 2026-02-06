import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from itertools import combinations
import hashlib
import random

# CONFIGURACIÓN Y ESTILO (TU DISEÑO ORIGINAL)
st.set_page_config(page_title="Fútbol 5 Mix", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border-radius: 0.5rem; font-weight: bold; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# CONEXIÓN A TU EXCEL
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Cargamos lo que haya en el Excel para que todos vean lo mismo
        df = conn.read(ttl=0) 
        return df.to_dict('records')
    except:
        return []

def guardar_datos(lista_jugadores):
    # Esta función manda lo que hiciste en la App hacia el Excel
    df = pd.DataFrame(lista_jugadores)
    conn.update(data=df)
    st.cache_data.clear()

# Inicializar datos desde el Excel (Memoria compartida)
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = cargar_datos()

# --- INTERFAZ ORIGINAL RECONSTRUIDA ---
st.title("⚽ Fútbol 5 Mix")

tab1, tab2, tab3 = st.tabs(["👥 Jugadores", "🗳️ Votación Anónima", "⚽ Equipos"])

with tab1:
    st.subheader("Agregar Jugador desde la App")
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        nombre = st.text_input("Nombre")
    with col2:
        nivel = st.slider("Nivel", 1, 10, 5)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar"):
            if nombre:
                nuevo = {'nombre': nombre, 'nivel': nivel, 'presente': False}
                st.session_state.jugadores.append(nuevo)
                # AQUÍ SE GUARDA EN EL EXCEL PARA SIEMPRE
                guardar_datos(st.session_state.jugadores) 
                st.rerun()

    st.markdown("---")
    st.write("### Lista de Jugadores")
    for i, j in enumerate(st.session_state.jugadores):
        col_p, col_n, col_b = st.columns([1, 4, 1])
        with col_p:
            p = st.checkbox("", value=j.get('presente', False), key=f"p_{i}")
            if p != j.get('presente'):
                st.session_state.jugadores[i]['presente'] = p
                guardar_datos(st.session_state.jugadores)
        with col_n:
            st.write(f"**{j['nombre']}** - Nivel: {j['nivel']}")
        with col_b:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.jugadores.pop(i)
                guardar_datos(st.session_state.jugadores)
                st.rerun()

with tab2:
    st.subheader("Votación Anónima")
    st.info("Aquí puedes restaurar tu lógica de votación. Al finalizar, los niveles se guardarán en el Excel.")
    # (Aquí va tu código original de votación, solo recuerda llamar a guardar_datos al final)
