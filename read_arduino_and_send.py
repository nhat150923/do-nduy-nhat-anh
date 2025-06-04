import serial
import time
import re
from send_sensor_data import send_data

# Cấu hình cổng Serial và tốc độ baud
# Thay đổi 'COMx' thành cổng COM mà Arduino Uno của bạn đang kết nối
# Bạn có thể tìm thấy cổng này trong Arduino IDE dưới Tools > Port
SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

def read_and_send_sensor_data():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Đã kết nối với Arduino Uno tại {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"Lỗi khi kết nối với cổng Serial: {e}")
        print("Vui lòng kiểm tra lại cổng COM và đảm bảo Arduino đã được cắm vào.")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Dữ liệu nhận được từ Arduino: {line}")

                # Sử dụng regex để trích xuất nhiệt độ và độ ẩm
                match = re.search(r"Humidity: (\d+\.?\d*)%?\s*Temperature: (\d+\.?\d*)", line)
                if match:
                    humidity_str = match.group(1)
                    temperature_str = match.group(2)
                    
                    try:
                        humidity = float(humidity_str)
                        temperature = float(temperature_str)
                        print(f"Đã phân tích: Nhiệt độ = {temperature}°C, Độ ẩm = {humidity}%")
                        
                        # Gửi dữ liệu đến backend FastAPI
                        send_data(temperature, humidity, "arduino_sensor_uno")
                    except ValueError:
                        print("Không thể chuyển đổi giá trị nhiệt độ hoặc độ ẩm sang số.")
                else:
                    print("Không tìm thấy dữ liệu nhiệt độ và độ ẩm trong dòng.")
            time.sleep(1) # Đợi 1 giây trước khi đọc lại
    except KeyboardInterrupt:
        print("Đã dừng chương trình.")
    finally:
        ser.close()
        print("Cổng Serial đã đóng.")

if __name__ == "__main__":
    read_and_send_sensor_data() 