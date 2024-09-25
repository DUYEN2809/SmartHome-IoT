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


def convert_audio(save_path, output_file='D:\Audio\output.wav'):
    try:
        # Đọc file âm thanh gốc
        y, sr = sf.read(save_path)

        # Lưu file âm thanh mới dưới định dạng WAV
        sf.write(output_file, y, sr)

        print(f"File âm thanh đã được chuyển đổi thành: {output_file}")
    except:
        st.write(save_path)
        sound = AudioSegment.from_file(save_path, format="m4a")
        sound.export(output_file, format="wav")

config = 'configs\\quartznet12x1_vi.yaml'
encoder_checkpoint = 'models\\acoustic_model\\vietnamese\\JasperEncoder-STEP-289936.pt'
decoder_checkpoint = 'models\\acoustic_model\\vietnamese\\JasperDecoderForCTC-STEP-289936.pt'
lm_path = 'models/language_model/5-gram-lm.binary'
vasr = VASR(
    config_file=config,
    encoder_checkpoint=encoder_checkpoint,
    decoder_checkpoint=decoder_checkpoint,
    lm_path=lm_path,
    beam_width=100
)
#audio = audiorecorder("Click to record", "Click to stop recording")
audio = st.file_uploader("Upload an audio file")
if audio is not None:
    st.audio(audio.read())
    save_folder = 'D:\Audio'
    save_path = Path(save_folder, audio.name)
    with open(save_path, mode='wb') as w:
        w.write(audio.getvalue())
    convert_audio(save_path=save_path)
    wave, sr = librosa.load('D:\Audio\output.wav', sr=16000)
    transcript = vasr.transcribe(wave)
    st.write(transcript)
