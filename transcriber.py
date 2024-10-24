import librosa
from audiorecorder import audiorecorder
import torch
from transformers import pipeline
def convert_audio(save_path):
    wave, ss = librosa.load(save_path, sr=16000)
    return wave, ss        
class TCB():
    device = torch.device('cuda')
    transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device=0)
    def Transciber(self,save_path=None, wave=None, **kwargs):
            if save_path is not None:
                wave , ss=convert_audio(save_path=save_path)
            output = self.transcriber(wave)['text']
            return output