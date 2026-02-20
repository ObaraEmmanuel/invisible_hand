#pragma once
#include <cstdint>

class HID {
public:
    virtual ~HID() = default;

    virtual bool connected();

    virtual bool begin();

    virtual void holdKey(uint8_t *keys, uint8_t len, uint8_t modifier);

    virtual void releaseKey(uint8_t *keys, uint8_t len, uint8_t modifier);

    virtual void releaseAll();

    virtual void buttonHold(uint8_t buttons);

    virtual void buttonRelease(uint8_t buttons);

    virtual void buttonReleaseAll();

    virtual void mouseMove(int8_t x, int8_t y);

    virtual void mouseWheel(int8_t hWheel, int8_t vWheel);
};
