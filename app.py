import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# Estilo neón real aplicado
st.set_page_config(page_title="CyberVoice Control", layout="centered", page_icon="🎙️")

st.markdown("""
<style>
/* Fuente futurista desde Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

html, body, [class*="css"]  {
    background-color: #050510 !important;
    color: #39ff14 !important;
    font-family: 'Orbitron', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #00ffe7 !important;
}

.stButton>button {
    background: linear-gradient(145deg, #00ffe7, #39ff14);
    color: black;
    border: none;
    padding: 0.75em 2em;
    font-size: 16px;
    font-family: 'Orbitron', sans-serif;
    border-radius: 12px;
    box-shadow: 0 0 15px #00ffe7;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: #050510;
    color: #00ffe7;
    border: 2px solid #00ffe7;
    box-shadow: 0 0 20px #00ffe7;
}

.stImage>img {
    border: 3px solid #00ffe7;
    border-radius: 12px;
}

hr {
    border-top: 1px solid #00ffe7;
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
st.image(image, width=250, caption="CyberVoice Interface")

st.markdown("### 🗣️ Da una orden por voz")
st.caption("Presiona el botón y habla. El mensaje se enviará vía MQTT al broker.")

# Botón Bokeh para reconocimiento de voz
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

# Activador del botón
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=100,
    debounce_time=0
)

# Procesamiento de voz
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
st.markdown("<center><sub style='color:#39ff14'>CyberVoice Interface - Neon Protocol v1.0</sub></center>", unsafe_allow_html=True)
