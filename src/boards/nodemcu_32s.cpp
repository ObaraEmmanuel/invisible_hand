#include "nodemcu_32s.h"

#define RANDOM_ANALOGUE    25

NodeMCU32s::NodeMCU32s() : ESP32BaseBoard(&serialComm, &hidDevice) {
    initComm = true;
    autoStart = true;
    analogPin = RANDOM_ANALOGUE;
}
