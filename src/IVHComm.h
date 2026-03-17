#pragma once
#include <cstdint>
#include <cstdlib>

#include "IVHMachine.h"

#define IVH_COMM_BUF_SIZE 256
#define IVH_COMM_MAX_BODY_SIZE 128
#define IVH_COMM_PING_INTERVAL 1000000 // us
#define IVH_COMM_FRAME_DELIMITER "\x99\x99"
#define IVH_COMM_FRAME_DELIMITER_LEN 2

typedef enum IVHCommCommand {
    IVH_COMM_INVALID = 0,
    // client to board command
    IVH_COMM_PACKAGE = 0x10,
    IVH_COMM_RESTART,
    IVH_COMM_PAUSE,
    IVH_COMM_RESUME,
    // client to board data request
    IVH_COMM_BOARD = 0x20,
    IVH_COMM_MEM,
    IVH_COMM_INPUT_TYPE,
    // board to client
    IVH_COMM_PACKAGE_PROGRESS = 0x30,
    IVH_COMM_PING = 0x99,
} IVHCommCommand_t;

typedef enum IVHCommState {
    IVH_COMM_ST_WAITING_START,
    IVH_COMM_ST_WAITING_END,
    IVH_COMM_ST_WAITING_LEN,
    IVH_COMM_ST_WAITING_COMMAND,
    IVH_COMM_ST_WAITING_DATA,
    IVH_COMM_ST_READING_PACKAGE,
} IVHCommState_t;

class IVHCommInterface {
public:
    virtual ~IVHCommInterface() = default;

    virtual size_t send(const uint8_t *data, size_t len) = 0;

    virtual size_t receive(uint8_t *buffer, size_t len) = 0;

    virtual size_t available() = 0;
};

const char * IVHCommCommandToString(IVHCommCommand command);

class IVHComm {
public:
    IVHComm() = default;

    IVHComm(IVHCommInterface *comm, IVHMachine *machine);

    ~IVHComm() = default;

    bool init();

    void tick();

    void setMachine(IVHMachine *_machine);

    void setCommInterface(IVHCommInterface *interface);

    void sendCommand(IVHCommCommand command);

    void sendCommand(IVHCommCommand command, const uint8_t *data, uint8_t len);

private:
    IVHCommInterface *comm = nullptr;
    IVHMachine *machine = nullptr;
    IVHMachineInterface *machineInterface = nullptr;
    uint8_t in[IVH_COMM_BUF_SIZE] = {};
    uint8_t out[IVH_COMM_BUF_SIZE] = {};
    uint8_t body[IVH_COMM_BUF_SIZE] = {};
    uint64_t pingDeadline = 0;
    IVHCommState state = IVH_COMM_ST_WAITING_START;
    uint8_t delimIndex = 0;
    size_t bodyLen = 0;
    size_t packageLen = 0;
    size_t packageRead = 0;
    IVHCommCommand currentCommand = IVH_COMM_INVALID;

    void handleCommand();

    static uint64_t readNumber(const uint8_t *data, size_t len);
};
