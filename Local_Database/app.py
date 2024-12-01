import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask import send_file
import requests 
app = Flask(__name__)
import sqlite3

# Tạo hoặc kết nối tới cơ sở dữ liệu SQLite
DB_NAME = "devices.db"

def init_db():
    """
    Khởi tạo cơ sở dữ liệu nếu chưa tồn tại.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tạo bảng devices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT NOT NULL,
        device TEXT NOT NULL,
        state INTEGER NOT NULL
    )
    """)

    # Thêm các thiết bị mẫu nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM devices")
    if cursor.fetchone()[0] == 0:
        devices = [
            ("livingroom", "light", 0),
            ("bedroom", "light", 0),
            ("kitchen", "light", 0),
            ("staircase", "light", 0)
        ]
        cursor.executemany("INSERT INTO devices (room, device, state) VALUES (?, ?, ?)", devices)

    conn.commit()
    conn.close()

def update_device_state(room, device, state):
    """
    Cập nhật trạng thái của một thiết bị.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE devices
    SET state = ?
    WHERE room = ? AND device = ?
    """, (state, room, device))

    conn.commit()
    conn.close()

CORS(app)  # Cho phép xử lý CORS nếu cần
def get_ngrok_url():
    with open("link_api.txt", "r") as file:
        return file.read().strip()
def parse_gemini_response(response: str) -> str:
    """
    Phân tích phản hồi từ gemini và tạo câu trả lời thân thiện với người dùng.

    Args:
        response (str): Phản hồi từ API gemini (vd: "output.livingroom.light.0").

    Returns:
        str: Câu trả lời thân thiện.
    """
    # Ánh xạ các giá trị trong response
    room_map = {
        "livingroom": "phòng khách",
        "bedroom": "phòng ngủ",
        "kitchen": "bếp",
        "staircase": "cầu thang",
    }

    device_map = {
        "light": "đèn",
    }

    state_map = {
        "0": "tắt",
        "1": "bật",
    }

    # Phân tích chuỗi phản hồi
    try:
        _, room, device, state = response.split(".")
        room_name = room_map.get(room, "không rõ phòng")
        device_name = device_map.get(device, "thiết bị không xác định")
        state_action = state_map.get(state, "không rõ trạng thái")
        
        # Tạo câu trả lời
        return f"Được rồi! Tôi đã {state_action} {device_name} {room_name} cho bạn."
    except ValueError:
        # Phản hồi không đúng định dạng
        return "Xin lỗi, tôi không thể hiểu yêu cầu này."

def parse_gemini_response_and_update_db(response: str) -> str:
    """
    Phân tích phản hồi từ gemini, cập nhật trạng thái thiết bị trong cơ sở dữ liệu,
    và tạo câu trả lời thân thiện với người dùng.

    Args:
        response (str): Phản hồi từ API gemini (vd: "output.livingroom.light.0").

    Returns:
        str: Câu trả lời thân thiện.
    """
    # Ánh xạ các giá trị trong response
    room_map = {
        "livingroom": "phòng khách",
        "bedroom": "phòng ngủ",
        "kitchen": "bếp",
        "staircase": "cầu thang",
        "stairway": "cầu thang",
    }

    device_map = {
        "light": "đèn",
    }

    state_map = {
        "0": "tắt",
        "1": "bật",
    }

    # Phân tích chuỗi phản hồi
    try:
        _, room, device, state = response.split(".")
        room_name = room_map.get(room, "không rõ phòng")
        device_name = device_map.get(device, "thiết bị không xác định")
        state_action = state_map.get(state, "không rõ trạng thái")

        # Cập nhật trạng thái trong cơ sở dữ liệu
        update_device_state(room, device, int(state))

        # Tạo câu trả lời
        return f"Được rồi! Tôi đã {state_action} {device_name} {room_name} cho bạn."
    except ValueError:
        # Phản hồi không đúng định dạng
        return "Xin lỗi, tôi không thể hiểu yêu cầu này."


@app.route('/save_audio', methods=['POST'])
def save_audio():
    output_file_path = "output.wav"
        # Kiểm tra và xóa tệp nếu tồn tại
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # Lưu file âm thanh được ghi
    audio_data = request.data
    audio_file_path = "input.wav"
    with open(audio_file_path, "wb") as f:
        f.write(audio_data)

    # Đọc URL của server ngrok từ file link_api.txt
    ngrok_url = get_ngrok_url()

    # 1. Gửi file âm thanh tới API /transcribe_api
    transcribe_api_url = f"{ngrok_url}/transcribe_api"
    transcription = ""
    try:
        with open(audio_file_path, "rb") as audio_file:
            files = {'file': audio_file}
            response = requests.post(transcribe_api_url, files=files)
        if response.status_code == 200:
            transcription = response.json().get("message", "")
            print(f"Transcription: {transcription}")
        else:
            return f"Lỗi khi gọi API /transcribe_api: {response.text}", 500
    except Exception as e:
        return f"Lỗi khi gửi file tới /transcribe_api: {str(e)}", 500

    # 2. Gọi API /gemini để xử lý lệnh điều khiển
    gemini_api_url = f"{ngrok_url}/gemini"
    gemini_response = ""
    try:
        data = {"body": transcription}
        response = requests.post(gemini_api_url, json=data)
        if response.status_code == 200:
            gemini_response = response.json()
            print(f"Gemini response: {gemini_response}")
        else:
            return f"Lỗi khi gọi API /gemini: {response.text}", 500
    except Exception as e:
        return f"Lỗi khi gửi yêu cầu tới /gemini: {str(e)}", 500

    friendly_response = parse_gemini_response_and_update_db(gemini_response)

    # 3. Gọi API /tts để tạo tệp âm thanh output.wav từ phản hồi
    tts_api_url = f"{ngrok_url}/tts"
    try:
        data = {"body": friendly_response}
        response = requests.post(tts_api_url, json=data)
        if response.status_code == 200:
            output_file_path = "output.wav"
            with open(output_file_path, "wb") as f:
                f.write(response.content)
        else:
            return f"Lỗi khi gọi API /tts: {response.text}", 500
    except Exception as e:
        return f"Lỗi khi gửi yêu cầu tới /tts: {str(e)}", 500

    return jsonify({"message": friendly_response})

@app.route('/')
def index():
    """
    Hiển thị giao diện quản lý trạng thái đèn.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT room, device, state FROM devices")
    devices = [{"room": row[0], "device": row[1], "state": row[2]} for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', devices=devices)

@app.route('/toggle_light', methods=['POST'])
def toggle_light():
    """
    API để thay đổi trạng thái của một thiết bị.
    """
    data = request.get_json()
    room = data.get("room")
    device = data.get("device")
    state = data.get("state")

    if room and device is not None and state in [0, 1]:
        update_device_state(room, device, state)
        return jsonify({"message": f"Trạng thái của {device} tại {room} đã được cập nhật thành {'Bật' if state == 1 else 'Tắt'}."})
    else:
        return jsonify({"error": "Thông tin không hợp lệ"}), 400

@app.route('/get_devices', methods=['GET'])
def get_devices():
    """
    API để lấy danh sách trạng thái các thiết bị.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT room, device, state FROM devices")
    devices = [{"room": row[0], "device": row[1], "state": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(devices)


@app.route('/get_audio', methods=['GET'])
def get_audio():
    audio_path = "output.wav"
    try:
        response = send_file(audio_path, mimetype="audio/wav", as_attachment=False)
        response.headers["Accept-Ranges"] = "bytes"  # Hỗ trợ phát trực tuyến\
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except FileNotFoundError:
        return {"error": "Tệp âm thanh không tồn tại"}, 404
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
