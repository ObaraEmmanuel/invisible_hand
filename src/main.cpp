#include <Arduino.h>

#include "boards/board.h"

#ifdef NODEMCU_32S

#include "boards/nodemcu_32s.h"
NodeMCU32s boardInstance;

#else

#include "boards/dummy_board.h"
DummyBoard boardInstance;

#endif

Board *board = nullptr;

void setup() {
    Serial.begin(115200);
    board = &boardInstance;
    board->setup();
}

void loop() {
    if (board == nullptr) {
        delay(1000);
        return;
    }
    board->commHandle->tick();
    board->loop();
    if (!board->ready()) {
        delay(10);
        return;
    }
    IVHErr err = board->machineHandle->execute();
    if (err == IVH_ERR_MACHINE_INVALID) {
        delay(10);
        return;
    }
    if (err != IVH_ERR_OK) {
        Serial.print("IVH Runtime Error: ");
        Serial.println(IVHErrToString(err));
    }
}
