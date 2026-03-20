#include <Arduino.h>

#include "esp32/BLE_HID.h"
#include "HID.h"
#include "IVH.h"
#include "IVHComm.h"
#include "arduino/SerialComm.h"

#define RANDOM_ANALOGUE 25
#define PACKAGE_SIZE 65536
#define HEARTBEAT_INTERVAL 1000

BLEHID hid_device;
SerialComm serial_comm;
IVH machineInterface(&hid_device);
IVHMachine machine(&machineInterface, nullptr);
IVHComm comm(&serial_comm, &machine);
uint8_t *package;

void setup() {
    Serial.begin(115200);
    BLEDevice::init("Hand");

    if (!hid_device.begin()) {
        Serial.println("HID device unable to start");
        return;
    }
    pinMode(RANDOM_ANALOGUE, INPUT);
    randomSeed(analogRead(RANDOM_ANALOGUE));
    package = new uint8_t[PACKAGE_SIZE];


    machineInterface.setPackageArea(package, PACKAGE_SIZE);
    machineInterface.bind(&machine);
    machine.setPackage(package);

    if (!comm.init()) {
        Serial.println("Failed to start IVH comm");
    }
}

void loop() {
    comm.tick();
    if (!hid_device.connected())
        return;
    IVHErr err = machine.execute();
    if (err == IVH_ERR_MACHINE_INVALID) {
        delay(10);
        return;
    }
    if (err != IVH_ERR_OK) {
        Serial.print("IVH Runtime Error: ");
        Serial.println(IVHErrToString(err));
    }
}