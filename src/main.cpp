#include <Arduino.h>

#include "esp32/BLE_HID.h"
#include "HID.h"
#include "IVH.h"

#define RANDOM_ANALOGUE 18

const unsigned char blob[49] =
"\x49\x56\x48\x99\x01\x00\x22\x00\x00\x00\xe0\x32\x40\x42\x0f\xe1"
"\x02\x00\x22\x7f\xef\x32\x40\x42\x0f\x23\x7f\x32\x40\x42\x0f\xe1"
"\x02\x00\x22\x81\xef\x32\x40\x42\x0f\x23\x81\xef\x45\x22\x16\xc5";

BLEHID hid_device;
IVH ivh_machine;

void setup() {
    Serial.begin(115200);
    BLEDevice::init("Hand");

    if (!hid_device.begin()) {
        Serial.println("HID device unable to start");
        return;
    }
    ivh_machine.setDevice(&hid_device);
    pinMode(RANDOM_ANALOGUE, INPUT);
    randomSeed(analogRead(RANDOM_ANALOGUE));
    ivh_machine.setPackage(blob);
    IVHErr err = ivh_machine.start();
    if (err != IVH_ERR_OK) {
        Serial.print("Error starting IVH: ");
        Serial.println(IVHErrToString(err));
    }else {
        Serial.println("IVH started");
    }
}

void loop() {
    if (!hid_device.connected())
        return;
    IVHErr err = ivh_machine.execute();
    if (err == IVH_ERR_MACHINE_INVALID) {
        delay(500);
        return;
    }
    if (err != IVH_ERR_OK) {
        Serial.print("IVH Runtime Error: ");
        Serial.println(IVHErrToString(err));
    }
    delay(1);
}