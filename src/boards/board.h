#pragma once
#include "IVHComm.h"
#include "IVHMachine.h"

class Board {
public:
    IVHMachine* machineHandle = nullptr;

    IVHComm* commHandle = nullptr;

    virtual ~Board() = default;

    virtual void setup();

    virtual void loop();

    virtual bool ready();
};
