#include <M5StickC.h>


const uint8_t SCREEN_BREATH = 20;

void setup() {
  //  Setup Display
  M5.begin();
  M5.Axp.ScreenBreath((int)SCREEN_BREATH);
  M5.Axp.EnableCoulombcounter(); 

  M5.Lcd.setRotation(1);

  // Setup LED
  pinMode(M5_LED, OUTPUT);

  // Setup Serial
  Serial.begin(9600);
  Serial.println("Initilized");  
}

void loop() {
  static bool ledState = false;
  M5.update();

  M5.Lcd.setCursor(1, 1, 1);
  M5.Lcd.printf("AXP Temp: %.1fC \r\n", M5.Axp.GetTempInAXP192());
  M5.Lcd.printf("Bat:\r\n  V: %.3fv  I: %.3fma\r\n", M5.Axp.GetBatVoltage(), M5.Axp.GetBatCurrent());
  M5.Lcd.printf("Bat power %.3fmw", M5.Axp.GetBatPower());

  digitalWrite(M5_LED, ledState ? HIGH : LOW);
  ledState = !ledState;

  delay(1000);
}
