import os
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
import soundfile as sf
import librosa
from pydub import AudioSegment
from pathlib import Path
from transformers import pipeline
from transcriber import TCB

app = FastAPI()
#make api to upload wav file and recive transcription
@app.post("/upload")
async def create_item(file: bytes):
    #save the file in a folder
    with open("./wavs/test.wav", "wb") as fh:
        fh.write(file)
    return {"message": "File Saved"}

@app.get("/transcribe")
async def get_item():
    #load the file and transcribe it
    y, sr = librosa.load("./wavs/test.wav", sr=16000)
    transcription = TCB(y, sr).tcb()
    return {"message": transcription}

@app.post("/transcribe_api")
async def transcribe_audio(file: UploadFile):
    # Save the uploaded file temporarily
    with open("temp_audio.wav", "wb") as f:
        f.write(await file.read())

    # Load and transcribe the saved file
    y, sr = librosa.load("temp_audio.wav", sr=16000)
    transcription = TCB(y, sr).tcb()

    # Remove the temporary file
    os.remove("temp_audio.wav")

    return {"message": transcription}