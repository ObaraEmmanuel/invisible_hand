#pragma once
#include "board.h"
#include "IVH.h"
#include "common/SerialComm.h"
#include "esp32/BLE_HID.h"


class NodeMCU32s : public Board {
public:
    NodeMCU32s();

    void setup() override;

    void loop() override;

    bool ready() override;

private:
    BLEHID hid_device{};
    SerialComm serial_comm{};
    IVH machineInterface;
    IVHMachine machine;
    IVHComm comm;
    uint8_t* package = nullptr;
};
