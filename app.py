import streamlit as st
import pandas as pd
import json
from datetime import datetime
import random
from itertools import combinations
import hashlib

# Configuración de la página
st.set_page_config(
    page_title="Fútbol 5 Mix",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #059669 0%, #047857 100%);
    }
    h1, h2, h3 {
        color: #10b981 !important;
    }
    .stMarkdown {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session_state
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = []

if 'historial' not in st.session_state:
    st.session_state.historial = []

if 'votacion_activa' not in st.session_state:
    st.session_state.votacion_activa = None

if 'mi_usuario_id' not in st.session_state:
    # Generar ID único basado en sesión de Streamlit
    st.session_state.mi_usuario_id = f"user_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"

if 'ya_vote' not in st.session_state:
    st.session_state.ya_vote = False

if 'mis_votos' not in st.session_state:
    st.session_state.mis_votos = {}

# Funciones auxiliares
def generar_combinaciones(jugadores, n=5):
    """Genera todas las combinaciones posibles de n jugadores"""
    return list(combinations(jugadores, n))

def encontrar_mejor_combinacion(jugadores_presentes):
    """Encuentra la combinación más equitativa de equipos"""
    combos = generar_combinaciones(jugadores_presentes, 5)
    mejor_combo = None
    menor_diferencia = float('inf')
    
    for equipo_a in combos:
        equipo_b = [j for j in jugadores_presentes if j not in equipo_a]
        suma_a = sum(j['nivel'] for j in equipo_a)
        suma_b = sum(j['nivel'] for j in equipo_b)
        diferencia = abs(suma_a - suma_b)
        
        if diferencia < menor_diferencia:
            menor_diferencia = diferencia
            mejor_combo = {
                'equipo_a': list(equipo_a),
                'equipo_b': equipo_b,
                'suma_a': suma_a,
                'suma_b': suma_b,
                'diferencia': diferencia
            }
    
    return mejor_combo

def ajustar_niveles_por_resultado(jugadores, partido):
    """Ajusta niveles automáticamente según resultado del partido"""
    if partido['ganador'] == 'Empate':
        return jugadores
    
    dif_goles = abs(partido['goles_a'] - partido['goles_b'])
    
    # Solo ajustar si hay goleada (3+ goles de diferencia)
    if dif_goles < 3:
        return jugadores
    
    jugadores_actualizados = []
    for jugador in jugadores:
        j = jugador.copy()
        
        # Equipo débil ganó por goleada -> subir nivel
        if (partido['ganador'] == 'A' and 
            j['nombre'] in partido['equipo_a'] and 
            partido['nivel_a'] < partido['nivel_b']):
            j['nivel'] = min(10, j['nivel'] + 1)
        
        elif (partido['ganador'] == 'B' and 
              j['nombre'] in partido['equipo_b'] and 
              partido['nivel_b'] < partido['nivel_a']):
            j['nivel'] = min(10, j['nivel'] + 1)
        
        # Equipo fuerte perdió por goleada -> bajar nivel
        elif (partido['ganador'] == 'B' and 
              j['nombre'] in partido['equipo_a'] and 
              partido['nivel_a'] > partido['nivel_b']):
            j['nivel'] = max(1, j['nivel'] - 1)
        
        elif (partido['ganador'] == 'A' and 
              j['nombre'] in partido['equipo_b'] and 
              partido['nivel_b'] > partido['nivel_a']):
            j['nivel'] = max(1, j['nivel'] - 1)
        
        jugadores_actualizados.append(j)
    
    return jugadores_actualizados

# HEADER
st.markdown("# ⚽ Fútbol 5 Mix")
st.markdown("### Balanceador Inteligente de Equipos")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["👥 Jugadores", "🗳️ Votación", "⚽ Generar Equipos", "📊 Historial"])

