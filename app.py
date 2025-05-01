import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# Configuración de página
st.set_page_config(
    page_title="CyberVoice Control",
    page_icon="🧠",
    layout="centered"
)

# Estilo visual neón + fondo animado
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

body {
    background-color: black !important;
    font-family: 'Orbitron', sans-serif;
    color: #39ff14 !important;
    overflow: hidden;
}

html {
    background: url('https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif') no-repeat center center fixed;
    background-size: cover;
}

h1, h2, h3, h4 {
    color: #00ffe7 !important;
    text-shadow: 0 0 5px #00ffe7;
}

.stButton>button {
    background: transparent;
    border: 2px solid #39ff14;
    color: #39ff14;
    padding: 0.75em 2em;
    font-size: 16px;
    font-family: 'Orbitron', sans-serif;
    border-radius: 12px;
    box-shadow: 0 0 10px #39ff14, 0 0 20px #00ffe7;
    transition: all 0.4s ease-in-out;
}

.stButton>button:hover {
    background-color: #00ffe7;
    color: black;
    box-shadow: 0 0 25px #00ffe7;
}

.stImage>img {
    border-radius: 16px;
    box-shadow: 0 0 20px #00ffe7;
    border: 2px solid #00ffe7;
}

hr {
    border-top: 1px solid #00ffe7;
}

small, footer {
    color: #39ff14 !important;
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

# Imagen decorativa
image = Image.open("roboto.png")
st.image(image, width=280, caption="CyberVoice Interface")

st.markdown("## 🗣️ Da una orden por voz")
st.caption("Presiona el botón y habla. El mensaje se enviará vía MQTT al broker.")

# Botón de reconocimiento de voz
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

# Escuchar el evento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

# Publicar el mensaje de voz
if result and "GET_TEXT" in result:
    texto_voz = result.get("GET_TEXT").strip()
    st.success(f"🎧 Escuchado: `{texto_voz}`")
    
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": texto_voz})
    client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass

st.markdown("---")
st.markdown("<center><small>🧠 CyberVoice Interface - <em>Neon Protocol v1.1</em></small></center>", unsafe_allow_html=True)
