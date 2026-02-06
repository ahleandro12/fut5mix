import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import combinations # para los equipos

# CONFIGURACIÓN Y ESTILO ORIGINAL
st.set_page_config(page_title="Fútbol 5 Mix", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 0.75rem; font-size: 1.1rem; font-weight: bold; border-radius: 0.5rem; }
    h1, h2, h3 { color: #10b981 !important; }
    .stMarkdown { color: white; }
</style>
""", unsafe_allow_html=True)

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        # Intenta leer la primera pestaña
        return conn.read(ttl=0)
    except Exception:
        # Si falla, devuelve un DataFrame vacío con las columnas necesarias
        return pd.DataFrame(columns=['nombre', 'nivel', 'presente', 'ganados', 'perdidos'])

# Cargar jugadores al inicio
df_jugadores = cargar_datos()

# --- AQUÍ EMPIEZA TU APP ---
st.title("⚽ Fútbol 5 Mix")

# Ejemplo de cómo guardar cuando agregas a alguien:
# new_data = pd.concat([df_jugadores, pd.DataFrame([nuevo_jugador])], ignore_index=True)
# conn.update(data=new_data)
# st.cache_data.clear()

st.info("Configuración de base de datos lista. Si ya pusiste el link en Secrets, la app cargará tus jugadores.")
