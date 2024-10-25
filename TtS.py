# Load model directly
import numpy as np
import scipy
import torch
from transformers import AutoTokenizer, AutoModelForTextToWaveform
# Use a pipeline as a high-level helper
from transformers import pipeline
import scipy.io.wavfile as wav
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
device = torch.device('cuda')
model = AutoModelForTextToWaveform.from_pretrained("facebook/mms-tts-vie")
# transfer model
model.to(device)

class TTS:
    def __init__(self, text):
        self.tokenizer = tokenizer
        self.model = model
        self.text = text

    def tts(self):
        # Tokenize input text
        encoded_inputs = self.tokenizer(self.text, return_tensors="pt").to(device)
        # Generate audio
        with torch.no_grad():
            output = self.model(**encoded_inputs).waveform
        output = output.cpu()
        data_np = output.numpy()
        data_np_squeezed = np.squeeze(data_np)
        wav.write("output.wav", rate=16000, data=data_np_squeezed)