# Hướng dẫn cài đặt và chạy hệ thống giám sát trang trại thông minh

Dự án này là một hệ thống giám sát trang trại thông minh, sử dụng cảm biến (qua Arduino Uno) để thu thập dữ liệu nhiệt độ và độ ẩm. Dữ liệu được gửi đến một backend FastAPI, lưu trữ trong cơ sở dữ liệu MySQL, và sau đó được chatbot Rasa sử dụng để cung cấp lời khuyên và cảnh báo tự động thông qua email khi nhiệt độ vượt ngưỡng.

## 1. Yêu cầu hệ thống

Trước khi bắt đầu, hãy đảm bảo bạn có các công cụ sau được cài đặt trên máy tính:

*   **Arduino IDE**: Để lập trình và tải mã lên Arduino Uno.
*   **Python 3.10+**: Môi trường phát triển chính.
*   **MySQL Server**: Cơ sở dữ liệu để lưu trữ dữ liệu cảm biến.
*   **Git** (tùy chọn nhưng khuyến khích): Để quản lý mã nguồn.

## 2. Cài đặt và cấu hình

### 2.1. Thiết lập cơ sở dữ liệu MySQL

1.  Đảm bảo MySQL Server của bạn đang chạy.
2.  Mở MySQL client (ví dụ: MySQL Workbench, terminal MySQL) và tạo một cơ sở dữ liệu mới. Tên cơ sở dữ liệu mặc định trong dự án là `farm_chatbot_db`.

    ```sql
    CREATE DATABASE farm_chatbot_db;
    ```

3.  Đảm bảo tài khoản người dùng MySQL (mặc định là `root` với mật khẩu `123456`) có quyền truy cập vào cơ sở dữ liệu này. Nếu không, hãy tạo hoặc cấu hình lại người dùng cho phù hợp với `DATABASE_URL` trong `main.py`.

### 2.2. Thiết lập môi trường Python

1.  **Tạo môi trường ảo (Virtual Environment)**:
    Mở terminal trong thư mục gốc của dự án (`/D:/iot/nhat_anh`) và chạy lệnh sau:
    ```bash
    python -m venv venv
    ```

2.  **Kích hoạt môi trường ảo**:
    *   **Trên Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **Trên macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

3.  **Cài đặt các thư viện cần thiết**:
    Sau khi kích hoạt môi trường ảo, cài đặt tất cả các thư viện từ `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### 2.3. Lập trình Arduino Uno

1.  **Mở Arduino IDE**: Mở file sketch Arduino đã được cung cấp (hoặc sử dụng mã mẫu trước đó).
2.  **Cài đặt thư viện DHT Sensor**: Trong Arduino IDE, đi tới `Sketch > Include Library > Manage Libraries...` và tìm kiếm, cài đặt `DHT sensor library by Adafruit` và `Adafruit Unified Sensor`.
3.  **Kết nối cảm biến DHT11/DHT22**: Nối chân DATA của cảm biến vào chân số 2 của Arduino Uno (hoặc chân bạn đã định nghĩa trong mã Arduino).
4.  **Xác định cổng COM**: Cắm Arduino Uno vào máy tính. Trong Arduino IDE, đi tới `Tools > Port` để xác định cổng COM mà Arduino của bạn đang kết nối (ví dụ: `COM3`).
5.  **Cập nhật `read_arduino_and_send.py`**: Mở file `read_arduino_and_send.py` và thay thế `'COMx'` bằng cổng COM thực tế của Arduino Uno của bạn (ví dụ: `SERIAL_PORT = 'COM3'`).
6.  **Tải mã lên Arduino**: Tải mã Arduino lên bo mạch Arduino Uno của bạn.

### 2.4. Cấu hình Email cho cảnh báo

1.  Mở file `actions/actions.py`.
2.  Tìm phần cấu hình Email và thay thế các giá trị `your_email@gmail.com`, `your_app_password`, `recipient_email@example.com` bằng thông tin email của bạn.
    ```python
    EMAIL_SENDER = "your_email@gmail.com"
    EMAIL_APP_PASSWORD = "your_app_password" # Đối với Gmail, đây là Mật khẩu ứng dụng
    EMAIL_RECEIVER = "recipient_email@example.com"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    ```
    *   **Quan trọng**: Nếu bạn dùng Gmail, bạn cần tạo **Mật khẩu ứng dụng** (App Password) thay vì mật khẩu tài khoản chính. Hướng dẫn: [https://support.google.com/accounts/answer/185833](https://support.google.com/accounts/answer/185833)

### 2.5. Huấn luyện lại mô hình Rasa

Sau khi đã thay đổi các file `domain.yml`, `data/rules.yml`, và `actions/actions.py`, bạn cần huấn luyện lại mô hình Rasa để các thay đổi có hiệu lực.

Trong terminal (đã kích hoạt môi trường ảo), chạy lệnh:
```bash
rasa train
```

## 3. Chạy ứng dụng

Bạn cần chạy 3 thành phần chính của hệ thống trong 3 cửa sổ terminal riêng biệt (đã kích hoạt môi trường ảo).

### 3.1. Khởi chạy Backend FastAPI

Trong terminal 1:
```bash
uvicorn main:app --reload
```
Điều này sẽ khởi động API backend của bạn, lắng nghe trên `http://localhost:8000`. Khi nhiệt độ cảm biến vượt quá 34°C, FastAPI sẽ gửi tín hiệu cảnh báo đến Rasa.

### 3.2. Khởi chạy Rasa Actions Server

Trong terminal 2:
```bash
rasa run actions
```
Điều này sẽ khởi động server cho các hành động tùy chỉnh của Rasa, bao gồm hành động lấy dữ liệu cảm biến và hành động xử lý cảnh báo nhiệt độ cao.

### 3.3. Khởi chạy Script đọc dữ liệu Arduino

Trong terminal 3:
```bash
python read_arduino_and_send.py
```
Script này sẽ đọc dữ liệu từ Arduino Uno thông qua cổng Serial và gửi nó đến backend FastAPI.

## 4. Tương tác với Chatbot

Sau khi tất cả các thành phần trên đã chạy, bạn có thể tương tác với chatbot Rasa.

### 4.1. Chạy chatbot Rasa

Trong một terminal riêng biệt (terminal 4):
```bash
rasa shell
```

### 4.2. Cách tương tác

*   **Hỏi về dữ liệu cảm biến**: Bạn có thể hỏi chatbot về nhiệt độ hoặc độ ẩm. Chatbot sẽ mặc định lấy dữ liệu từ `arduino_sensor_uno`.
    *   `nhiệt độ hiện tại thế nào?`
    *   `độ ẩm bây giờ là bao nhiêu?`
    *   `dữ liệu cảm biến thế nào?`

*   **Yêu cầu tư vấn**: Bạn có thể yêu cầu chatbot tư vấn về trang trại. Chatbot sẽ lấy dữ liệu cảm biến mới nhất để đưa ra lời khuyên phù hợp.
    *   `tư vấn về trang trại`
    *   `cho tôi lời khuyên về cách quản lý`

*   **Cảnh báo tự động**: Khi nhiệt độ từ cảm biến gửi đến FastAPI vượt quá 34°C, hệ thống sẽ tự động kích hoạt hành động tư vấn và gửi email thông báo đến địa chỉ email bạn đã cấu hình. 

# Cấu hình thêm api của Google Gemini vào file main.py
