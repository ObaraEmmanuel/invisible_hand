#pragma once
#include "HID.h"
#include "IVHComm.h"
#include "IVHMachine.h"

class Board : public IVHMachineInterface {
public:
    IVHMachine machine{this};
    IVHComm comm{*this};
    IVHCommInterface* commInterface;
    const char* name = BOARD_NAME;
    size_t packageBufferSize = PACKAGE_BUFFER_SIZE;

    Board(IVHCommInterface *comm, HID *hid);

    ~Board() override = default;

    [[nodiscard]] uint8_t getInputType() const;

    virtual bool setup() = 0;

    virtual void loop() = 0;

    virtual bool ready() = 0;

    // HID methods

    void pause() override;

    void resume() override;

    void reset() override;

    void keyHold(uint8_t *key, uint8_t len, uint8_t modifier) override;

    void keyRelease(uint8_t *key, uint8_t len, uint8_t modifier) override;

    void buttonHold(uint8_t button) override;

    void buttonRelease(uint8_t button) override;

    void mouseMove(int8_t x, int8_t y) override;

    void mouseWheel(int8_t x, int8_t y) override;

    void updatePackage(const uint8_t *data, uint32_t offset, uint32_t len) override;

protected:
    HID *hid = nullptr;
    uint8_t *packageBuffer = nullptr;
    uint8_t stack[STACK_SIZE]{};
    size_t currentPackageSize = 0;
};
