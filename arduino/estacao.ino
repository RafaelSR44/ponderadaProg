/*
  estacao.ino
  -----------
  Sketch Arduino para a Estação Meteorológica IoT.
  Lê temperatura e umidade do sensor DHT11 e envia os dados
  em formato JSON pela porta serial a cada 5 segundos.

  Dependências (instalar pela Arduino IDE → Gerenciar Bibliotecas):
    - DHT sensor library (Adafruit)
    - ArduinoJson (Benoit Blanchon)

  Ligação DHT11:
    VCC  → 5V
    GND  → GND
    DATA → pino digital 2 (com resistor pull-up de 10kΩ para 5V)
*/

#include <DHT.h>
#include <ArduinoJson.h>

#define DHTPIN  2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(2000);  // aguarda estabilização do sensor
}

void loop() {
  float temperatura = dht.readTemperature();
  float umidade     = dht.readHumidity();

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("{\"erro\": \"falha na leitura do sensor\"}");
    delay(5000);
    return;
  }

  StaticJsonDocument<128> doc;
  doc["temperatura"] = temperatura;
  doc["umidade"]     = umidade;

  serializeJson(doc, Serial);
  Serial.println();  // \n marca fim da linha para PySerial

  delay(5000);
}
