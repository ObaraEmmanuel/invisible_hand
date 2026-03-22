#include "BLE_HID.h"
#include "BLE_HID_report.h"

BLEHID *BLEHID::instance = nullptr;


BLEHID::BLEHID() = default;

BLEHID *BLEHID::getInstance() {
    return instance;
}

bool BLEHID::begin() {
    _server = BLEDevice::createServer();
    _server->setCallbacks(this);

    // create an HID device
    hid = new BLEHIDDevice(_server);
    input = hid->inputReport(1); // report ID
    output = hid->outputReport(1); // report ID
    mouse_input = hid->inputReport(2);

    output->setCallbacks(this);

    // set manufacturer name
    hid->manufacturer()->setValue("IVH");
    // set USB vendor and product ID
    hid->pnp(0x02, 0xe502, 0xa111, 0x0210);
    // information about HID device: device is not localized, device can be connected
    hid->hidInfo(0x00, 0x02);

    // Security: device requires bonding
    security = new BLESecurity();
    security->setAuthenticationMode(ESP_LE_AUTH_BOND);

    // set report map
    hid->reportMap(const_cast<uint8_t *>(REPORT_MAP), sizeof(REPORT_MAP));
    hid->startServices();

    // set battery level to 100%
    setBatteryLevel(100);

    // advertise the services
    advertising = _server->getAdvertising();
    advertising->setAppearance(HID_KEYBOARD);
    advertising->addServiceUUID(hid->hidService()->getUUID());
    advertising->addServiceUUID(hid->deviceInfo()->getUUID());
    advertising->addServiceUUID(hid->batteryService()->getUUID());
    advertising->start();

    instance = this;
    return true;
}

void BLEHID::onConnect(BLEServer *server) {
    isConnected = true;

    // Allow notifications for characteristics
    BLE2902 *cccDesc = (BLE2902 *) input->getDescriptorByUUID(BLEUUID(static_cast<uint16_t>(0x2902)));
    cccDesc->setNotifications(true);
    cccDesc = (BLE2902 *) mouse_input->getDescriptorByUUID(BLEUUID(static_cast<uint16_t>(0x2902)));
    cccDesc->setNotifications(true);
    Serial.println("keyboard connected");
}

void BLEHID::onDisconnect(BLEServer *server) {
    isConnected = false;

    // Disallow notifications for characteristics
    BLE2902 *cccDesc = (BLE2902 *) input->getDescriptorByUUID(BLEUUID(static_cast<uint16_t>(0x2902)));
    cccDesc->setNotifications(false);
    cccDesc = (BLE2902 *) mouse_input->getDescriptorByUUID(BLEUUID(static_cast<uint16_t>(0x2902)));
    cccDesc->setNotifications(false);
    _server->getAdvertising()->start();
    Serial.println("keyboard disconnected");
}

void BLEHID::onWrite(BLECharacteristic *characteristic) {
    // OutputReport* report = (OutputReport*) characteristic->getData();
    // hasCapsLock = report->LEDs & 0x2;
}

void BLEHID::setBatteryLevel(uint8_t level) {
    battery = level;

    if (hid)
        hid->setBatteryLevel(battery);
}

void BLEHID::holdKey(uint8_t *keys, uint8_t len, uint8_t modifiers) {
    if (!isConnected)
        return;
    for (uint8_t i = 0; i < len; i++) {
        int index = -1;
        bool found = false;
        uint8_t key = keys[i];
        for (uint8_t j = 0; j < MAX_REPORT_KEYS; j++) {
            if (pressed[j] == 0 && index == -1)
                index = j;
            if (pressed[j] == key) {
                found = true;
            }
        }
        if (index == -1) {
            // there are 6 keys already being pressed
            break;
        }
        if (!found)
            pressed[index] = key;
    }
    _modifiers |= modifiers;
    send_keys();
}

void BLEHID::releaseKey(uint8_t *keys, uint8_t len, uint8_t modifiers) {
    if (!isConnected)
        return;
    for (uint8_t i = 0; i < len; i++) {
        for (unsigned char &j: pressed) {
            if (j == keys[i]) {
                j = 0;
            }
        }
    }
    _modifiers &= ~modifiers;
    send_keys();
}

void BLEHID::releaseAll() {
    if (!isConnected)
        return;
    memset(pressed, 0, sizeof(uint8_t) * MAX_REPORT_KEYS);
    _modifiers = 0;
    send_keys();
}

void BLEHID::buttonHold(uint8_t buttons) {
    if (!isConnected)
        return;
    _buttons |= buttons;
    MouseInputReport report = {.buttons = _buttons};
    mouse_input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    mouse_input->notify();
}

void BLEHID::buttonRelease(uint8_t buttons) {
    if (!isConnected)
        return;
    _buttons &= ~buttons;
    MouseInputReport report = {.buttons = _buttons};
    mouse_input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    mouse_input->notify();
}

void BLEHID::buttonReleaseAll() {
    if (!isConnected)
        return;
    _buttons = 0;
    MouseInputReport report = {.buttons = _buttons};
    mouse_input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    mouse_input->notify();
}

void BLEHID::mouseMove(int8_t x, int8_t y) {
    if (!isConnected)
        return;
    MouseInputReport report = {.x = x, .y = y};
    mouse_input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    mouse_input->notify();
}

void BLEHID::mouseWheel(int8_t hWheel, int8_t vWheel) {
    if (!isConnected)
        return;
    MouseInputReport report = {.hWheel = hWheel, .vWheel = vWheel};
    mouse_input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    mouse_input->notify();
}

void BLEHID::send_keys() const {
    if (!isConnected)
        return;
    KeyboardInputReport report = {};
    int index = 0;
    for (unsigned char i: pressed) {
        if (i != 0) {
            report.pressedKeys[index++] = i;
        }
    }
    report.modifiers = _modifiers;

    input->setValue(reinterpret_cast<uint8_t *>(&report), sizeof(report));
    input->notify();
}

KEYMAP BLEHID::get_key(uint8_t key, uint8_t modifier) {
    if (key >= KEYMAP_SIZE) {
        // key not supported
        // return invalid sentinel
        return {0xff, 0xff};
    }
    KEYMAP original = keymap[key];
    if (modifier)
        return {original.usage, static_cast<unsigned char>(original.modifier | modifier)};
    return original;
}

bool BLEHID::connected() {
    return isConnected;
}
