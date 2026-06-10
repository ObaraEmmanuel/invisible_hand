#ifdef ESP32S3DEVKIT
#include "ESP32S3Devkit.h"
#include "Adafruit_NeoPixel.h"

#define RANDOM_ANALOGUE  4
#define RGB_LED_PIN 48

ESP32S3Devkit::ESP32S3Devkit() : ESP32BaseBoard(&serialComm, &hidDevice),
                                 rgbLED(1, RGB_LED_PIN, NEO_GRB + NEO_KHZ800) {
    initComm = true;
    autoStart = true;
    analogPin = RANDOM_ANALOGUE;
}

bool ESP32S3Devkit::setup() {
    if (!ESP32BaseBoard::setup())
        return false;

    rgbLED.begin();
    rgbLED.setBrightness(16);
    rgbLED.show();
    return true;
}

void ESP32S3Devkit::updateIndicators() {
    static uint32_t red = Adafruit_NeoPixel::Color(255, 0, 0);
    static uint32_t green = Adafruit_NeoPixel::Color(0, 255, 0);
    static uint32_t blue = Adafruit_NeoPixel::Color(0, 0, 255);

    if (machine.isRunning() && ready()) {
        rgbLED.setPixelColor(0, green);
    }else if (ready()) {
        rgbLED.setPixelColor(0, blue);
    }else {
        rgbLED.setPixelColor(0, red);
    }
    rgbLED.show();
}
#endif
