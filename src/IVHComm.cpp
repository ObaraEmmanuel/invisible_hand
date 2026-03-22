#include "IVHComm.h"

#include <algorithm>
#include <cstring>

#define DEFAULT_NAME "Unknown"


IVHComm::IVHComm(IVHCommInterface *comm, IVHMachine *machine) : comm(comm), machine(machine) {
}

bool IVHComm::init() {
    if (machine == nullptr || comm == nullptr) {
        return false;
    }
    if (machine->getInterface() == nullptr) {
        return false;
    }
    machineInterface = machine->getInterface();

    pingDeadline = machineInterface->getMicros() + IVH_COMM_PING_INTERVAL;
    return true;
}

void IVHComm::tick() {
    if (machine == nullptr || comm == nullptr || machineInterface == nullptr) {
        return;
    }
    auto micros = machineInterface->getMicros();
    if (micros > pingDeadline) {
        pingDeadline = micros + IVH_COMM_PING_INTERVAL;
        sendCommand(IVH_COMM_PING);
    }
    size_t available;
    while ((available = comm->available()) > 0) {
        memset(out, 0, IVH_COMM_BUF_SIZE);
        auto len = comm->receive(in, std::min(static_cast<size_t>(IVH_COMM_BUF_SIZE), available));
        size_t offset = 0;
        while (offset < len) {
            switch (state) {
                case IVH_COMM_ST_WAITING_START:
                    if (in[offset++] == reinterpret_cast<const uint8_t *>(IVH_COMM_FRAME_START_DELIMITER)[delimIndex])
                        delimIndex++;
                    else
                        delimIndex = 0;

                    if (delimIndex == IVH_COMM_FRAME_DELIMITER_LEN) {
                        delimIndex = 0;
                        state = IVH_COMM_ST_WAITING_LEN;
                    }
                    break;
                case IVH_COMM_ST_WAITING_LEN:
                    bodyLen = in[offset++];
                    state = IVH_COMM_ST_WAITING_COMMAND;
                    break;
                case IVH_COMM_ST_WAITING_COMMAND:
                    currentCommand = static_cast<IVHCommCommand>(in[offset++]);
                    state = IVH_COMM_ST_WAITING_DATA;
                    break;
                case IVH_COMM_ST_WAITING_DATA: {
                    auto availableBody = std::min(bodyLen, len - offset);
                    memcpy(body, in + offset, availableBody);
                    offset += availableBody;
                    if (availableBody == bodyLen) {
                        state = IVH_COMM_ST_WAITING_END;
                    }
                    break;
                }
                case IVH_COMM_ST_WAITING_END:
                    if (in[offset++] == reinterpret_cast<const uint8_t *>(IVH_COMM_FRAME_END_DELIMITER)[delimIndex])
                        delimIndex++;
                    else {
                        delimIndex = 0;
                        // invalid packet so let's continue reading
                        state = IVH_COMM_ST_WAITING_START;
                    }

                    if (delimIndex == IVH_COMM_FRAME_DELIMITER_LEN) {
                        delimIndex = 0;
                        state = IVH_COMM_ST_WAITING_START;
                        handleCommand();
                    }
                    break;
                case IVH_COMM_ST_READING_PACKAGE: {
                    auto availablePackage = std::min(packageLen - packageRead, len - offset);
                    machineInterface->updatePackage(in + offset, packageRead, availablePackage);
                    offset += availablePackage;
                    packageRead += availablePackage;
                    sendCommand(
                        IVH_COMM_PACKAGE_PROGRESS,
                        reinterpret_cast<const uint8_t *>(&packageRead),
                        sizeof(packageRead)
                    );
                    if (packageRead >= packageLen) {
                        state = IVH_COMM_ST_WAITING_START;
                    }
                    break;
                }
                default:
                    // Unknown state, skip parsing altogether
                    // We should ideally never get here
                    offset = len;
            }
        }
    }
}

void IVHComm::handleCommand() {
    switch (currentCommand) {
        case IVH_COMM_PACKAGE:
            packageLen = readNumber(body, bodyLen);
            packageRead = 0;
            // Pause the machine because we are updating the package currently being read
            machine->pause();
            state = IVH_COMM_ST_READING_PACKAGE;
            break;
        case IVH_COMM_RESTART:
            machine->start();
            break;
        case IVH_COMM_PAUSE:
            machine->pause();
            break;
        case IVH_COMM_RESUME:
            machine->resume();
            break;
        case IVH_COMM_BOARD: {
            const char* board = machineInterface->board;
            if (board == nullptr)
                board = DEFAULT_NAME;
            sendCommand(
                IVH_COMM_BOARD,
                reinterpret_cast<const uint8_t *>(board),
                strlen(board)
            );
            break;
        }
        case IVH_COMM_MEM:
            sendCommand(
                IVH_COMM_MEM,
                reinterpret_cast<const uint8_t *>(&machineInterface->maxPackageSize),
                sizeof(machineInterface->maxPackageSize)
            );
            break;
        case IVH_COMM_INPUT_TYPE:
            sendCommand(
                IVH_COMM_INPUT_TYPE,
                &machineInterface->inputType,
                sizeof(machineInterface->inputType)
            );
            break;
        default:
            // unhandled command, do nothing
            break;
    }
}

uint64_t IVHComm::readNumber(const uint8_t *data, size_t len) {
    uint64_t result = 0;
    for (size_t i = 0; i < len; i++) {
        result |= data[i] << (i * 8);
    }
    return result;
}

void IVHComm::setMachine(IVHMachine *_machine) {
    this->machine = _machine;
}

void IVHComm::setCommInterface(IVHCommInterface *interface) {
    this->comm = interface;
}

void IVHComm::sendCommand(const IVHCommCommand command) {
    sendCommand(command, nullptr, 0);
}

void IVHComm::sendCommand(const IVHCommCommand command, const uint8_t *data, const uint8_t len) {
    memset(out, 0, IVH_COMM_BUF_SIZE);
    size_t offset = 0;
    memcpy(out + offset, IVH_COMM_FRAME_START_DELIMITER, IVH_COMM_FRAME_DELIMITER_LEN);
    offset += IVH_COMM_FRAME_DELIMITER_LEN;
    out[offset++] = len;
    out[offset++] = command;
    if (data != nullptr) {
        memcpy(out + offset, data, len);
        offset += len;
    }
    memcpy(out + offset, IVH_COMM_FRAME_END_DELIMITER, IVH_COMM_FRAME_DELIMITER_LEN);
    offset += IVH_COMM_FRAME_DELIMITER_LEN;
    comm->send(out, offset);
}

const char * IVHCommCommandToString(IVHCommCommand command) {
    switch (command)
    {
        case IVH_COMM_INVALID:           return "IVH_COMM_INVALID";
        case IVH_COMM_PACKAGE:           return "IVH_COMM_PACKAGE";
        case IVH_COMM_BOARD:             return "IVH_COMM_BOARD";
        case IVH_COMM_RESTART:           return "IVH_COMM_RESTART";
        case IVH_COMM_PAUSE:             return "IVH_COMM_PAUSE";
        case IVH_COMM_RESUME:            return "IVH_COMM_RESUME";
        case IVH_COMM_MEM:               return "IVH_COMM_MEM";
        case IVH_COMM_INPUT_TYPE:        return "IVH_COMM_INPUT_TYPE";
        case IVH_COMM_PACKAGE_PROGRESS:  return "IVH_COMM_PACKAGE_PROGRESS";
        case IVH_COMM_PING:              return "IVH_COMM_PING";
    }
    return "IVH_COMM_UNKNOWN";
}