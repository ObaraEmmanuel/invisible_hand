#pragma once

#include "esp32_board.h"
#include "common/SerialComm.h"
#include "esp32/BLE_HID.h"


class NodeMCU32s : public ESP32BaseBoard {
public:
    NodeMCU32s();

    bool setup() override;

    void loop() override;

    bool ready() override;

private:
    BLEHID hid_device{};
    SerialComm serial_comm{};
    uint8_t LEDState = 0;
    bool firstToggle = false;
};
