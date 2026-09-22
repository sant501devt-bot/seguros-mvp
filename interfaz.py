import streamlit as st
import requests
import os

# Configuración de página con ícono y layout ancho
st.set_page_config(
    page_title="Auditoría de Pólizas AI",
    page_icon="",
    layout="wide"
)

# URL del backend: usa la variable de entorno BACKEND_URL si existe (para cuando
# esté desplegado en internet), o localhost si estás probando en tu PC.
# En Streamlit Cloud, esto se configura en "Secrets" -- lo vemos en el siguiente paso.
BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))

# BARRA LATERAL (SIDEBAR) 
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/shield.png", width=70)
    st.title("SaaS Auditoría")
    st.caption("v1.0.0 | MVP P&C Insurance")
    st.markdown("---")
    
    st.subheader("Configuración")
    nombre_proyecto = st.text_input("Nombre del Cliente/Proyecto", "Cliente_Demo_01")
    
    st.markdown("---")
    st.markdown("### 🟢 Estado del Sistema")
    st.success("API Backend: Conectado")
    st.info("Modelo: Gemini 2.5 Flash")

# ÁREA PRINCIPAL 
st.title("Auditoría Inteligente de Pólizas")
st.write("Sube un documento contractual en PDF para extraer análisis de coberturas, riesgos y recomendaciones automatizadas.")

# Zona de carga de archivos en 2 columnas
col_upload, col_info = st.columns([2, 1])

with col_upload:
    archivo_pdf = st.file_uploader("Arrastra tu póliza en formato PDF aquí", type=["pdf"])

with col_info:
    st.info("""
    **💡 Consejos para la demo:**
    * Soporta pólizas de autos, hogar y vida.
    * Asegúrate de que el PDF sea legible.
    * El proceso toma entre 3 y 8 segundos.
    """)

# Botón de ejecución
if st.button("Ejecutar Auditoría Completa", use_container_width=True) and archivo_pdf:
    with st.spinner("La Inteligencia Artificial está analizando el documento..."):
        try:
            # Petición HTTP al backend FastAPI
            files = {"file": (archivo_pdf.name, archivo_pdf.getvalue(), "application/pdf")}
            url = f"{BACKEND_URL}/auditar?nombre_proyecto={nombre_proyecto}"
            response = requests.post(url, files=files)

            if response.status_code == 200:
                resultado = response.json().get("analisis", {})
                st.success("¡Análisis finalizado con éxito!")
                st.markdown("---")

                # MÉTRICAS PRINCIPALES 
                st.subheader("Resumen del Análisis")
                m1, m2, m3 = st.columns(3)
                
                m1.metric("Número de Póliza", resultado.get("numero_poliza", "N/A"))
                
                score = resultado.get("score_salud", 0)
                m2.metric("Score de Salud", f"{score}/100", delta=f"{score - 50} pts vs Promedio", delta_color="normal")
                
                riesgos = resultado.get("matriz_riesgos", [])
                m3.metric("Riesgos Identificados", len(riesgos))

                st.markdown("---")

                # DETALLE DE RIESGOS EN COLUMNAS/CARDS
                st.subheader("Matriz de Riesgos Detectados")
                
                if riesgos:
                    for item in riesgos:
                        nivel = item.get("nivel_riesgo", "BAJO").upper()
                        hallazgo = item.get("hallazgo", "")
                        recomendacion = item.get("recomendacion", "")

                        # Color dinámico según el nivel de riesgo
                        if nivel == "ALTO":
                            st.error(f"**[RIESGO ALTO]** {hallazgo}\n\n*Recomendación: {recomendacion}*")
                        elif nivel == "MEDIO":
                            st.warning(f"**[RIESGO MEDIO]** {hallazgo}\n\n*Recomendación: {recomendacion}*")
                        else:
                            st.info(f"**[RIESGO BAJO]** {hallazgo}\n\n*Recomendación: {recomendacion}*")
                else:
                    st.write("No se detectaron cláusulas de riesgo crítico.")

                # JSON COMPLETO EN PESTAÑA DESPLEGABLE 
                with st.expander("Ver estructura JSON completa"):
                    st.json(resultado)

            else:
                st.error(f"Error en el servidor: Código {response.status_code}")

        except Exception as e:
            st.error(f"No se pudo conectar con el servidor backend: {e}")