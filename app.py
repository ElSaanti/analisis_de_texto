import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json


# ---------- CONFIG ----------
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# ---------- ESTILOS ----------
st.markdown("""
<style>
.metric-card {
    background: #f7f7f9;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid #e6e6e6;
    text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.metric-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #111;
}
.status-box {
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 12px;
}
.status-positive {
    background-color: #eaf7ee;
    border: 1px solid #b9e3c2;
    color: #1f6b35;
}
.status-neutral {
    background-color: #eef2f7;
    border: 1px solid #ccd6e3;
    color: #40566b;
}
.status-negative {
    background-color: #fdeeee;
    border: 1px solid #f1c0c0;
    color: #9a2d2d;
}
.small-muted {
    color: #666;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ---------- FUNCION LOTTIE ----------
def cargar_lottie(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# ---------- TITULO ----------
st.title("📝 Analizador de Texto con TextBlob")

animacion = cargar_lottie("Emoji - Happy.json")
if animacion:
    st_lottie(animacion, height=180, key="happy")

st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:

- Análisis de sentimiento y subjetividad  
- Extracción de palabras clave  
- Análisis de frecuencia de palabras  
""")


# ---------- SIDEBAR ----------
st.sidebar.title("Opciones")

modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

mostrar_traduccion = st.sidebar.checkbox("Mostrar traducción completa", value=True)
mostrar_tabla_palabras = st.sidebar.checkbox("Mostrar tabla de palabras frecuentes", value=True)


# ---------- CONTAR PALABRAS ----------
def contar_palabras(texto):

    stop_words = set([
        "a","al","algo","algunas","algunos","ante","antes","como","con","contra",
        "de","del","desde","donde","durante","el","ella","ellos","en","entre",
        "era","es","esta","este","esto","estos","ha","la","las","lo","los",
        "me","mi","mis","mucho","muy","no","nos","o","otra","otro","para",
        "pero","por","porque","que","se","si","sin","sobre","son","soy",
        "su","sus","tambien","te","tengo","tu","tus","un","una","uno","unos",
        "y","ya","yo",

        # inglés
        "the","and","is","in","it","of","to","for","with","on","this",
        "that","was","are","be","as","at","by","an","or","from","but"
    ])

    palabras = re.findall(r'\b\w+\b', texto.lower())

    palabras_filtradas = [
        p for p in palabras
        if p not in stop_words and len(p) > 2
    ]

    contador = {}

    for p in palabras_filtradas:
        contador[p] = contador.get(p, 0) + 1

    contador = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))

    return contador, palabras_filtradas


# ---------- TRADUCTOR ----------
translator = Translator()

def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src="es", dest="en")
        return traduccion.text
    except:
        return texto


# ---------- PROCESAR ----------
def procesar_texto(texto):

    texto_original = texto
    texto_ingles = traducir_texto(texto)

    blob = TextBlob(texto_ingles)

    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity

    frases_originales = [
        f.strip()
        for f in re.split(r'[.!?]+', texto_original)
        if f.strip()
    ]

    frases_traducidas = [
        f.strip()
        for f in re.split(r'[.!?]+', texto_ingles)
        if f.strip()
    ]

    frases = []

    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })

    contador, palabras = contar_palabras(texto_ingles)

    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases,
        "contador_palabras": contador,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }


# ---------- APOYO VISUAL ----------
def etiqueta_sentimiento(valor):
    if valor > 0.05:
        return "Positivo"
    elif valor < -0.05:
        return "Negativo"
    return "Neutral"

def color_sentimiento(valor):
    if valor > 0.05:
        return "status-positive"
    elif valor < -0.05:
        return "status-negative"
    return "status-neutral"


# ---------- VISUAL ----------
def crear_visualizaciones(r):

    st.markdown("## Resultados del análisis")

    total_palabras = len(r["palabras"])
    total_frases = len(r["frases"])
    sentimiento_label = etiqueta_sentimiento(r["sentimiento"])

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Sentimiento</div>
            <div class="metric-value">{r["sentimiento"]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Subjetividad</div>
            <div class="metric-value">{r["subjetividad"]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Palabras útiles</div>
            <div class="metric-value">{total_palabras}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Frases detectadas</div>
            <div class="metric-value">{total_frases}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="status-box {color_sentimiento(r["sentimiento"])}">Resultado general: {sentimiento_label}</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sentimiento")
        s_norm = (r["sentimiento"] + 1) / 2
        st.progress(float(s_norm))
        st.write(f"Valor: {r['sentimiento']:.2f}")

        st.subheader("Subjetividad")
        st.progress(float(r["subjetividad"]))
        st.write(f"Valor: {r['subjetividad']:.2f}")

    with col2:
        st.subheader("Palabras más frecuentes")
        if r["contador_palabras"]:
            top = dict(list(r["contador_palabras"].items())[:10])
            st.bar_chart(top)
        else:
            st.info("No hay suficientes palabras para mostrar.")

    if mostrar_tabla_palabras and r["contador_palabras"]:
        st.subheader("Top 10 palabras frecuentes")
        df_top = pd.DataFrame(
            list(r["contador_palabras"].items())[:10],
            columns=["Palabra", "Frecuencia"]
        )
        st.dataframe(df_top, use_container_width=True, hide_index=True)

    if mostrar_traduccion:
        st.subheader("Texto traducido")
        with st.expander("Ver traducción"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Texto original**")
                st.text(r["texto_original"])
            with c2:
                st.markdown("**Texto traducido**")
                st.text(r["texto_traducido"])

    st.subheader("Frases analizadas")

    if r["frases"]:
        for i, f in enumerate(r["frases"][:10], start=1):
            blob = TextBlob(f["traducido"])
            s = blob.sentiment.polarity

            if s > 0.05:
                estado = "Positiva"
            elif s < -0.05:
                estado = "Negativa"
            else:
                estado = "Neutral"

            with st.container():
                st.markdown(f"**Frase {i}**")
                st.write(f"Original: {f['original']}")
                st.write(f"Traducida: {f['traducido']}")
                st.caption(f"Clasificación: {estado} | Polaridad: {s:.2f}")
                st.markdown("---")
    else:
        st.info("No se detectaron frases.")


# ---------- MODOS ----------
if modo == "Texto directo":

    texto = st.text_area(
        "Texto",
        height=220,
        placeholder="Escribe o pega aquí el texto que deseas analizar..."
    )

    if st.button("Analizar texto", type="primary"):

        if texto.strip():
            with st.spinner("Analizando texto..."):
                r = procesar_texto(texto)
                crear_visualizaciones(r)
        else:
            st.warning("Escribe algo para poder analizarlo.")

elif modo == "Archivo de texto":

    archivo = st.file_uploader(
        "Archivo",
        type=["txt", "csv", "md"]
    )

    if archivo:
        contenido = archivo.read().decode("utf-8")

        with st.expander("Vista previa del archivo"):
            st.text(contenido[:800] + ("..." if len(contenido) > 800 else ""))

        if st.button("Analizar archivo", type="primary"):
            with st.spinner("Analizando archivo..."):
                r = procesar_texto(contenido)
                crear_visualizaciones(r)


# ---------- FOOTER ----------
st.markdown("---")
st.markdown('<p class="small-muted">Hecho con Streamlit + TextBlob + Lottie</p>', unsafe_allow_html=True)
