#pragma once
#include <cstdint>

class HID {
public:
    uint8_t type = 0;
    uint8_t LEDs = 0;

    virtual ~HID() = default;

    virtual bool connected();

    virtual bool begin();

    virtual void pause();

    virtual void resume();

    virtual void reset();

    virtual void keyHold(uint8_t *keys, uint8_t len, uint8_t modifier);

    virtual void keyRelease(uint8_t *keys, uint8_t len, uint8_t modifier);

    virtual void keyReleaseAll();

    virtual void buttonHold(uint8_t buttons);

    virtual void buttonRelease(uint8_t buttons);

    virtual void buttonReleaseAll();

    virtual void mouseMove(int8_t x, int8_t y);

    virtual void mouseWheel(int8_t hWheel, int8_t vWheel);
};
