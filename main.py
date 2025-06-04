# main.py

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import google.generativeai as genai
import requests

# Database connection URL
# Replace with your actual MySQL connection details
DATABASE_URL = "mysql+mysqlconnector://root:123456@localhost:3306/farm_chatbot_db" 

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base class
Base = declarative_base()

# Define Database Model for Sensor Data
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(length=255), index=True) # Consider using DateTime type in a real app
    temperature = Column(Integer) # Or Float
    humidity = Column(Integer) # Or Float
    sensor_id = Column(String(length=255), index=True, nullable=True)

# Pydantic model for incoming sensor data
class SensorDataCreate(BaseModel):
    timestamp: str # Should match the type in your SQLAlchemy model
    temperature: int # Or float
    humidity: int # Or float
    sensor_id: str | None = None # Use Optional[str] if not using Python 3.10+

# Pydantic model for returning sensor data
class SensorDataResponse(BaseModel):
    id: int
    timestamp: str
    temperature: int
    humidity: int
    sensor_id: str | None

    class Config:
        orm_mode = True # Enable ORM mode

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example endpoint using DB (uncomment and complete later)
# @app.get("/items/{item_id}")
# def read_item(item_id: int, db: Session = Depends(get_db)):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     return item 

# Endpoint to receive sensor data
@app.post("/sensor_data/")
def create_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    db_sensor_data = SensorData(
        timestamp=data.timestamp,
        temperature=data.temperature,
        humidity=data.humidity,
        sensor_id=data.sensor_id
    )
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)

    # Logic để kích hoạt cảnh báo nhiệt độ cao và email
    if data.temperature > 34:
        print(f"Nhiệt độ ({data.temperature}°C) vượt ngưỡng 34°C. Gửi sự kiện tới Rasa.")
        # Đây là URL mặc định của Rasa REST webhook
        rasa_webhook_url = "http://localhost:5005/webhooks/rest/webhook"
        try:
            # Gửi một tin nhắn đặc biệt đến Rasa để kích hoạt hành động tùy chỉnh
            # Sử dụng một user ID cố định cho cảnh báo tự động
            rasa_payload = {
                "sender": "automated_sensor_alert",
                "message": f"/trigger_high_temp_alert{{\"temperature\": {data.temperature}, \"humidity\": {data.humidity}}}"
            }
            rasa_response = requests.post(rasa_webhook_url, json=rasa_payload)
            rasa_response.raise_for_status()
            print("Đã gửi tín hiệu cảnh báo nhiệt độ cao đến Rasa thành công.")
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi gửi tín hiệu cảnh báo đến Rasa: {e}")

    return db_sensor_data 

# Endpoint to get sensor data by sensor_id
@app.get("/sensor_data/{sensor_id}", response_model=list[SensorDataResponse])
def read_sensor_data(sensor_id: str, db: Session = Depends(get_db)):
    sensor_data = db.query(SensorData).filter(SensorData.sensor_id == sensor_id).all()
    return sensor_data 

# --- Google AI Configuration ---
# Replace with your actual Google AI API Key
# Consider using environment variables for better security
GOOGLE_API_KEY = "api Gemini Key"
genai.configure(api_key=GOOGLE_API_KEY)
# --- End Google AI Configuration ---

# Pydantic model for user query to LLM
class UserQuery(BaseModel):
    query: str

# Endpoint to get advice from LLM based on sensor data
@app.post("/get_advice/")
def get_advice(user_query: UserQuery, db: Session = Depends(get_db)):
    # Fetch the latest sensor data
    latest_sensor_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()

    # Construct the prompt for the LLM
    prompt = user_query.query
    if latest_sensor_data:
        sensor_info = (
            f"\n\nDữ liệu cảm biến hiện tại:\n"
            f"Nhiệt độ: {latest_sensor_data.temperature}°C\n"
            f"Độ ẩm: {latest_sensor_data.humidity}%\n"
            f"Thời gian: {latest_sensor_data.timestamp}"
        )
        if latest_sensor_data.sensor_id:
            sensor_info += f"\nID Cảm biến: {latest_sensor_data.sensor_id}"

        prompt += sensor_info
        prompt += "\n\nDựa trên thông tin này và câu hỏi của người dùng, hãy đưa ra lời tư vấn phù hợp cho việc quản lý trang trại bằng tiếng Việt."

    try:
        # Call the Google AI API
        model = genai.GenerativeModel('gemini-2.0-flash') # Changed model name
        response = model.generate_content(prompt)
        advice = response.text
    except Exception as e:
        # Handle potential errors from the API call
        print(f"Error calling LLM API: {e}")
        advice = "Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này."

    return {"advice": advice} 