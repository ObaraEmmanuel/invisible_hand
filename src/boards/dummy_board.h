#pragma once
#include "board.h"


class DummyBoard : public Board {
public:
    DummyBoard() = default;

    void setup() override;

    void loop() override;

    bool ready() override;
};
