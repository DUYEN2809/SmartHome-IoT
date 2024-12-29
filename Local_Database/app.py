from functools import wraps
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from flask import send_file
import requests
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24) # Secret key cho session

# Database names
DB_NAME = "devices.db"
USERS_DB_NAME = "users.db"

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
        state INTEGER NOT NULL,
        pin_notes TEXT  -- Thêm cột pin_notes ở đây
    )
    """)

    # Kiểm tra xem cột pin_notes đã tồn tại chưa (cho trường hợp bảng đã tồn tại nhưng chưa có cột pin_notes)
    cursor.execute("PRAGMA table_info(devices)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'pin_notes' not in columns:
        cursor.execute("ALTER TABLE devices ADD COLUMN pin_notes TEXT")

    # Thêm các thiết bị mẫu nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM devices")
    if cursor.fetchone()[0] == 0:
        devices = [
            ("livingroom", "light", 0, ""),  # Thêm giá trị rỗng cho pin_notes
            ("bedroom", "light", 0, ""),
            ("kitchen", "light", 0, ""),
            ("staircase", "light", 0, "")
        ]
        cursor.executemany("INSERT INTO devices (room, device, state, pin_notes) VALUES (?, ?, ?, ?)", devices)

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

def init_users_db():
    """
    Khởi tạo cơ sở dữ liệu người dùng nếu chưa tồn tại.
    """
    conn = sqlite3.connect(USERS_DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Thêm user mặc định nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'user'")
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('user')
        cursor.execute("INSERT INTO users (username, password) VALUES ('user', ?)", (hashed_password,))

    conn.commit()
    conn.close()

def get_user(username):
    """
    Lấy thông tin người dùng từ database.
    """
    conn = sqlite3.connect(USERS_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Xử lý đăng nhập.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)

        if user and check_password_hash(user[2], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Xử lý đăng xuất.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

def login_required(f):
    """
    Decorator cho các route yêu cầu đăng nhập.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# endregion

# region Device Management

@app.route('/add_device', methods=['GET', 'POST'])
@login_required
def add_device():
    """
    Thêm thiết bị.
    """
    if request.method == 'POST':
        room = request.form.get('room')
        device = request.form.get('device')
        state = request.form.get('state')
        pin_notes = request.form.get('pin_notes')
        expert_password = request.form.get('expert_password')

        if expert_password != 'IoT@2024':
            flash('Sai mật khẩu chuyên gia.', 'error')
            return render_template('add_device.html', rooms=get_rooms(), device_types=get_device_types())

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO devices (room, device, state, pin_notes) VALUES (?, ?, ?, ?)", (room, device, state, pin_notes))
        conn.commit()
        conn.close()

        flash('Thêm thiết bị thành công.', 'success')
        return redirect(url_for('index'))

    return render_template('add_device.html', rooms=get_rooms(), device_types=get_device_types())

# ... (các import và code khác giữ nguyên) ...

@app.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    """
    Sửa (và xóa) thiết bị.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Xử lý cập nhật
        room = request.form.get('room')
        device = request.form.get('device')
        state = request.form.get('state')
        pin_notes = request.form.get('pin_notes')
        expert_password = request.form.get('expert_password')

        if expert_password != 'IoT@2024':
            flash('Sai mật khẩu chuyên gia.', 'error')
        else:
            # Nếu form submit có trường 'delete' (tức là ấn nút Xóa)
            if 'delete' in request.form:
                cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
                conn.commit()
                flash('Xóa thiết bị thành công.', 'success')
                conn.close()
                return redirect(url_for('index'))
            else: # Ngược lại là ấn nút Cập nhật
                cursor.execute("UPDATE devices SET room = ?, device = ?, state = ?, pin_notes = ? WHERE id = ?", (room, device, state, pin_notes, device_id))
                conn.commit()
                flash('Cập nhật thiết bị thành công.', 'success')

        # Lấy lại thông tin thiết bị sau khi cập nhật hoặc nếu mật khẩu sai
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device_data = cursor.fetchone()
        conn.close()
        return render_template('edit_device.html', device=device_data, rooms=get_rooms(), device_types=get_device_types())

    cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
    device_data = cursor.fetchone()
    conn.close()

    if device_data:
        return render_template('edit_device.html', device=device_data, rooms=get_rooms(), device_types=get_device_types())
    else:
        flash('Không tìm thấy thiết bị.', 'error')
        return redirect(url_for('index'))

# ... (phần code còn lại giữ nguyên) ...

@app.route('/delete_device/<int:device_id>', methods=['POST'])
@login_required
def delete_device(device_id):
    """
    Xóa thiết bị.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
    conn.commit()
    conn.close()

    flash('Xóa thiết bị thành công.', 'success')
    return redirect(url_for('index'))

def get_rooms():
    """
    Lấy danh sách các phòng.
    """
    return ["livingroom", "bedroom", "kitchen", "staircase"]

def get_device_types():
    """
    Lấy danh sách các loại thiết bị.
    """
    return ["light"]
# endregion

# region User Management

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Thay đổi mật khẩu người dùng.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = get_user(session['username'])

        if not check_password_hash(user[2], current_password):
            flash('Mật khẩu hiện tại không đúng.', 'error')
        elif new_password != confirm_password:
            flash('Mật khẩu mới không khớp.', 'error')
        else:
            hashed_password = generate_password_hash(new_password)
            conn = sqlite3.connect(USERS_DB_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user[0]))
            conn.commit()
            conn.close()
            flash('Thay đổi mật khẩu thành công.', 'success')
            return redirect(url_for('index'))

    return render_template('change_password.html')

# endregion
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

@app.route('/')
@login_required
def index():
    """
    Hiển thị giao diện quản lý trạng thái đèn.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, room, device, state, pin_notes FROM devices")
    devices = [{"id": row[0], "room": row[1], "device": row[2], "state": row[3], "pin_notes": row[4]} for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', devices=devices)

@app.route('/toggle_light', methods=['POST'])
@login_required
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
@login_required
def get_devices():
    """
    API để lấy danh sách trạng thái các thiết bị.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT room, device, state, pin_notes FROM devices")
    devices = [{"room": row[0], "device": row[1], "state": row[2], "pin_notes": row[3]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(devices)

# ...

if __name__ == "__main__":
    init_db()
    init_users_db()
    app.run(host='0.0.0.0', port=5000, debug=True)