import soundfile as sf
import librosa
import streamlit as st
from audiorecorder import audiorecorder
from pydub import AudioSegment
from pathlib import Path
from transformers import pipeline
from transcriber import TCB
Model=TCB()
audio = st.file_uploader("Upload an audio file")
if audio is not None:
    st.audio(audio.read())
    save_folder = 'D:\Audio'
    save_path = Path(save_folder, audio.name)
    with open(save_path, mode='wb') as w:
        w.write(audio.getvalue())
    output = Model.Transciber(save_path=save_path)
    st.write(output)