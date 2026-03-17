#include "SerialComm.h"

#include <Arduino.h>

size_t SerialComm::send(const uint8_t *data, size_t len) {
    return Serial.write(data, len);
}

size_t SerialComm::receive(uint8_t *buffer, size_t len) {
    return Serial.read(buffer, len);
}

size_t SerialComm::available() {
    return Serial.available();
}

