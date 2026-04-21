import whisper
import soundfile as sf
import sounddevice as sd
duration_record = 5
frecuen_calidad = 16000
def record_voice():
    audio = sd.rec(duration_record * frecuen_calidad, samplerate=frecuen_calidad, channels=1, dtype='float32')
    sd.wait()
    return audio
def voice_text(audio):
    modelo = whisper.load_model("base")
    sf.write("temp.wav", audio, frecuen_calidad)
    resultado = modelo.transcribe("temp.wav")
    return resultado["text"]
print("dime que necesitas")
user_voice = record_voice()
user_text = voice_text(user_voice)
print(user_text)