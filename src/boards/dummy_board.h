#pragma once
#include "board.h"


class DummyBoard : public Board {
public:
    using Board::Board;

    bool setup() override;

    void loop() override;

    bool ready() override;
};
