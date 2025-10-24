#pragma once

#define US_KEYBOARD 1

#include <Arduino.h>
#include "BLEDevice.h"
#include "BLEHIDDevice.h"
#include "HID.h"
#include "HIDKeyboardTypes.h"


// Message (report) sent when a key is pressed or released
struct InputReport {
    uint8_t modifiers;	     // bitmask: CTRL = 1, SHIFT = 2, ALT = 4
    uint8_t reserved;        // must be 0
    uint8_t pressedKeys[6];  // up to six concurrently pressed keys
};

// Message (report) received when an LED's state changed
struct OutputReport {
    uint8_t LEDs;            // bitmask: num lock = 1, caps lock = 2, scroll lock = 4, compose = 8, kana = 16
};



class BLEHID: public HID, public BLEServerCallbacks, public BLECharacteristicCallbacks{
public:
    BLEHID();
    static BLEHID* getInstance();

    void onConnect(BLEServer* server) override;

    void onDisconnect(BLEServer* server) override;

    /**
     * Called when the client (computer, smart phone) wants to turn on or off
     * the LEDs in the keyboard.
     *
     * bit 0 - NUM LOCK
     * bit 1 - CAPS LOCK
     * bit 2 - SCROLL LOCK
     */
    void onWrite(BLECharacteristic* characteristic) override;

    void setBatteryLevel(uint8_t level);

    void pressAndHold(uint8_t key, uint8_t modifier) override;

    void press(uint8_t key, uint8_t modifier) override;

    void releaseKey(uint8_t key, uint8_t modifier) override;

    void releaseAll() override;

    void mouseMove(signed char x, signed char y, signed char wheel, signed char hWheel) override;

    void reEnforce();

    bool connected() override;

protected:

    void send_keys();

    static KEYMAP get_key(uint8_t key, uint8_t modifier=0);

private:
    BLEHIDDevice* hid;
    BLECharacteristic* input;
    BLECharacteristic* output;
    BLECharacteristic* mouse_input;
    BLESecurity* security;
    BLEAdvertising* advertising;
    BLEServer* _server;

    static BLEHID* instance;

    bool isConnected{};
    uint8_t battery{};

    KEYMAP pressed[6]{};
    uint8_t pressed_index = 0;
};
