#include "ESP32BaseBoard.h"
#include <Arduino.h>
#include <LittleFS.h>
#include <esp_task_wdt.h>

#define PACKAGE_FILE "/package.ivh"

#ifndef LED_HIGH_LOGIC
#define LED_HIGH_LOGIC 1
#endif

#define WDT_TIMEOUT 5


bool ESP32BaseBoard::setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(analogPin, INPUT);
    randomSeed(analogRead(analogPin));

    if (initComm)
        comm.init();

    if (!hid->begin()) {
        Serial.println("Unable to start HID device");
        return false;
    }


    if (LittleFS.begin(true)) {
        hasFileSystem = true;
        if (File f = LittleFS.open(PACKAGE_FILE, FILE_READ)) {
            currentPackageSize = f.read(packageBuffer, packageBufferSize);
            f.close();
        }

        if (autoStart && currentPackageSize > 0)
            machine.start();
    }else {
        // board can still work without a file system
        // flashing will however not be possible
        Serial.println("Failed to mount LFS");
        hasFileSystem = false;
    }

    // enable watchdog timer
    esp_task_wdt_init(WDT_TIMEOUT, true);
    esp_task_wdt_add(nullptr);

    return true;
}

void ESP32BaseBoard::loop() {
    const IVHState state = machine.getState();
    if ((hidLEDState ^ hid->LEDs) & CAPS_LOCK) {
        // Caps Lock has been toggled
        if (state == IVH_ST_PAUSED)
            machine.resume();
        else if (state == IVH_ST_STOPPED)
            machine.start();
        else
            machine.pause();

        // force ping to reflect state change ASAP
        comm.forcePing();
    }
    hidLEDState = hid->LEDs;
    updateIndicators();
    // reset watchdog timer
    esp_task_wdt_reset();
}

bool ESP32BaseBoard::ready() {
    return hid->connected();
}

void ESP32BaseBoard::updateIndicators() {
    if (!machine.isRunning() || !ready()) {
        digitalWrite(LED_BUILTIN, !LED_HIGH_LOGIC);
    }else {
        digitalWrite(LED_BUILTIN, LED_HIGH_LOGIC);
    }
}

uint64_t ESP32BaseBoard::getRandom(uint64_t min, uint64_t max) {
    // IVH machine requires random values in the closed range [min, max]
    // arduino random returns values in open range [min, max) so add 1
    return random(static_cast<long>(min), static_cast<long>(max + 1));
}

uint64_t ESP32BaseBoard::getMicros() {
    return micros();
}

bool ESP32BaseBoard::flashPackage() {
    if (!hasFileSystem) {
        return false;
    }
    File f = LittleFS.open(PACKAGE_FILE, FILE_WRITE);
    if (!f)
        return false;
    auto written = f.write(packageBuffer, currentPackageSize);
    f.close();
    return written == currentPackageSize;
}
