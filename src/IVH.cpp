#include "IVH.h"

#include <Arduino.h>
#include <esp32-hal.h>

IVH::IVH() : IVH(nullptr) {
}

IVH::IVH(HID *device) {
    if (device != nullptr)
        setDevice(device);
    board = BOARD_NAME;
}

void IVH::setDevice(HID *device) {
    hid_device = device;
}

void IVH::setPackageArea(uint8_t *area) {
    _package = area;
}

void IVH::bind(IVHMachine *machine) {
    machine->setStackBuffer(_stack, IVH_STACK_SIZE);
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

void IVH::updatePackage(const uint8_t *data, uint32_t offset, uint32_t len) {
    memcpy(_package + offset, data, len);
}
