import os
from infer import VASR
import soundfile as sf
import librosa
import torch
from openai import OpenAI
import streamlit as st
from audiorecorder import audiorecorder
from pydub import AudioSegment
import pandas as pd
import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
from pydub import AudioSegment
import speech_recognition as sr
from transformers import pipeline
device = torch.device('cuda')
def convert_audio(save_path, output_file='D:\Audio\output.wav'):
    try:
        # Đọc file âm thanh gốc
        y, sr = sf.read(save_path)

        # Lưu file âm thanh mới dưới định dạng WAV
        sf.write(output_file, y, sr)

        print(f"File âm thanh đã được chuyển đổi thành: {output_file}")
    except:
        st.write(save_path)
        sound = AudioSegment.from_file(save_path, format="mp3")
        sound.export(output_file, format="wav")
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device=0)
keyword = "Vi"
audio = st.file_uploader("Upload an audio file")
if audio is not None:
    st.audio(audio.read())
    save_folder = 'D:\Audio'
    save_path = Path(save_folder, audio.name)
    with open(save_path, mode='wb') as w:
        w.write(audio.getvalue())
    convert_audio(save_path=save_path)
    wave, ss = librosa.load('D:\Audio\output.wav', sr=16000)
    output = transcriber(wave)['text']
    st.write(output)