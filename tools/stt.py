from groq import Groq
from dotenv import load_dotenv
import os
from io import BytesIO

load_dotenv()

api=os.getenv("GROQ_API_KEY")
client = Groq(api_key=api)
MODEL="whisper-large-v3"

def read_audio(file_path):
    try:
        with open(file_path,"rb") as f:
            audio_bytes=f.read()
        return audio_bytes
    except FileNotFoundError:
        raise Exception("Audio file not found")


def send_to_whisper(audio_bytes):
    audio_file=BytesIO(audio_bytes)
    audio_file.name="audio.wav"
    response=client.audio.transcriptions.create(
        file=audio_file,
        model=MODEL
    )
    return response.text
def transcribe_audio(file_path):
    audio_bytes=read_audio(file_path)
    text=send_to_whisper(audio_bytes)
    return text

if __name__=="__main__":
    text=transcribe_audio(r"C:\Users\Sri Balagi\Downloads\Recording.m4a")
    print(text)