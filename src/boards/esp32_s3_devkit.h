#pragma once
#include "Adafruit_NeoPixel.h"
#include "esp32_board.h"
#include "common/SerialComm.h"
#include "esp32/BLE_HID.h"


class ESP32S3Devkit: public ESP32BaseBoard {
public:
    ESP32S3Devkit();

    bool setup() override;

    void updateIndicators() override;

private:
    BLEHID hidDevice{};
    SerialComm serialComm{};
    Adafruit_NeoPixel rgbLED;
    uint8_t LEDState = 0;
    bool firstToggle = false;
};
