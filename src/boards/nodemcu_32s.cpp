#include "nodemcu_32s.h"

#define RANDOM_ANALOGUE    25
#define PACKAGE_SIZE       65536
#define LED                2

NodeMCU32s::NodeMCU32s() : machineInterface(&hid_device),
                           machine(&machineInterface, nullptr),
                           comm(&serial_comm, &machine) {
    machineHandle = &machine;
    commHandle = &comm;
}

void NodeMCU32s::setup() {
    BLEDevice::init("Hand");
    if (!hid_device.begin()) {
        Serial.println("HID device unable to start");
        return;
    }
    machineInterface.bind(&machine);
    if (package == nullptr) {
        package = new uint8_t[PACKAGE_SIZE];
        memset(package, 0, PACKAGE_SIZE);
        machineInterface.setPackageArea(package, PACKAGE_SIZE);
        machine.setPackage(package);
    }
    pinMode(RANDOM_ANALOGUE, INPUT);
    randomSeed(analogRead(RANDOM_ANALOGUE));
    pinMode(LED, OUTPUT);

    if (!comm.init()) {
        Serial.println("Failed to start IVH comm");
    }
}

void NodeMCU32s::loop() {
    IVHState state = machine.getState();
    if (state == IVH_ST_STOPPED || state == IVH_ST_PAUSED || !ready()) {
        digitalWrite(LED, LOW);
    }else {
        digitalWrite(LED, HIGH);
    }
}

bool NodeMCU32s::ready() {
    return hid_device.connected();
}
