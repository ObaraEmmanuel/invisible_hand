#include <Arduino.h>

#include "boards/board.h"

#ifdef NODEMCU_32S

#include "boards/nodemcu_32s.h"
NodeMCU32s board{};

#elif defined ESP32_S3_N16R8V

#include "boards/esp32_s3_devkit.h"
ESP32S3Devkit board{};

#else

#include "boards/dummy_board.h"
DummyBoard board{};

#endif

bool boardReady = false;

void setup() {
    Serial.begin(115200);
    boardReady = board.setup();
}

void loop() {
    if (!boardReady) {
        delay(1000);
        return;
    }
    board.comm.tick();
    board.loop();
    if (!board.ready()) {
        delay(10);
        return;
    }
    IVHErr err = board.machine.execute();
    if (err == IVH_ERR_MACHINE_INVALID) {
        delay(10);
        return;
    }
    if (err != IVH_ERR_OK) {
        Serial.print("IVH Runtime Error: ");
        Serial.println(IVHErrToString(err));
    }
}
