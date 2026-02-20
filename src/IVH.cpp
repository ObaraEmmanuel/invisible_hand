#include "IVH.h"

#include <Arduino.h>
#include <esp32-hal.h>

IVH::IVH() {
    stack.buffer = _stack;
    stack.length = IVH_STACK_SIZE;
    keys.buffer = _keys;
    keys.length = IVH_KEY_BUF_SIZE;
}

void IVH::setDevice(HID *device) {
    hid_device = device;
}

void IVH::buttonHold(uint8_t button) {
    hid_device->buttonHold(button);
}

void IVH::buttonRelease(uint8_t button) {
    hid_device->buttonRelease(button);
}

void IVH::keyHold(uint8_t *key, uint8_t len, uint8_t modifier) {
    hid_device->holdKey(key, len, modifier);
}

void IVH::keyRelease(uint8_t *key, uint8_t len, uint8_t modifier) {
    if (len == 0 && modifier == 0) {
        hid_device->releaseAll();
        return;
    }
    hid_device->releaseKey(key, len, modifier);
}

void IVH::mouseMove(int8_t x, int8_t y) {
    hid_device->mouseMove(x, y);
}

void IVH::mouseWheel(int8_t x, int8_t y) {
    hid_device->mouseWheel(x, y);
}

uint64_t IVH::getRandom(uint64_t min, uint64_t max) {
    return random(static_cast<long>(min), static_cast<long>(max));
}

uint64_t IVH::getMicros() {
    return micros();
}
