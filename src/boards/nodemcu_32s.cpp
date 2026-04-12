#include "nodemcu_32s.h"
#include <Arduino.h>

#define RANDOM_ANALOGUE    25
#define PACKAGE_SIZE       65536

NodeMCU32s::NodeMCU32s() : ESP32BaseBoard(&serial_comm, &hid_device) {
}

bool NodeMCU32s::setup() {
    if (!ESP32BaseBoard::setup())
        return false;

    // init serial comm
    comm.init();

    if (!hid_device.begin()) {
        Serial.println("HID device unable to start");
        return false;
    }
    pinMode(RANDOM_ANALOGUE, INPUT);
    randomSeed(analogRead(RANDOM_ANALOGUE));
    pinMode(LED_BUILTIN, OUTPUT);

    // There is a loaded package so begin execution
    if (currentPackageSize > 0)
        machine.start();
    return true;
}

void NodeMCU32s::loop() {
    const IVHState state = machine.getState();
    if ((LEDState ^ hid_device.LEDs) & CAPS_LOCK) {
        if (firstToggle) {
            // Caps Lock has been toggled
            if (state == IVH_ST_PAUSED)
                machine.resume();
            else if (state == IVH_ST_STOPPED)
                machine.start();
            else
                machine.pause();
        }
        firstToggle = true;
        // force ping to reflect state change ASAP
        comm.forcePing();

    }
    LEDState = hid_device.LEDs;
    if (state == IVH_ST_STOPPED || state == IVH_ST_INVALID || state == IVH_ST_PAUSED || !ready()) {
        digitalWrite(LED_BUILTIN, LOW);
    }else {
        digitalWrite(LED_BUILTIN, HIGH);
    }
}

bool NodeMCU32s::ready() {
    return hid_device.connected();
}
