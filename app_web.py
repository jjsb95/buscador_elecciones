import os
import re
import streamlit as st
import pdfplumber

# Configuración de la página web
st.set_page_config(
    page_title="Padrón Electoral - UNAC 2026",
    page_icon="🗳️",
    layout="centered"
)

# Título principal de la aplicación web
st.title("🗳️ Buscador de Padrones Electorales")
st.subheader("Universidad Nacional del Callao")
st.markdown("---")

# Función optimizada con la caché de Streamlit para no releer los PDFs en cada búsqueda
@st.cache_data
def extraer_datos_padron(ruta_carpeta):
    base_datos = {}
    if not os.path.exists(ruta_carpeta):
        return base_datos
        
    archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith('.pdf')]
    
    for archivo in archivos:
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        with pdfplumber.open(ruta_completa) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if not texto:
                    continue
                
                # Extraer Mesa y Ubicación
                match_mesa = re.search(r"MESA DE\s+SUFRAGIO\s+N°\s*(\d+)", texto, re.IGNORECASE)
                num_mesa = match_mesa.group(1) if match_mesa else "No encontrada"
                
                match_ubicacion = re.search(r"Ubicación de la Mesa:\s*(.*)", texto, re.IGNORECASE)
                ubicacion_mesa = match_ubicacion.group(1).strip() if match_ubicacion else "No encontrada"
                
                # Extraer alumnos
                lineas = texto.split("\n")
                for linea in lineas:
                    match_alumno = re.match(r"^(\d+)\s+([A-Z0-9]+)\s+(.+?)\s+([A-Z]{3,4})\s+", linea)
                    if match_alumno:
                        codigo = match_alumno.group(2)
                        nombre_completo = match_alumno.group(3)
                        
                        base_datos[codigo] = {
                            "nombre": nombre_completo,
                            "mesa": num_mesa,
                            "ubicacion": ubicacion_mesa,
                            "archivo": archivo
                        }
    return base_datos

# --- CONFIGURACIÓN FIJA POR DEFECTO ---
# Se define la carpeta actual de manera interna y oculta
CARPETA_PADRONES = "."

# Intentar cargar los datos automáticamente
with st.spinner("Cargando padrón electoral... por favor espere."):
    datos_votantes = extraer_datos_padron(CARPETA_PADRONES)

# --- SECCIÓN DEL BUSCADOR ---
if datos_votantes:
    st.markdown("### 🔍 Consulta tu lugar de votación")
    
    # Campo de texto para ingresar el código
    codigo_buscar = st.text_input(
        "Ingresa tu Código Universitario:", 
        placeholder="Ej. 2426110189", 
        max_chars=15
    ).strip().upper()

    # Ejecutar búsqueda si el usuario escribe algo
    if codigo_buscar:
        if codigo_buscar in datos_votantes:
            votante = datos_votantes[codigo_buscar]
            
            st.success("🎉 ¡Elector encontrado con éxito!")
            
            # Diseño estructurado en columnas para los resultados
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**👤 Estudiante:**\n{votante['nombre']}")
                st.markdown(f"**🆔 Código:**\n{codigo_buscar}")
            
            with col2:
                st.info(f"**🗳️ Mesa de Sufragio:**\nN° {votante['mesa']}")
                st.warning(f"**📍 Ubicación de la Mesa:**\n{votante['ubicacion']}")
                
            st.caption(f"📄 *Fuente de datos: {votante['archivo']}*")
            
        else:
            st.error(f"❌ El código **'{codigo_buscar}'** no figura en el padrón electoral. Verifica que esté bien escrito.")
else:
    st.error("⚠️ No se encontraron archivos PDF en la carpeta del programa. Por favor, coloca las listas en la misma carpeta que este script.")
