#include "BLE_HID.h"
#include "BLE_HID_keymap.h"

BLEHID* BLEHID::instance = nullptr;


BLEHID::BLEHID() {
    _server = BLEDevice::createServer();
    _server->setCallbacks(this);

    // create an HID device
    hid = new BLEHIDDevice(_server);
    input = hid->inputReport(1); // report ID
    output = hid->outputReport(1); // report ID
    mouse_input = hid->inputReport(2);

    output->setCallbacks(this);

    // set manufacturer name
    hid->manufacturer()->setValue("Barracoder");
    // set USB vendor and product ID
    hid->pnp(0x02, 0xe502, 0xa111, 0x0210);
    // information about HID device: device is not localized, device can be connected
    hid->hidInfo(0x00, 0x02);

    // Security: device requires bonding
    security = new BLESecurity();
    security->setAuthenticationMode(ESP_LE_AUTH_BOND);

    // set report map
    hid->reportMap((uint8_t*)REPORT_MAP, sizeof(REPORT_MAP));
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
}

BLEHID *BLEHID::getInstance() {
    return instance;
}

void BLEHID::onConnect(BLEServer *server) {
    isConnected = true;

    // Allow notifications for characteristics
    BLE2902* cccDesc = (BLE2902*)input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    cccDesc->setNotifications(true);
    cccDesc = (BLE2902*)mouse_input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    cccDesc->setNotifications(true);
    Serial.println("keyboard connected");
}

void BLEHID::onDisconnect(BLEServer *server) {
    isConnected = false;

    // Disallow notifications for characteristics
    BLE2902* cccDesc = (BLE2902*)input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    cccDesc->setNotifications(false);
    cccDesc = (BLE2902*)mouse_input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    cccDesc->setNotifications(false);
    Serial.println("keyboard disconnected");
}

void BLEHID::onWrite(BLECharacteristic *characteristic) {
    // OutputReport* report = (OutputReport*) characteristic->getData();
    // hasCapsLock = report->LEDs & 0x2;
}

void BLEHID::setBatteryLevel(uint8_t level) {
    battery = level;

    if(hid)
        hid->setBatteryLevel(battery);
}

void BLEHID::pressAndHold(uint8_t key, uint8_t modifier) {
    KEYMAP map = get_key(key, modifier);
    if(map.modifier == 0xff)
        return;

    if(pressed_index >= 6)
        return;

    pressed[pressed_index++] = map;

    send_keys();
}

void BLEHID::press(uint8_t key, uint8_t modifier){
    pressAndHold(key, modifier);
    delay(5);
    releaseKey(key, modifier);
}

void BLEHID::releaseKey(uint8_t key, uint8_t modifier) {
    KEYMAP map = get_key(key, modifier);
    if(map.modifier == 0xff)
        return;

    bool overwrite = false;

    for(int i = 0; i < pressed_index; i++){
        if(overwrite){
            pressed[i - 1] = pressed[i];
            if((i + 1) == pressed_index){
                pressed[i] = {};
            }
            continue;
        }

        if(pressed[i].modifier == map.modifier && pressed[i].usage == map.usage){
            overwrite = true;
        }
    }

    if(overwrite){
        pressed_index--;
    }

    send_keys();
}

void BLEHID::releaseAll() {
    if(!pressed_index)
        return;
    bzero(pressed, sizeof(pressed));
    pressed_index = 0;
    send_keys();
}

void BLEHID::send_keys() {
    if(!isConnected)
        return;
    InputReport report = {};
    for(int i = 0; i < pressed_index; i++){
        report.pressedKeys[i] = pressed[i].usage;
        report.modifiers |= pressed[i].modifier;
    }

    input->setValue((uint8_t*)&report, sizeof(report));
    input->notify();
}

KEYMAP BLEHID::get_key(uint8_t key, uint8_t modifier) {
    if(key >= KEYMAP_SIZE){
        // key not supported
        // return invalid sentinel
        return {0xff, 0xff};
    }
    KEYMAP original = keymap[key];
    if(modifier)
        return {original.usage, static_cast<unsigned char>(original.modifier | modifier)};
    return original;
}

bool BLEHID::connected() {
    return isConnected;
}

void BLEHID::reEnforce() {
    InputReport report = {};
    input->setValue((uint8_t*)&report, sizeof(report));
    input->notify();

    send_keys();
}

void BLEHID::mouseMove(signed char x, signed char y, signed char wheel, signed char hWheel){
    if(!isConnected)
        return;
    uint8_t m[5];
    m[0] = 0;
    m[1] = x;
    m[2] = y;
    m[3] = wheel;
    m[4] = hWheel;
    mouse_input->setValue(m, 5);
    mouse_input->notify();
}