# ============ TAB 1: JUGADORES ============
with tab1:
    st.markdown("## Agregar Jugador")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        nombre = st.text_input("Nombre del jugador", key="nombre_input")
    
    with col2:
        nivel = st.selectbox("Nivel", list(range(1, 11)), index=4, key="nivel_input")
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar"):
            if nombre.strip():
                nuevo_jugador = {
                    'id': len(st.session_state.jugadores) + 1,
                    'nombre': nombre.strip(),
                    'nivel': nivel,
                    'presente': False,
                    'partidos_ganados': 0,
                    'partidos_perdidos': 0,
                    'goles_favor': 0,
                    'goles_contra': 0
                }
                st.session_state.jugadores.append(nuevo_jugador)
                st.success(f"✅ {nombre} agregado!")
                st.rerun()
            else:
                st.error("Ingresa un nombre")
    
    st.markdown("---")
    st.markdown("## Lista de Jugadores")
    
    presentes = sum(1 for j in st.session_state.jugadores if j['presente'])
    st.markdown(f"### Presentes: **{presentes}/10**")
    
    if len(st.session_state.jugadores) == 0:
        st.info("No hay jugadores registrados. ¡Agrega el primero!")
    else:
        for idx, jugador in enumerate(st.session_state.jugadores):
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                presente = st.checkbox(
                    "✓", 
                    value=jugador['presente'],
                    key=f"presente_{jugador['id']}",
                    label_visibility="collapsed"
                )
                if presente != jugador['presente']:
                    st.session_state.jugadores[idx]['presente'] = presente
                    st.rerun()
            
            with col2:
                total_partidos = jugador['partidos_ganados'] + jugador['partidos_perdidos']
                win_rate = (jugador['partidos_ganados'] / total_partidos * 100) if total_partidos > 0 else 0
                
                stats = ""
                if total_partidos > 0:
                    stats = f" - {win_rate:.0f}% victorias ({jugador['partidos_ganados']}G {jugador['partidos_perdidos']}P)"
                
                st.markdown(f"**{jugador['nombre']}** - Nivel {jugador['nivel']}{stats}")
            
            with col3:
                if total_partidos > 0:
                    st.markdown(f"⚽ {jugador['goles_favor']}-{jugador['goles_contra']}")
            
            with col4:
                if st.button("🗑️", key=f"delete_{jugador['id']}"):
                    st.session_state.jugadores = [j for j in st.session_state.jugadores if j['id'] != jugador['id']]
                    st.rerun()

