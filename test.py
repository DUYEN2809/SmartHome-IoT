import requests
import os

# Replace with the URL of your API endpoint (modify port if needed)
url = "http://127.0.0.1:8000//transcribe_api"

# Path to the audio file you want to upload
audio_file_path = "d://Audio//Recording.wav"
# Tạo một file để upload
with open(audio_file_path, "rb") as audio_file:
    files = {'file': audio_file}

    # Gửi yêu cầu POST
    response = requests.post(url, files=files)

    # Kiểm tra kết quả
    if response.status_code == 200:
        print(response.json())  # In kết quả trả về dưới dạng JSON
    else:
        print("Lỗi khi gọi API:", response.text)