# IoT Project

Đây là một ứng dụng API được xây dựng bằng FastAPI. Dưới đây là các hướng dẫn để cài đặt và chạy dự án.

## Chạy ứng dụng A.I Server

Ứng dụng của bạn được code trong file `SRAPI.py`. Để chạy ứng dụng FastAPI này bằng Uvicorn, sử dụng các lệnh dưới đây.

### Cách chạy cơ bản 

Chạy ứng dụng với tùy chọn `--reload` để tự động tải lại khi có thay đổi mã nguồn:

```bash
uvicorn SRAPI:app --host 0.0.0.0 --port 8000 --reload
```
### Lưu ý tạo Inbound Rules cho UFW (Firewall)
Nếu bạn sử dụng firewall, hãy thêm các quy tắc cho phép truy cập vào port `8000` như sau:
```bash
sudo ufw allow 8000/tcp
```
Đối với Window:
```bash
Mở port 8000 trên Windows Firewall
Mở Control Panel và đi đến System and Security > Windows Defender Firewall.
Chọn Advanced settings ở thanh bên trái.
Trong cửa sổ Windows Firewall, chọn Inbound Rules > New Rule.
Chọn Port và nhấn Next.
Chọn TCP và nhập 8000 vào mục Specific local ports.
Chọn Allow the connection và nhấn Next.
Chọn các mục Domain, Private, và Public theo yêu cầu, rồi nhấn Next.
Đặt tên cho rule, ví dụ: "Allow Port 8000", rồi nhấn Finish.
```

### Tạo Tunnels bằng Ngrok cho Deloy Api lên Internet
Nếu bạn muốn deploy API của mình lên internet, hãy sử dụng tunnels ngrok. Như vậy, bạn có thể truy cập ứng dụng của mình từ nơi khác.

```bash
ngrok http 8000
```

## Chạy ứng dụng Local Database

Để chạy local database, bạn cần truy cập /Local_Database ở repo này và sử dụng lệnh sau:
```bash
cd /Local_Database
python app.py
```
## TEMPLATE arduino với ESP8266

Đây là một template cho Arduino của ESP8266.
Đường dẫn template: SmartHome-IoT\Local_Database\arduino