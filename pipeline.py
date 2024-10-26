"""
Đây là một pipeline cho phép chúng ta có thể xử lý dữ liệu trong nhiều bước.

Pipeline này là một Class gọi là SmartHome_Pipeline. Nó sẽ có các phương thức sau:
- __init__(): để khởi tạo pipeline.
- Data_cleaning(): chuẩn hóa dữ liệu.
- SR_processing(): xử lý âm thanh thành văn bản
- Gemini_processing(): xử lý văn bản thành các signal đơn lẻ.
- Signal_processing(): xử lý signal đơn lẻ thành các signal được chuẩn hóa cho ADRUINO
- TTS_processing(): xử lý văn bản thành tiếng nói.

Đầu vào của Class này là một file audio. Đầu ra là một file audio và file JSON chứa dữ liệu thông tin.

"""