import numpy as np
import torch
from transformers import VitsTokenizer, VitsModel, set_seed
import scipy.io.wavfile as wav

tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-vie")
model = VitsModel.from_pretrained("facebook/mms-tts-vie")

inputs = tokenizer(text="Xin chào, đây là một bài phát biểu mẫu.", return_tensors="pt")

set_seed(555)  # make deterministic

with torch.no_grad():
   outputs = model(**inputs)

waveform = outputs.waveform[0]
output = waveform.cpu()
data_np = output.numpy()
data_np_squeezed = np.squeeze(data_np)
wav.write("output.wav", rate=model.config.sampling_rate, data=data_np_squeezed)
