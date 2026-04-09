#pragma once
#include <cstddef>
#include "HID.h"
#include "IVHMachine.h"

#define IVH_STACK_SIZE 4096
#define IVH_KEY_BUF_SIZE 256


class IVH final : public IVHMachineInterface{
public:
    IVH();
    explicit IVH(HID* device);
    void setDevice(HID* device);
    void setPackageArea(uint8_t *area, size_t size);
    void bind(IVHMachine* machine);
    size_t _macroSize = 0;
private:
    HID* hid_device{};
    uint8_t *_package = nullptr;
    size_t _packageSize = 0;
    uint8_t _stack[IVH_STACK_SIZE] = {};
    uint8_t _keys[IVH_KEY_BUF_SIZE] = {};

protected:
    void keyHold(uint8_t *key, uint8_t len, uint8_t modifier) override;
    void keyRelease(uint8_t *key, uint8_t len, uint8_t modifier) override;
    void buttonHold(uint8_t button) override;
    void buttonRelease(uint8_t button) override;
    void mouseMove(int8_t x, int8_t y) override;
    void mouseWheel(int8_t x, int8_t y) override;
    uint64_t getRandom(uint64_t min, uint64_t max) override;
    uint64_t getMicros() override;
    void updatePackage(const uint8_t *data, uint32_t offset, uint32_t len) override;
    bool flashPackage() override;
};
