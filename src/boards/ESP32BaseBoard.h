#pragma once
#include "board.h"
#include "esp32/BLE_HID.h"


class ESP32BaseBoard : public Board {
public:
    using Board::Board;
    bool setup() override;
    void loop() override;
    bool ready() override;
    virtual void updateIndicators();
    uint64_t getRandom(uint64_t min, uint64_t max) override;
    uint64_t getMicros() override;
    bool flashPackage() override;
protected:
    uint8_t hidLEDState = 0;
    bool firstToggle = false;
    bool hasFileSystem = false;
    bool autoStart = false;
    bool initComm = true;
    int analogPin = 0;
};
