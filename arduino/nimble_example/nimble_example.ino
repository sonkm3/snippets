#include <M5StickC.h>

#include <NimBLEDevice.h>

NimBLEServer* pServer;
NimBLECharacteristic* pTempChar;


class ServerCallbacks : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo) override {
        Serial.printf("Client address: %s\n", connInfo.getAddress().toString().c_str());
        pServer->updateConnParams(connInfo.getConnHandle(), 24, 48, 0, 180);
    }

    void onDisconnect(NimBLEServer* pServer, NimBLEConnInfo& connInfo, int reason) override {
        Serial.printf("Client disconnected - start advertising\n");
        NimBLEDevice::startAdvertising();
    }

    void onMTUChange(uint16_t MTU, NimBLEConnInfo& connInfo) override {
        Serial.printf("MTU updated: %u for connection ID: %u\n", MTU, connInfo.getConnHandle());
    }
};

void setup() {
  // setup
  M5.begin();
  Serial.begin(9600);

  NimBLEDevice::init("Sensor");
  pServer = NimBLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  NimBLEService* pService = pServer->createService("1809");
  pTempChar = pService->createCharacteristic("2A1C", NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY);
  pTempChar->setValue("0.0");

  pService->start();
  NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->setName("Sensor");
  pAdvertising->addServiceUUID("1809");
  pAdvertising->enableScanResponse(true);
  pAdvertising->start();
}

void loop() {
  static float temp = M5.Axp.GetTempInAXP192();
  pTempChar->setValue(temp);
  pTempChar->notify();
  delay(1000);
}
