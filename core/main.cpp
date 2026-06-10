#include <Arduino.h>

#include "IVHMachine.h"

#define STRINGIFY_INNER(x) #x
#define STRINGIFY(x) STRINGIFY_INNER(x)
#define BOARD_HEADER_PATH(x) boards/x.h
#define BOARD_HEADER STRINGIFY(BOARD_HEADER_PATH(BOARD_CLASS))

#include BOARD_HEADER
BOARD_CLASS board{};


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
