#include "esp32_board.h"
#include <Arduino.h>
#include <LittleFS.h>

#define PACKAGE_FILE "/package.ivh"


bool ESP32BaseBoard::setup() {
    if (!LittleFS.begin(true)) {
        Serial.println("Failed to mount LFS");
        hasFileSystem = false;
        // board can still work without a file system
        // flashing will however not be possible
        return true;
    }
    hasFileSystem = true;

    File f = LittleFS.open(PACKAGE_FILE, FILE_READ);
    if (f) {
        currentPackageSize = f.read(packageBuffer, packageBufferSize);
        f.close();
    }
    return true;
}

uint64_t ESP32BaseBoard::getRandom(uint64_t min, uint64_t max) {
    return random(static_cast<long>(min), static_cast<long>(max));
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
