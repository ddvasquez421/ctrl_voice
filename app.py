import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# Estilo cibernético aplicado globalmente
st.set_page_config(page_title="CyberVoice Control", layout="centered", page_icon="🎙️")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"]  {
        background-color: #0f0f1a;
        color: #00ffcc;
        font-family: 'Orbitron', sans-serif;
    }
    h1, h2, h3, h4, h5 {
        color: #00ffff;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button {
        background-color: #1f1f2e;
        color: #00ffcc;
        border: 1px solid #00ffcc;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        font-size: 16px;
    }
    .st-bf, .st-cg, .stTextInput>div>div>input {
        background-color: #1f1f2e !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
    }
    .bk-btn {
        background-color: #222244 !important;
        color: #00ffcc !important;
        font-family: 'Orbitron', sans-serif !important;
        border-radius: 8px;
        border: 1px solid #00ffff;
    }
</style>
""", unsafe_allow_html=True)

# MQTT Setup
def on_publish(client, userdata, result):
    print("Dato publicado.\n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.success(f"📡 Mensaje recibido: `{message_received}`")

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# Interfaz
st.title("🎙️ INTERFACES MULTIMODALES")
st.subheader("🧬 Control por Voz con MQTT")

# Imagen
image = Image.open("voice_ctrl.jpg")
st.image(image, width=220, caption="CyberVoice Interface")

st.markdown("### 🗣️ Da una orden por voz")
st.caption("Presiona el botón y habla. El mensaje se enviará vía MQTT al broker.")

# Botón de reconocimiento de voz (JavaScript)
stt_button = Button(label="🎤 Iniciar reconocimiento", width=250)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value !== "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Escucha y captura resultados
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    texto_voz = result.get("GET_TEXT").strip()
    st.success(f"🎧 Escuchado: `{texto_voz}`")
    
    # Publicar por MQTT
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto_voz})
    client1.publish("voice_ctrl", message)

    # Crear carpeta temporal si no existe
    try:
        os.mkdir("temp")
    except:
        pass

# Footer
st.markdown("---")
st.markdown("<center><sub>CyberVoice Interface - Powered by MQTT & JS Speech API</sub></center>", unsafe_allow_html=True)
