# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests
import smtplib
from email.mime.text import MIMEText

# Replace with the actual URL of your FastAPI backend
FASTAPI_BACKEND_URL = "http://localhost:8000"

# Cấu hình Email (cần điền thông tin của bạn vào đây)
EMAIL_SENDER = "tengmail@gmail.com"
EMAIL_APP_PASSWORD = "matkhau"
EMAIL_RECEIVER = "tengmail@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Hoặc 465 cho SSL

class ActionGetSensorData(Action):

    def name(self) -> Text:
        return "action_get_sensor_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sensor_id = tracker.get_slot("sensor_id")

        if not sensor_id:
            sensor_id = "arduino_sensor_uno" # Mặc định sử dụng ID này

        try:
            # Call the FastAPI backend endpoint to get sensor data
            response = requests.get(f"{FASTAPI_BACKEND_URL}/sensor_data/{sensor_id}")
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            sensor_data_list = response.json()

            if sensor_data_list:
                # Format the sensor data to send back to the user
                # For simplicity, let's just send the latest reading
                latest_data = sensor_data_list[-1] # Get the last item (assuming latest based on GET endpoint)
                message = (
                    f"Dữ liệu mới nhất từ cảm biến {sensor_id}:\n"
                    f"Nhiệt độ: {latest_data.get('temperature', 'N/A')}°C\n"
                    f"Độ ẩm: {latest_data.get('humidity', 'N/A')}%\n"
                    f"Thời gian: {latest_data.get('timestamp', 'N/A')}"
                )
                dispatcher.utter_message(text=message)
            else:
                dispatcher.utter_message(text=f"Không tìm thấy dữ liệu cho cảm biến {sensor_id}.")

        except requests.exceptions.RequestException as e:
            print(f"Error calling FastAPI backend for sensor data: {e}")
            dispatcher.utter_message(text="Xin lỗi, tôi gặp sự cố khi lấy dữ liệu cảm biến.")
        except Exception as e:
            print(f"An unexpected error occurred in action_get_sensor_data: {e}")
            dispatcher.utter_message(text="Xin lỗi, đã xảy ra lỗi nội bộ.")

        return []

class ActionGetAdvice(Action):

    def name(self) -> Text:
        return "action_get_advice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's latest message text
        user_latest_message = tracker.latest_message.get('text')

        try:
            # Call the FastAPI backend endpoint to get advice
            response = requests.post(f"{FASTAPI_BACKEND_URL}/get_advice/", json={"query": user_latest_message})
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            advice_response = response.json()
            advice = advice_response.get("advice", "Không nhận được tư vấn.")

            dispatcher.utter_message(text=advice)

        except requests.exceptions.RequestException as e:
            print(f"Error calling FastAPI backend for advice: {e}")
            dispatcher.utter_message(text="Xin lỗi, tôi gặp sự cố khi lấy lời tư vấn.")
        except Exception as e:
            print(f"An unexpected error occurred in action_get_advice: {e}")
            dispatcher.utter_message(text="Xin lỗi, đã xảy ra lỗi nội bộ.")

        return []

class ActionHandleHighTemperatureAlert(Action):

    def name(self) -> Text:
        return "action_handle_high_temperature_alert"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        temperature = tracker.get_slot("temperature")
        humidity = tracker.get_slot("humidity")

        if temperature is None or humidity is None:
            print("Không tìm thấy nhiệt độ hoặc độ ẩm trong slot để tư vấn.")
            dispatcher.utter_message(text="Xin lỗi, tôi không thể tư vấn vì thiếu dữ liệu cảm biến.")
            return []

        # Tạo câu hỏi cho mô hình AI dựa trên dữ liệu nhiệt độ cao
        user_query_for_llm = (
            f"Nhiệt độ hiện tại là {temperature}°C và độ ẩm là {humidity}%. "
            f"Nhiệt độ đang cao hơn mức bình thường (trên 34°C). "
            f"Hãy đưa ra lời khuyên chi tiết về cách quản lý trang trại (ví dụ: cây trồng, vật nuôi, hệ thống tưới tiêu) trong điều kiện này bằng tiếng Việt. "
            f"Đặc biệt chú ý đến tác động của nhiệt độ cao và độ ẩm." 
        )

        advice = ""
        try:
            # Gọi endpoint FastAPI để lấy lời tư vấn
            response = requests.post(f"{FASTAPI_BACKEND_URL}/get_advice/", json={"query": user_query_for_llm})
            response.raise_for_status()
            advice_response = response.json()
            advice = advice_response.get("advice", "Không nhận được tư vấn từ AI.")

            dispatcher.utter_message(text=f"Cảnh báo nhiệt độ cao! {temperature}°C. \nLời tư vấn: {advice}")

            # Gửi email
            self._send_email_notification(temperature, humidity, advice)

        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi gọi FastAPI backend cho lời tư vấn: {e}")
            dispatcher.utter_message(text="Xin lỗi, tôi gặp sự cố khi lấy lời tư vấn.")
        except Exception as e:
            print(f"Lỗi không mong muốn trong action_handle_high_temperature_alert: {e}")
            dispatcher.utter_message(text="Xin lỗi, đã xảy ra lỗi nội bộ khi xử lý cảnh báo.")

        return []

    def _send_email_notification(self, temperature: float, humidity: float, advice: str):
        subject = f"CẢNH BÁO NGUY HIỂM: Nhiệt độ cao tại trang trại! ({temperature}°C)"
        body = f"""
Kính gửi Người quản lý,

Nhiệt độ tại trang trại hiện đang ở mức cao đáng báo động: {temperature}°C.
Độ ẩm: {humidity}%

Lời tư vấn từ hệ thống:
{advice}

Vui lòng kiểm tra và có biện pháp xử lý kịp thời.

Trân trọng,
Hệ thống giám sát trang trại tự động
"""

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() # Bắt đầu mã hóa TLS
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.send_message(msg)
            print(f"Đã gửi email cảnh báo đến {EMAIL_RECEIVER}")
        except Exception as e:
            print(f"Lỗi khi gửi email cảnh báo: {e}")
