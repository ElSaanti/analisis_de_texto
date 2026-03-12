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
    st_lottie(animacion, height=200, key="happy")


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

        # ingles
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

    contador = dict(
        sorted(contador.items(), key=lambda x: x[1], reverse=True)
    )

    return contador, palabras_filtradas


# ---------- TRADUCTOR ----------
translator = Translator()


def traducir_texto(texto):

    try:
        traduccion = translator.translate(
            texto,
            src="es",
            dest="en"
        )
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

    for i in range(
        min(len(frases_originales),
            len(frases_traducidas))
    ):
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


# ---------- VISUAL ----------
def crear_visualizaciones(r):

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Sentimiento")

        s_norm = (r["sentimiento"] + 1) / 2

        st.progress(s_norm)

        st.write(r["sentimiento"])

        st.subheader("Subjetividad")

        st.progress(r["subjetividad"])

        st.write(r["subjetividad"])

    with col2:

        st.subheader("Palabras más frecuentes")

        if r["contador_palabras"]:

            top = dict(
                list(
                    r["contador_palabras"].items()
                )[:10]
            )

            st.bar_chart(top)

    st.subheader("Texto traducido")

    st.text(r["texto_traducido"])

    st.subheader("Frases")

    for f in r["frases"][:10]:

        blob = TextBlob(f["traducido"])

        s = blob.sentiment.polarity

        st.write(
            f["original"],
            "|",
            round(s, 2)
        )


# ---------- MODOS ----------

if modo == "Texto directo":

    texto = st.text_area(
        "Texto",
        height=200
    )

    if st.button("Analizar texto"):

        if texto.strip():

            r = procesar_texto(texto)

            crear_visualizaciones(r)

        else:

            st.warning("Escribe algo")


elif modo == "Archivo de texto":

    archivo = st.file_uploader(
        "Archivo",
        type=["txt"]
    )

    if archivo:

        contenido = archivo.read().decode()

        st.text(contenido[:500])

        if st.button("Analizar archivo"):

            r = procesar_texto(contenido)

            crear_visualizaciones(r)


st.markdown("---")
st.markdown("Hecho con Streamlit + TextBlob + Lottie")
