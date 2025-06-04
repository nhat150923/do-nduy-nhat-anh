CHATBOT NÔNG NGHIỆP THÔNG MINH
Nông nghiệp thông minh (Smart Agriculture) ra đời như một giải pháp tất yếu, ứng dụng các công nghệ hiện đại như Internet of Things (IoT), trí tuệ nhân tạo (AI), cảm biến thông minh, điện toán đám mây, và đặc biệt là mô hình ngôn ngữ lớn (LLM) để tự động hóa và tối ưu hóa mọi hoạt động trong quy trình sản xuất nông nghiệp.
Trong xu thế đó, đề tài “Xây dựng chatbot hỗ trợ quản lý trang trại kết hợp API LLM và cảm biến IoT sử dụng Arduino Uno” được triển khai với mục tiêu xây dựng một hệ thống:
Có khả năng giao tiếp ngôn ngữ tự nhiên với người dùng (nông dân).
　　　　　Tự động thu thập và phân tích dữ liệu từ các cảm biến môi trường như độ ẩm đất, nhiệt độ không khí.
Điều khiển thiết bị tự động như hệ thống bơm nước hoặc cho ăn.
Và đặc biệt, đưa ra các tư vấn thông minh dựa trên dữ liệu thực tế tại trang trại.
Việc sử dụng Arduino Uno làm nền tảng phần cứng giúp mô hình đơn giản, chi phí thấp nhưng dễ mở rộng và tiếp cận với sinh viên, kỹ thuật viên, cũng như hộ nông dân nhỏ. Tích hợp cùng với mô hình ngôn ngữ lớn (LLM), chatbot có thể hiểu và phản hồi thông minh, tạo ra một công cụ hỗ trợ đắc lực trong sản xuất nông nghiệp hiện đại.
CHỨC NĂNG VÀ MÔ TẢ
| **STT** | **Chức năng**                              | **Mô tả chi tiết**                                                                                                                                                   |
| ------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1️⃣     | Đọc dữ liệu cảm biến từ Arduino Uno        | Arduino thu thập dữ liệu từ các cảm biến như DHT11 (nhiệt độ, độ ẩm) và cảm biến độ ẩm đất, sau đó gửi qua Serial.                                                   |
| 2️⃣     | Phân tích và gửi dữ liệu lên máy chủ       | Tệp `read_arduino_and_send.py` nhận dữ liệu từ Arduino qua Serial COM, phân tích chuỗi dữ liệu bằng regex, trích xuất nhiệt độ/độ ẩm và gửi đến API `/sensor_data/`. |
| 3️⃣     | Lưu trữ dữ liệu cảm biến vào cơ sở dữ liệu | FastAPI nhận dữ liệu từ client Python và lưu vào bảng `sensor_data` trong MySQL thông qua SQLAlchemy ORM.                                                            |
| 4️⃣     | Truy xuất dữ liệu cảm biến theo ID         | Người dùng có thể gọi API `/sensor_data/{sensor_id}` để xem toàn bộ dữ liệu cảm biến của một thiết bị cụ thể.                                                        |
| 5️⃣     | Phát hiện nhiệt độ cao và gửi cảnh báo     | Nếu nhiệt độ vượt quá 34°C, hệ thống sẽ tự động gọi webhook gửi sự kiện đến **Rasa chatbot** để sinh cảnh báo hoặc phản hồi.                                         |
| 6️⃣     | Gửi câu hỏi từ người dùng đến LLM          | API `/get_advice/` nhận câu hỏi từ người dùng và tự động thêm thông tin cảm biến mới nhất vào nội dung prompt.                                                       |
| 7️⃣     | Sinh tư vấn thông minh từ LLM              | Sử dụng mô hình **Gemini 2.0 (Google Generative AI)** để xử lý prompt, phân tích dữ liệu cảm biến và trả lời phù hợp bằng tiếng Việt.                                |
| 8️⃣     | Chatbot nhận lệnh điều khiển thiết bị      | Người dùng gửi lệnh như “tưới nước 5 phút”, chatbot xử lý ngôn ngữ, sinh hành động tương ứng để điều khiển máy bơm qua relay (phần này mở rộng sau nếu cần).         |
| 9️⃣     | Giao tiếp người dùng qua Rasa Chatbot      | Giao tiếp ngôn ngữ tự nhiên giữa người dùng và hệ thống qua giao diện chatbot Rasa, kết nối với API backend.                                                         |
| 🔟      | Kiểm tra hệ thống hoạt động                | API `/health` dùng để kiểm tra trạng thái hoạt động của hệ thống (health check).                                                                                     |


SƠ ĐỒ CÁC KHÂU
![image](https://github.com/user-attachments/assets/1d2b6d01-191d-48b6-8156-60040da2ce3b)

SƠ ĐỒ CHỨC NĂNG HỆ THỐNG
![image](https://github.com/user-attachments/assets/c35fca3c-eafd-4b82-85f7-dad740735b48)

CÔNG NGHỆ SỬ DỤNG
Thành phần	Công nghệ đề xuất
IoT sensing	ESP32 + Cảm biến độ ẩm/nhiệt độ (DHT11, Soil Moisture Sensor)
Điều khiển	Relay Module điều khiển máy bơm/thiết bị cho ăn
Giao tiếp IoT	Giao thức MQTT hoặc HTTP REST API
Xử lý ngôn ngữ	GPT API (OpenAI), hoặc open-source như LLaMA
Backend xử lý	Python Flask hoặc Node.js
Giao diện người dùng	Telegram Bot, Zalo, hoặc Web chat
QUY TRÌNH HOẠT ĐỘNG
1.Truy vấn thông tin
 Ví dụ: 
Người dùng gửi: “Độ ẩm đất ở khu A hiện tại là bao nhiêu?”
 Chatbot phân tích → xác định mục tiêu là “truy xuất cảm biến độ ẩm khu A”. 
Gửi truy vấn API: GET /sensors/moisture?zone=A. 
Nhận dữ liệu: ví dụ 25%. Phản hồi: “Độ ẩm khu A hiện tại là 25%, hơi khô, nên tưới thêm nước.” 
2. Điều khiển thiết bị 
Ví dụ: 
Người dùng gửi: “Tưới nước cho khu A trong 10 phút”
 LLM hiểu yêu cầu → sinh lệnh: POST /actuators/pump/start?zone=A&duration=10. 
Thiết bị nhận lệnh → kích hoạt máy bơm khu A.
 Phản hồi: “Đã kích hoạt bơm nước khu A trong 10 phút.”
HƯỚNG PHÁT TRIỂN MỞ RỘNG
 Nhận dạng hình ảnh từ camera: phát hiện sâu bệnh, vật thể lạ, động vật hoang dã.
  Phân tích lịch sử dữ liệu cảm biến: dự đoán điều kiện thời tiết, lên lịch tưới tiêu tự động.
  Học máy (ML): cá nhân hóa phản hồi dựa trên hành vi người dùng và thời điểm.
  Tích hợp bản đồ số, GPS: định vị các khu vực trong trang trại.

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
