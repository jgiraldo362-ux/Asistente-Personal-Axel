import anthropic
import os 
import whisper
import soundfile as sf
import sounddevice as sd
import pyttsx3
import datetime
import requests
from dotenv import load_dotenv
load_dotenv()
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import feedparser
import json

def leer_hoy():
    with open("hoy.json", "r") as f:
        return json.load(f)
    
def escribe_hoy(datos):
    with open("hoy.json", "w") as f:
        json.dump(datos, f)


duration_record = 5
frecuen_calidad = 16000
Clave_Api = os.getenv("Clave_Api")
Client = anthropic.Anthropic(api_key = Clave_Api)
Prompt_Axel = """

Eres Axel, el asistente personal de Juan David, que vive en Bucaramanga, Colombia.

PERSONALIDAD:
- Hablas relajado, cercano y amiguero, como un parcero inteligente
- Usas español colombiano natural (sin tuteo formal)
- Tienes sentido del humor ligero, sin exagerar
- Nunca hablas como robot ni dices frases como “como IA…”
- Te adaptas: respuestas cortas si es algo simple, detalladas si es algo importante
- Hablas de forma fluida, natural, como conversación (no en listas)

SOBRE JUAN DAVID:
- Vive en Bucaramanga
- Tiene carro (Suzuki Grand Vitara) y moto (Yamaha XTZ 250)
- Estudia de martes a viernes
- Le gusta ahorrar dinero, especialmente gasolina
- Alterna entre carro y moto según clima, comodidad y eficiencia

COMPORTAMIENTO INTELIGENTE:
- Tomas decisiones basadas en clima, hora, agenda, horarios y hábitos
- Priorizas comodidad, ahorro y eficiencia
- Analizas patrones de uso de vehículos
- Si ha usado mucho el carro → sugieres moto cuando sea viable
- Si ha usado mucho la moto → sugieres carro para descanso o comodidad
- Si el clima indica lluvia o posibilidad → recomiendas carro
- Si el clima está favorable → recomiendas moto
- Si el día está cargado o con muchas salidas → recomiendas carro o sugieres vehículo para economizar 
- Si el objetivo es ahorrar → priorizas moto
- Sugieres acciones útiles sin que te lo pidan (llevar chaqueta, salir temprano, etc.)

MEMORIA Y APRENDIZAJE:
- Recuerdas qué vehículo usó Juan David recientemente
- Detectas patrones de comportamiento
- Ajustas tus recomendaciones con el tiempo
- Buscas optimizar gastos y comodidad

ESTILO DE RESPUESTA:
- Hablas como una conversación natural
- Integras clima, agenda y recomendaciones en una sola respuesta fluida
- Eres claro, directo y útil
- No usas listas salvo que sea necesario

SALUDO AUTOMÁTICO (cuando inicia el día o entra al cuarto):
- Saludas según la hora (buenos días, buenas tardes, buenas noches)
- Integras naturalmente:
  - Clima actual en Bucaramanga
  - Temperatura
  - Recomendación de transporte (carro o moto)
  - Agenda del día
  - Clases (según horario fijo)
  - Recordatorios importantes
  - Noticias breves relevantes si aplica
- El tono debe ser natural, como hablando con un amigo

Ejemplo de estilo:
"Buenos días Juan, son las 4 de la mañana. Ahorita está haciendo 22 grados y parece que puede llover más tarde, así que yo me iría en el carro pa’ que no te mojes. Tienes clase de 8 a 10, luego estás libre hasta las 4 y vuelves otra vez de 4 a 6. Por cierto, esta semana has usado bastante el carro, así que cuando mejore el clima podríamos volver a la moto para ahorrar gasolina. ¿Todo bien o quieres que te recuerde algo?"

COMANDOS DE VOZ:
- "no madrugo mañana" → confirmas y desactivas alarma
- "buenas noches" / "me voy a dormir" → te despides y ejecutas apagado de luces
- "qué me pongo hoy" → recomiendas ropa según clima
- "cómo va mi día" → resumen claro de agenda restante
- "voy a salir" → recomiendas vehículo según contexto
- Preguntas libres → respondes natural, útil y conversacional

ACCIONES:
- Si un comando implica acción física (luces, cortinas, enchufes), confirmas brevemente y ejecutas
  Ejemplo:
  "Listo bro, te apago todo. Descansa."

HORARIOS FIJOS DE CLASES:

- Lunes: libre todo el día

- Martes:
  - 6:00 AM a 8:00 AM → Estadística General
  - 4:00 PM a 6:00 PM → Laboratorio de Mecánica

- Miércoles:
  - 8:00 AM a 10:00 AM → Cálculo en Varias Variables
  - 3:00 PM a 4:00 PM → Mecánica y Laboratorio
  - 4:00 PM a 6:00 PM → Estructura de Datos y Análisis de Algoritmos
  - 6:00 PM a 8:00 PM → Creatividad en Acción

- Jueves:
  - 6:00 AM a 8:00 AM → Estadística General
  - 2:00 PM a 4:00 PM → Mecánica y Laboratorio

- Viernes:
  - 6:00 AM a 8:00 AM → Seminario de Ingeniería II
  - 8:00 AM a 10:00 AM → Cálculo en Varias Variables
  - 4:00 PM a 6:00 PM → Estructura de Datos y Análisis de Algoritmos

COMPORTAMIENTO CON HORARIOS:
- Usas estos horarios como base aunque no estén en la agenda
- Identificas el día actual usando {dia_semana}
- Solo mencionas las clases correspondientes a ese día
- No mencionas clases de otros días
- Si no hay clases ese día, lo dices claramente
- Si hay eventos en la agenda, tienen prioridad
- Si es lunes, consideras día libre
- Si hay clases temprano (6:00 AM), lo mencionas y sugieres prepararse
- Ajustas recomendaciones de transporte según carga del día

CONTEXTO QUE RECIBES EN CADA INTERACCIÓN:
- Hora actual: {hora}
- Clima en Bucaramanga: {clima}
- Temperatura: {temperatura}
- Agenda del día: {agenda}
- Día de la semana: {dia_semana}
- Vehículo usado ayer: {vehiculo_ayer}

REGLAS ADICIONALES:
- Si Juan David dijo “no madrugo mañana”, no asumes rutina de 4:00 AM
- Si no hay eventos en agenda, te basas en horarios fijos
- Puedes sugerir mejoras en su día sin que te lo pidan
- Siempre buscas hacerle la vida más fácil

OBJETIVO:
Ser un asistente inteligente, natural y proactivo tipo Jarvis, que ayude a Juan David a organizar su día, optimizar su tiempo, ahorrar dinero y tomar mejores decisiones de forma automática.

"""
engine =pyttsx3.init()
def record_voice():
    audio = sd.rec(duration_record * frecuen_calidad, samplerate=frecuen_calidad, channels=1, dtype='float32')
    sd.wait()
    return audio

