import soundfile as sf
import librosa
import streamlit as st
from audiorecorder import audiorecorder
from pydub import AudioSegment
from pathlib import Path
from transformers import pipeline
# Danh sách các cách gọi tên "Hạ Vi" và các sai sót nhận diện
keywords = [
    "Hạ Vi",
    "Hạ Vĩ",
    "Ha Vi",
    "Ha Vĩ",
    "Hà Vi",
    "Hà Vy",
    "Hạ Vê",
    "Hà Vĩ",
    "Hạ Vy",
    "Hà V",
    "Ha V",
    "Hạ Viên",
    "Hà Viên",
    "Hà Vân",
    "Hạ Vũ",
    "Hạ Quỳ"
]
def convert_audio(save_path, output_file='D:\Audio\output.wav'):
    try:
        y, sr = sf.read(save_path)
        sf.write(output_file, y, sr)
        print(f"File âm thanh đã được chuyển đổi thành: {output_file}")
    except Exception as e:
        st.write(save_path)
        sound = AudioSegment.from_file(save_path, format="mp3")
        sound.export(output_file, format="wav")


transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device=0)

audio = st.file_uploader("Upload an audio file")
if audio is not None:
    st.audio(audio.read())
    save_folder = 'D:\Audio'
    save_path = Path(save_folder, audio.name)
    
    with open(save_path, mode='wb') as w:
        w.write(audio.getvalue())
        
    convert_audio(save_path=save_path)
    
    # Kiểm tra từ khóa trước khi tiến hành transcript
    wave, ss = librosa.load('D:\Audio\output.wav', sr=16000)
    output = transcriber(wave)['text']
    st.write(output)