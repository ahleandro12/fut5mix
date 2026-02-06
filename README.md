# ⚽ Fútbol 5 Mix - Balanceador Inteligente de Equipos

Aplicación web para balancear equipos de fútbol 5 con votación anónima y ajuste automático de niveles.

## 🚀 Despliegue en Streamlit Cloud (GRATIS)

### Paso 1: Sube los archivos a GitHub

1. Ve a [github.com](https://github.com) y crea una cuenta (si no tienes)
2. Crea un nuevo repositorio llamado `futbol5-mix`
3. Sube estos 2 archivos:
   - `app.py`
   - `requirements.txt`

### Paso 2: Despliega en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Click en "New app"
4. Selecciona tu repositorio `futbol5-mix`
5. Main file path: `app.py`
6. Click en "Deploy"

¡Listo! Tu app estará online en 2-3 minutos.

## 💻 Ejecutar en local (opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run app.py
```

La app se abrirá en `http://localhost:8501`

## ✨ Características

- ✅ **Votación Anónima**: Cada jugador vota desde su dispositivo sin revelar identidad
- ✅ **Balanceo Inteligente**: Algoritmo que encuentra la combinación más equitativa
- ✅ **Historial Completo**: Registro de todos los partidos jugados
- ✅ **Ajuste Automático**: Los niveles se actualizan según resultados
- ✅ **Compartir WhatsApp**: Exporta los equipos fácilmente
- ✅ **Estadísticas**: Win rate, goles favor/contra por jugador

## 📱 Cómo usar

1. **Agregar Jugadores**: Ingresa nombre y nivel inicial (1-10)
2. **Votar Niveles**: Inicia votación anónima para calibrar niveles
3. **Seleccionar Presentes**: Marca quiénes juegan hoy (10 jugadores)
4. **Generar Equipos**: El algoritmo crea el mix más equitativo
5. **Registrar Resultado**: Ingresa goles y el sistema ajusta niveles automáticamente

## 🔐 Privacidad

- Los votos son 100% anónimos
- Cada dispositivo genera un ID único
- Nadie puede ver quién votó qué
- Solo se muestra el promedio final

## 📊 Ajuste Automático de Niveles

El sistema sube/baja niveles automáticamente cuando:
- Un equipo más débil gana por 3+ goles → **Sube nivel (+1)**
- Un equipo más fuerte pierde por 3+ goles → **Baja nivel (-1)**

Esto hace que los equipos sean cada vez más equilibrados.

## 🎯 Tecnologías

- Python 3.10+
- Streamlit
- Pandas
