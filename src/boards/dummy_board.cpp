#include "dummy_board.h"
#include <HardwareSerial.h>

bool DummyBoard::setup() {
    // show warning
    Serial.println("No board configured, using dummy board!");
    return true;
}

void DummyBoard::loop() {
    // do nothing
}

bool DummyBoard::ready() {
    // never ready
    return false;
}
