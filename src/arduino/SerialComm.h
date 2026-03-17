#pragma once
#include "IVHComm.h"

class SerialComm : public IVHCommInterface {
public:
    size_t send(const uint8_t *data, size_t len) override;

    size_t receive(uint8_t *buffer, size_t len) override;

    size_t available() override;
};
