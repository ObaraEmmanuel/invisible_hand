#include "board.h"

#include <cstring>
#include <HardwareSerial.h>

Board::Board(IVHCommInterface* comm, HID* hid): commInterface(comm), hid(hid) {
    packageBuffer = new uint8_t[packageBufferSize]{};
    machine.setPackage(packageBuffer);
    machine.setStackBuffer(stack, STACK_SIZE);
}

uint8_t Board::getInputType() const {
    return hid->type;
}

void Board::pause() {
    hid->pause();
}

void Board::resume() {
    hid->resume();
}

void Board::reset() {
    hid->reset();
}

void Board::keyHold(uint8_t *key, uint8_t len, uint8_t modifier) {
    hid->keyHold(key, len, modifier);
}

void Board::keyRelease(uint8_t *key, uint8_t len, uint8_t modifier) {
    if (len == 0 && modifier == 0) {
        hid->keyReleaseAll();
        return;
    }
    hid->keyRelease(key, len, modifier);
}

void Board::buttonHold(uint8_t button) {
    hid->buttonHold(button);
}

void Board::buttonRelease(uint8_t button) {
    hid->buttonRelease(button);
}

void Board::mouseMove(int8_t x, int8_t y) {
    hid->mouseMove(x, y);
}

void Board::mouseWheel(int8_t x, int8_t y) {
    hid->mouseWheel(x, y);
}

void Board::updatePackage(const uint8_t *data, uint32_t offset, uint32_t len) {
    memcpy(packageBuffer + offset, data, len);
    currentPackageSize = offset + len;
}
