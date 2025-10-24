#include <Arduino.h>

#include "BLE_HID.h"
#include "HID.h"


HID* hid_device;

void setup() {
    BLEDevice::init("Hand");
    hid_device = new BLEHID();
}

void loop() {
    if (!hid_device->connected())
        return;
    hid_device->press(UP_ARROW, 0);
    delay(2000);
}