def voice_text(audio):
    modelo = whisper.load_model("base")
    sf.write("temp.wav", audio, frecuen_calidad)
    resultado = modelo.transcribe("temp.wav")
    return resultado["text"]

def text2voice(text):
    engine.say(text)
    engine.runAndWait()

def contexto_dia():
     ahora = datetime.datetime.now()
     hora = ahora.strftime("%I:%M %p")
     dia = ahora.strftime("%A")
     return hora,dia

def clima_bga():
    url = "https://api.open-meteo.com/v1/forecast?latitude=7.1254&longitude=-73.1198&current_weather=true"
    respuesta = requests.get(url)
    datos = respuesta.json()["current_weather"]
    temperatura = datos["temperature"]
    codigo_clima = datos["weathercode"]
    condiciones = {
    0: "despejado",
    1: "mayormente despejado", 
    2: "parcialmente nublado",
    3: "nublado",
    45: "neblina",
    61: "lluvia leve",
    63: "lluvia moderada",
    65: "lluvia fuerte",
    80: "chubascos leves",
    95: "tormenta"
}
    clima = condiciones.get(codigo_clima, "clima desconocido")
    return clima, temperatura

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
def personal_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    ahora = datetime.datetime.utcnow().isoformat() + "Z"
    eventos = service.events().list(
        calendarId="primary",
        timeMin=ahora,
        maxResults=5,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    items = eventos.get("items", [])
    if not items:
        return "Sin compromisos hoy"
    agenda = []
    for evento in items:
        titulo = evento["summary"]
        hora_evento = evento["start"].get("dateTime", evento["start"].get("date"))
        agenda.append(f"{titulo} a las {hora_evento}")
    return ", ".join(agenda)

def noticias_axel():
    url = "https://www.vanguardia.com/rss.xml"
    feedparser = feedparser.parse(url)
    noticias = []
    for entry in feed.entries[:3]:
        noticias.append(entry.title)
    return ",".join(noticias)

def mensaje_Axel(mensaje, hora, dia, clima, temperatura, agenda):
    prompt_actual = Prompt_Axel.replace(("{hora}", hora).replace("{dia_semana}", dia).replace("{clima}", clima).replace("{temperatura}", str(temperatura)).replace("{agenda}, agenda").replace("{noticias}, noticias").replace("{vehiculo_ayer}", memoria["vehiculo_ayer"]))
    respuesta_Client = Client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system = prompt_actual,
        messages=[{"role": "user", "content": mensaje}]
    )
    return respuesta_Client.content[0].text
while True:
    memoria = leer_hoy()
    hora,dia = contexto_dia()
    clima, temperatura = clima_bga()
    noticias = noticias_axel()
    agenda = personal_calendar() 
    print("dime que necesitas")
    user_voice = record_voice()
    mensaje_user = voice_text(user_voice)
    if "no madrugo mañana" in mensaje_user.lower():
        memoria["alarma_mañana"] = "desactivada"
        escribe_hoy(memoria)
    if "fui en carro" in mensaje_user.lower():
        memoria["vehiculo_ayer"] = "carro"
        escribe_hoy(memoria)
    if "fui en moto" in mensaje_user.lower():
        memoria["vehiculo_ayer"] = "moto"
        escribe_hoy(memoria)

    if mensaje_user == "no es mas":
        print("listo,avisame si necesitas otra cosa")
        break
    else:
        Respuesta_Axel = mensaje_Axel(mensaje_user, hora, dia, clima, temperatura, agenda, noticias, memoria)
        print(Respuesta_Axel)
        text2voice(Respuesta_Axel)

