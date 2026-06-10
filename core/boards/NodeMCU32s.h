#pragma once

#include "ESP32BaseBoard.h"
#include "common/SerialComm.h"
#include "esp32/BLE_HID.h"


class NodeMCU32s : public ESP32BaseBoard {
public:
    NodeMCU32s();

private:
    BLEHID hidDevice{};
    SerialComm serialComm{};
};
