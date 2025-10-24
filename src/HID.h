#pragma once
#include <cstdint>


class HID {
    public:
    virtual ~HID() = default;
    virtual bool connected();
    virtual void pressAndHold(uint8_t key, uint8_t modifier);
    virtual void press(uint8_t key, uint8_t modifier);
    virtual void releaseKey(uint8_t key, uint8_t modifier);
    virtual void releaseAll();
    virtual void mouseMove(signed char x, signed char y, signed char wheel, signed char hWheel);
};
