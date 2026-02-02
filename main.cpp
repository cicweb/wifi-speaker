#include <WiFi.h>

const char* ssid     = "YOURWIFISSID";
const char* password = "YOURWIFIPASSWORDHERE";

WiFiServer server(1234);
WiFiClient client;

// audio config
#define DAC_PIN 25
#define SAMPLE_RATE 22050
#define BUFFER_SIZE 4096

uint8_t audioBuffer[BUFFER_SIZE];
volatile uint16_t wIndex = 0;
volatile uint16_t rIndex = 0;

hw_timer_t* audioTimer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

// limiter for lm386
uint8_t processSample(uint8_t s) {
  int centered = s - 128;

  if (centered > 18) centered = 18;
  if (centered < -18) centered = -18;

  return centered + 128;
}

// isr config
void IRAM_ATTR onAudio() {
  static uint8_t last = 128;

  portENTER_CRITICAL_ISR(&timerMux);

  if (rIndex != wIndex) {
    last = processSample(audioBuffer[rIndex]);
    rIndex = (rIndex + 1) % BUFFER_SIZE;
  }

  dacWrite(DAC_PIN, last);

  portEXIT_CRITICAL_ISR(&timerMux);
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());

  server.begin();

  dacWrite(DAC_PIN, 128);

  audioTimer = timerBegin(0, 80, true); 
  timerAttachInterrupt(audioTimer, &onAudio, true);
  timerAlarmWrite(audioTimer, 1000000 / SAMPLE_RATE, true);
  timerAlarmEnable(audioTimer);
}

void loop() {
  if (!client || !client.connected()) {
    client = server.available();
    return;
  }

  while (client.available()) {
    uint8_t b = client.read();
    uint16_t next = (wIndex + 1) % BUFFER_SIZE;

    if (next != rIndex) {
      audioBuffer[wIndex] = b;
      wIndex = next;
    }
  }
}
