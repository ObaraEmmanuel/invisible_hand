#pragma once
#include "board.h"


class ESP32BaseBoard : public Board {
public:
    using Board::Board;
    bool setup() override;
    uint64_t getRandom(uint64_t min, uint64_t max) override;
    uint64_t getMicros() override;
    bool flashPackage() override;
protected:
    size_t maxPackageSize=0;
    bool hasFileSystem = false;
};