# ============ TAB 2: VOTACIÓN ============
with tab2:
    st.markdown("## 🗳️ Sistema de Votación Anónima")
    
    presentes_votacion = [j for j in st.session_state.jugadores if j['presente']]
    
    if st.session_state.votacion_activa is None:
        st.info("No hay votación activa")
        
        if len(presentes_votacion) < 2:
            st.warning("⚠️ Necesitas al menos 2 jugadores presentes para iniciar votación")
        else:
            if st.button("🚀 Iniciar Votación Anónima", type="primary"):
                st.session_state.votacion_activa = {
                    'id': datetime.now().timestamp(),
                    'jugadores': presentes_votacion,
                    'votos': {},
                    'fecha_inicio': datetime.now().isoformat()
                }
                st.session_state.ya_vote = False
                st.session_state.mis_votos = {}
                st.success("✅ Votación iniciada! Comparte esta página con todos para que voten.")
                st.rerun()
    
    else:
        # Votación activa
        st.success("✅ Votación en curso")
        
        votantes = len(st.session_state.votacion_activa['votos'])
        st.markdown(f"### 📊 {votantes} persona(s) han votado")
        
        if not st.session_state.ya_vote:
            st.markdown("---")
            st.markdown("### 🔒 Tu voto es 100% anónimo")
            st.info("Nadie sabrá cómo votaste. Vota el nivel de cada jugador según tu opinión.")
            
            st.markdown("---")
            
            for jugador in st.session_state.votacion_activa['jugadores']:
                st.markdown(f"#### {jugador['nombre']} (Nivel actual: {jugador['nivel']})")
                
                voto = st.slider(
                    "Nivel",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.mis_votos.get(jugador['id'], jugador['nivel']),
                    key=f"voto_{jugador['id']}",
                    label_visibility="collapsed"
                )
                
                st.session_state.mis_votos[jugador['id']] = voto
            
            st.markdown("---")
            
            votos_completos = len(st.session_state.mis_votos) == len(st.session_state.votacion_activa['jugadores'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    f"✅ Enviar Mi Voto ({len(st.session_state.mis_votos)}/{len(st.session_state.votacion_activa['jugadores'])})",
                    disabled=not votos_completos,
                    type="primary"
                ):
                    st.session_state.votacion_activa['votos'][st.session_state.mi_usuario_id] = st.session_state.mis_votos.copy()
                    st.session_state.ya_vote = True
                    st.success("¡Tu voto fue registrado de forma anónima!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar Votación"):
                    st.session_state.votacion_activa = None
                    st.session_state.ya_vote = False
                    st.session_state.mis_votos = {}
                    st.rerun()
        
        else:
            st.success("✅ Ya votaste! Esperando a que más jugadores voten...")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🏁 Finalizar y Calcular Resultados", type="primary"):
                    if votantes < 2:
                        st.error("Se necesitan al menos 2 votantes")
                    else:
                        # Calcular promedios
                        for jugador in st.session_state.votacion_activa['jugadores']:
                            votos_recibidos = []
                            for votos_usuario in st.session_state.votacion_activa['votos'].values():
                                if jugador['id'] in votos_usuario:
                                    votos_recibidos.append(votos_usuario[jugador['id']])
                            
                            if votos_recibidos:
                                promedio = round(sum(votos_recibidos) / len(votos_recibidos))
                                
                                # Actualizar nivel
                                for idx, j in enumerate(st.session_state.jugadores):
                                    if j['id'] == jugador['id']:
                                        st.session_state.jugadores[idx]['nivel'] = promedio
                        
                        st.session_state.votacion_activa = None
                        st.session_state.ya_vote = False
                        st.session_state.mis_votos = {}
                        
                        st.success(f"✅ Votación finalizada! {votantes} personas votaron. Niveles actualizados.")
                        st.rerun()
            
            with col2:
                if st.button("❌ Cancelar Votación"):
                    st.session_state.votacion_activa = None
                    st.session_state.ya_vote = False
                    st.session_state.mis_votos = {}
                    st.rerun()

# ============ TAB 3: GENERAR EQUIPOS ============
with tab3:
    st.markdown("## ⚽ Generar Equipos Balanceados")
    
    presentes_equipos = [j for j in st.session_state.jugadores if j['presente']]
    
    st.markdown(f"### Jugadores presentes: **{len(presentes_equipos)}/10**")
    
    if len(presentes_equipos) != 10:
        st.warning("⚠️ Debes seleccionar exactamente 10 jugadores en la pestaña 'Jugadores'")
    else:
        if st.button("🎲 Generar Mix Equitativo", type="primary"):
            with st.spinner("Calculando la mejor combinación..."):
                resultado = encontrar_mejor_combinacion(presentes_equipos)
                st.session_state.equipos_generados = resultado
            st.success("¡Equipos generados!")
            st.rerun()
        
        if 'equipos_generados' in st.session_state:
            equipos = st.session_state.equipos_generados
            
            st.markdown("---")
            st.markdown("## 🏆 EQUIPOS BALANCEADOS")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🟢 EQUIPO A")
                st.markdown(f"**Total: {equipos['suma_a']} puntos**")
                for j in equipos['equipo_a']:
                    st.markdown(f"- **{j['nombre']}** (Nivel {j['nivel']})")
            
            with col2:
                st.markdown("### ⚪ EQUIPO B")
                st.markdown(f"**Total: {equipos['suma_b']} puntos**")
                for j in equipos['equipo_b']:
                    st.markdown(f"- **{j['nombre']}** (Nivel {j['nivel']})")
            
            st.markdown("---")
            st.markdown(f"### Diferencia: **{equipos['diferencia']} punto(s)**")
            
            # Copiar para WhatsApp
            texto_whatsapp = f"""⚽ EQUIPOS CONFIRMADOS ⚽

🟢 EQUIPO A:
{chr(10).join(f"• {j['nombre']}" for j in equipos['equipo_a'])}

⚪ EQUIPO B:
{chr(10).join(f"• {j['nombre']}" for j in equipos['equipo_b'])}"""
            
            st.text_area("📱 Copiar para WhatsApp:", texto_whatsapp, height=200)
            
            # Registrar resultado
            st.markdown("---")
            st.markdown("### 📊 Registrar Resultado del Partido")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                goles_a = st.number_input("Goles Equipo A", min_value=0, value=0, step=1)
            
            with col2:
                goles_b = st.number_input("Goles Equipo B", min_value=0, value=0, step=1)
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Guardar"):
                    partido = {
                        'id': datetime.now().timestamp(),
                        'fecha': datetime.now().strftime("%d/%m/%Y"),
                        'equipo_a': [j['nombre'] for j in equipos['equipo_a']],
                        'equipo_b': [j['nombre'] for j in equipos['equipo_b']],
                        'goles_a': goles_a,
                        'goles_b': goles_b,
                        'nivel_a': equipos['suma_a'],
                        'nivel_b': equipos['suma_b'],
                        'ganador': 'A' if goles_a > goles_b else 'B' if goles_b > goles_a else 'Empate'
                    }
                    
                    # Actualizar estadísticas
                    for idx, j in enumerate(st.session_state.jugadores):
                        if j['nombre'] in partido['equipo_a']:
                            st.session_state.jugadores[idx]['partidos_ganados'] += (1 if goles_a > goles_b else 0)
                            st.session_state.jugadores[idx]['partidos_perdidos'] += (1 if goles_a < goles_b else 0)
                            st.session_state.jugadores[idx]['goles_favor'] += goles_a
                            st.session_state.jugadores[idx]['goles_contra'] += goles_b
                        
                        elif j['nombre'] in partido['equipo_b']:
                            st.session_state.jugadores[idx]['partidos_ganados'] += (1 if goles_b > goles_a else 0)
                            st.session_state.jugadores[idx]['partidos_perdidos'] += (1 if goles_b < goles_a else 0)
                            st.session_state.jugadores[idx]['goles_favor'] += goles_b
                            st.session_state.jugadores[idx]['goles_contra'] += goles_a
                    
                    # Ajustar niveles automáticamente
                    st.session_state.jugadores = ajustar_niveles_por_resultado(
                        st.session_state.jugadores, 
                        partido
                    )
                    
                    st.session_state.historial.append(partido)
                    st.success("✅ Resultado guardado! Los niveles se han ajustado automáticamente.")
                    st.rerun()

# ============ TAB 4: HISTORIAL ============
with tab4:
    st.markdown("## 📊 Historial de Partidos")
    
    if len(st.session_state.historial) == 0:
        st.info("No hay partidos registrados todavía")
    else:
        for partido in st.session_state.historial:
            with st.expander(f"🗓️ {partido['fecha']} - {partido['goles_a']} vs {partido['goles_b']}"):
                col1, col2 = st.columns(2)
                
                ganador_emoji = "🏆" if partido['ganador'] == 'A' else "🥈" if partido['ganador'] == 'B' else "⚖️"
                ganador_texto = f"Ganó Equipo {partido['ganador']}" if partido['ganador'] != 'Empate' else 'Empate'
                
                st.markdown(f"### {ganador_emoji} {ganador_texto}")
                st.markdown(f"## {partido['goles_a']} - {partido['goles_b']}")
                
                with col1:
                    st.markdown(f"**🟢 Equipo A ({partido['nivel_a']} pts)**")
                    for nombre in partido['equipo_a']:
                        st.markdown(f"• {nombre}")
                
                with col2:
                    st.markdown(f"**⚪ Equipo B ({partido['nivel_b']} pts)**")
                    for nombre in partido['equipo_b']:
                        st.markdown(f"• {nombre}")

# Footer
st.markdown("---")
st.markdown("### 💡 Características:")
st.markdown("""
- ✅ Votación 100% anónima para definir niveles
- ✅ Algoritmo que genera el mix más equitativo posible
- ✅ Historial de partidos con estadísticas
- ✅ Ajuste automático de niveles según resultados
- ✅ Compartir equipos por WhatsApp
""")
