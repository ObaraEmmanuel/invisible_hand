#include "dummy_board.h"
#include <HardwareSerial.h>

void DummyBoard::setup() {
    // show warning
    Serial.println("No board configured, using dummy board!");
}

void DummyBoard::loop() {
    // do nothing
}

bool DummyBoard::ready() {
    // never ready
    return false;
}
