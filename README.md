# IoT Project

Đây là một ứng dụng API được xây dựng bằng FastAPI. Dưới đây là các hướng dẫn để cài đặt và chạy dự án.

## Chạy ứng dụng

Ứng dụng của bạn được code trong file `SRAPI.py`. Để chạy ứng dụng FastAPI này bằng Uvicorn, sử dụng các lệnh dưới đây.

### Cách chạy cơ bản 

Chạy ứng dụng với tùy chọn `--reload` để tự động tải lại khi có thay đổi mã nguồn:

```bash
uvicorn SRAPI:app --host 0.0.0.0 --port 8000 --reload
