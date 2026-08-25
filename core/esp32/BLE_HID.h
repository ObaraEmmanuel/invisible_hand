#pragma once

#define US_KEYBOARD 1

#include "BLEDevice.h"
#include "BLEHIDDevice.h"
#include "HID.h"
#include "HIDKeyboardTypes.h"

#define MAX_REPORT_KEYS 6

// Message (report) sent when a key is pressed or released
struct KeyboardInputReport {
    uint8_t modifiers;	                   // bitmask: CTRL = 1, SHIFT = 2, ALT = 4
    uint8_t reserved;                      // must be 0
    uint8_t pressedKeys[MAX_REPORT_KEYS];  // up to six concurrently pressed keys
};

// Message (report) received when an LED's state changed
struct KeyboardOutputReport {
    uint8_t LEDs;                          // bitmask: num lock = 1, caps lock = 2, scroll lock = 4, compose = 8, kana = 16
};

struct LEDReport {
    uint8_t LEDs;            // bitmask: num lock = 1, caps lock = 2, scroll lock = 4, compose = 8, kana = 16
};

enum LEDs {
    NuM_LOCK      = 1,
    CAPS_LOCK     = 1 << 1,
    SCROLL_LOCK   = 1 << 2,
    COMPOSE       = 1 << 3,
    KANA          = 1 << 4,
};


// Message (report) sent for mouse events
struct MouseInputReport {
    uint8_t buttons;
    int8_t x;
    int8_t y;
    int8_t hWheel;
    int8_t vWheel;
};

class BLEHID: public HID, public BLEServerCallbacks, public BLECharacteristicCallbacks{
public:
    BLEHID();

    bool begin() override;

    void pause() override;

    void resume() override;

    void reset() override;

    void onConnect(BLEServer* server) override;

    void onDisconnect(BLEServer* server) override;

    void onWrite(BLECharacteristic* characteristic) override;

    void setBatteryLevel(uint8_t level);

    bool connected() override;

    void keyHold(uint8_t *keys, uint8_t len, uint8_t modifiers) override;

    void keyRelease(uint8_t *keys, uint8_t len, uint8_t modifiers) override;

    void keyReleaseAll() override;

    void buttonHold(uint8_t buttons) override;

    void buttonRelease(uint8_t buttons) override;

    void buttonReleaseAll() override;

    void mouseMove(int8_t x, int8_t y) override;

    void mouseWheel(int8_t hWheel, int8_t vWheel) override;

protected:

    void send_keys() const;

    static KEYMAP get_key(uint8_t key, uint8_t modifier=0);

private:
    BLEHIDDevice* hid{};
    BLECharacteristic* input{};
    BLECharacteristic* output{};
    BLECharacteristic* mouse_input{};
    BLESecurity* security{};
    BLEAdvertising* advertising{};
    BLEServer* _server{};

    volatile bool isConnected{};
    uint8_t battery{};

    uint8_t pressed[MAX_REPORT_KEYS]{};
    uint8_t _modifiers{};
    uint8_t _buttons{};
};
