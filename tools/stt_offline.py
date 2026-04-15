from transformers import pipeline
import torch
import os
import shutil
import subprocess
os.environ["PATH"]+=";C:\\ffmpeg\\bin"
print(shutil.which("ffmpeg"))
pipe=pipeline("automatic-speech-recognition",model="openai/whisper-small")

def safe_transcribe(audio_path):
    try:
        return pipe(audio_path)
    except Exception as e:
        print("Direct read failed -> converting...",e)
        temp_wav="temp_audio.wav"

        cmd=[
            "ffmpeg","-y",
            "i",audio_path,
            "-ar","16000",
            "-ac","1",
            "-f","wav",
            temp_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists(temp_wav):
            raise RuntimeError("FFmpeg conversion failed")
        return pipe(temp_wav)
result=safe_transcribe(r"C:\Users\Sri Balagi\Downloads\Recording.m4a")
print(result)