#pragma once

#include <cstdint>

#define IVH_MAGIC "IVH\x99"
#define IVH_MAX_VERSION 1
#define IVH_HEADER_SIZE 10
#define IVH_KEY_BUF_SIZE 256

static const uint8_t IVH_COMMAND_LEN[256] = {
    /*      0    1    2    3    4    5    6    7    8    9    A    B    C    D    E    F */
    /* 0 */   0,   0,   0,   0,   2,   3, 255,   0,   2,   3, 255,   1,   2,   3, 255,   0,
    /* 1 */   2,   2,   2,   1,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 2 */   2,   2,   2,   2,   3,   3,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 3 */   2,   3,   4,   5,   6,   7,   8,   9,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 4 */   3,   0,   0,   0,   4,   5,   0,   0,   6,   7,   9,   0,  10,  11,  13,  17,
    /* 5 */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 6 */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 7 */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 8 */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* 9 */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* A */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* B */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* C */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* D */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    /* E */   1,   3,   5,   1,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   1,   1,
    /* F */   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0
};


typedef enum IVHErr {
    IVH_ERR_OK = 0,
    IVH_ERR_MACHINE_INVALID,
    IVH_ERR_INTERFACE_UNSET,
    IVH_ERR_BUFFER_UNSET,
    IVH_ERR_PACKAGE_UNSET,
    IVH_ERR_PACKAGE_CORRUPT,
    IVH_ERR_STACK_UNSET,
    IVH_ERR_STACK_OVERFLOW,
    IVH_ERR_STACK_UNDERFLOW,
    IVH_ERR_OFFSET_BUF_UNSET,
    IVH_ERR_INVALID_MAGIC,
    IVH_ERR_UNSUPPORTED_VERSION,
    IVH_ERR_INVALID_COMMAND,
} IVHErr_t;

// Assumes IVHErr_t and IVH_ERR_OK exist
#define IVH_TRY(expr)                         \
    do {                                      \
        IVHErr_t _ivh_err = (expr);           \
        if (_ivh_err != IVH_ERR_OK)           \
            return _ivh_err;                  \
    } while (0)


typedef enum IVHState {
    IVH_ST_STOPPED = 0,
    IVH_ST_WAITING,
    IVH_ST_WAITING_INTERNAL,
    IVH_ST_RUNNING,
    IVH_ST_PAUSED,
} IVHState_t;

typedef enum IVHCommand {
    IVH_COM_INVALID,
    IVH_COM_KEYHOLD,
    IVH_COM_KEYRELEASE,
    IVH_COM_KEYPRESS,
    IVH_COM_BUTTONHOLD,
    IVH_COM_BUTTONRELEASE,
    IVH_COM_BUTTONPRESS,
    IVH_COM_MOUSEMOVE,
    IVH_COM_MOUSEWHEEL,
    IVH_COM_DELAY,
    IVH_COM_DELAYRANDOM,
    IVH_COM_LOOP,
    IVH_COM_LOOPRANDOM,
    IVH_COM_RANDOMIZE,
    IVH_COM_BREAK,
    IVH_COM_END,
} IVHCommand_t;

typedef union IVHParam {
    uint8_t key;
    uint8_t len;
    uint8_t modifier;
    uint8_t button;
    int8_t delta;
    uint16_t count;
    uint64_t duration;
} IVHParam_t;

typedef struct IVHBuffer {
    uint8_t *buffer;
    uint64_t length;
} IVHBuffer_t;

typedef enum IVHInputType {
    IVH_INPUT_NONE       = 0,
    IVH_INPUT_USB        = 1,
    IVH_INPUT_BLE        = 1 << 1,
    IVH_INPUT_KEYBOARD   = 1 << 2,
    IVH_INPUT_MOUSE      = 1 << 3,
} IVHInputType_t;

const char *IVHCommandToString(IVHCommand_t cmd);

const char *IVHErrToString(IVHErr_t err);

class IVHMachineInterface {
public:
    const char* board = nullptr;
    uint8_t inputType = IVH_INPUT_NONE;
    uint64_t maxPackageSize = 0;

    virtual ~IVHMachineInterface() = default;

    virtual uint64_t getRandom(uint64_t min, uint64_t max) = 0;

    virtual void keyHold(uint8_t *key, uint8_t len, uint8_t modifier) = 0;

    virtual void keyRelease(uint8_t *key, uint8_t len, uint8_t modifier) = 0;

    virtual void buttonHold(uint8_t button) = 0;

    virtual void buttonRelease(uint8_t button) = 0;

    virtual void mouseMove(int8_t x, int8_t y) = 0;

    virtual void mouseWheel(int8_t x, int8_t y) = 0;

    virtual uint64_t getMicros() = 0;

    virtual void updatePackage(const uint8_t* data, uint32_t offset, uint32_t len) = 0;
};

class IVHMachine {
public:
    IVHCommand_t lastCommand = IVH_COM_INVALID;

    IVHMachine() = default;

    IVHMachine(IVHMachineInterface *interface, const uint8_t *package);

    virtual ~IVHMachine() = default;

    void setPackage(const uint8_t *_package);

    void setStackBuffer(uint8_t *_stack, uint64_t _length);

    void pause();

    void resume();

    void setPressInterval(uint64_t _interval);

    [[nodiscard]] uint32_t getCurrentOffset() const;

    [[nodiscard]] IVHState_t getState() const;

    [[nodiscard]] IVHMachineInterface *getInterface() const;

    IVHCommand_t fetch();

    IVHErr_t start();

    IVHErr_t execute();

private:
    bool machineReady = false;
    uint32_t _returnOffset = 0;
    uint64_t _pressInterval = 5000; //5ms
    IVHMachineInterface* _interface = nullptr;

    IVHCommand_t _readKey(uint8_t key);

    IVHCommand_t _readButton(uint8_t key);

    IVHCommand_t _readMouse(uint8_t key);

    IVHCommand_t _readDelay(uint8_t key);

    IVHCommand_t _readDelayRandom(uint8_t key);

    IVHCommand_t _readRandomizeBlock();

    IVHCommand_t _readBlock(uint8_t key);

    static bool isBufferValid(const IVHBuffer *buffer);

    static uint64_t read(const uint8_t *buf, uint8_t bytes);

    IVHErr_t push(uint64_t value, uint8_t bytes);

    IVHErr_t pop(uint64_t *value, uint8_t bytes);

    IVHErr_t peek(uint64_t *value, uint64_t offset, uint8_t bytes) const;

    IVHErr_t beginLoop(uint16_t count);

    IVHErr_t endLoop();

    IVHErr_t fastForwardBlock(uint32_t *finalOffset);

    IVHErr_t breakLoop();

protected:
    uint64_t packageLength = 0;
    uint32_t currentOffset = 0;
    uint32_t maxOffset = 0;
    uint32_t stackPointer = 0;
    uint16_t depth = 0;
    const uint8_t *package = nullptr;
    uint8_t keys[IVH_KEY_BUF_SIZE] = {};
    IVHBuffer stack = {};
    IVHErr err = IVH_ERR_OK;
    IVHState state = IVH_ST_STOPPED, tempState = {};
    uint64_t currentMicro = 1, deadlineMicro = 0;
    IVHParam param1 = {}, param2 = {}, param3 = {};
};
