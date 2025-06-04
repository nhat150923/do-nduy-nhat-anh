#include "DHT.h"

#define DHTPIN 2     // Chân data của cảm biến DHT được kết nối
#define DHTTYPE DHT11   // Loại cảm biến DHT bạn đang sử dụng (DHT11 hoặc DHT22)

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600); // Khởi tạo giao tiếp Serial với tốc độ 9600 baud
  Serial.println(F("DHTxx test!"));

  dht.begin();
}

void loop() {
  // Chờ một vài giây giữa các lần đo
  delay(2000);

  // Đọc độ ẩm. Giá trị NaN nếu không đọc được
  float h = dht.readHumidity();
  // Đọc nhiệt độ theo độ C. Giá trị NaN nếu không đọc được
  float t = dht.readTemperature();
  // Đọc nhiệt độ theo độ F (tùy chọn)
  // float f = dht.readTemperature(true);

  // Kiểm tra xem có đọc được giá trị hợp lệ hay không
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Tính chỉ số nhiệt theo độ C và độ F (tùy chọn)
  // float hic = dht.computeHeatIndex(t, h);
  // float hif = dht.computeHeatIndex(f, h);

  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.println(F("°C "));
  // Serial.print(F("Heat index: "));
  // Serial.print(hic);
  // Serial.println(F("°C "));
}
