#include "IVHMachine.h"

#include <algorithm>
#include <cmath>
#include <cstring>

static bool CRC32IsValid(uint32_t expected, const uint8_t* data, size_t len);


IVHMachine::IVHMachine(IVHMachineInterface *interface, const uint8_t *package) : _interface(interface), package(package) {
}

void IVHMachine::setPackage(const uint8_t *_package) {
    package = _package;
    machineReady = false;
}

void IVHMachine::setStackBuffer(uint8_t *_stack, uint64_t _length) {
    stack.buffer = _stack;
    stack.length = _length;
}

void IVHMachine::pause() {
    if (state == IVH_ST_PAUSED || state == IVH_ST_STOPPED)
        return;
    tempState = state;
    state = IVH_ST_PAUSED;
}

void IVHMachine::resume() {
    if (state != IVH_ST_PAUSED)
        return;
    state = tempState;
}

void IVHMachine::setPressInterval(uint64_t _interval) {
    _pressInterval = _interval;
}

uint32_t IVHMachine::getCurrentOffset() const {
    return currentOffset;
}

IVHState_t IVHMachine::getState() const {
    return state;
}

IVHMachineInterface * IVHMachine::getInterface() const {
    return _interface;
}

IVHCommand_t IVHMachine::fetch() {
    IVHCommand_t command = IVH_COM_INVALID;
    uint8_t key = package[currentOffset++];

    switch (key & 0xf0) {
        case 0x00:
            command = _readKey(key);
            break;
        case 0x10:
            command = _readButton(key);
            break;
        case 0x20:
            command = _readMouse(key);
            break;
        case 0x30:
            command = _readDelay(key);
            break;
        case 0x40:
            command = _readDelayRandom(key);
            break;
        case 0xE0:
            command = _readBlock(key);
            break;
        default:
            break;
    }
    return command;
}

IVHCommand_t IVHMachine::_readKey(uint8_t key) {
    IVHCommand_t command = IVH_COM_INVALID;
    switch ((key & 0b1100) >> 2) {
        case 1:
            command = IVH_COM_KEYHOLD;
            break;
        case 2:
            command = IVH_COM_KEYRELEASE;
            break;
        case 3:
            command = IVH_COM_KEYPRESS;
            break;
        default:
            break;
    }

    switch (key & 0xf) {
        case 0x4:
        case 0x8:
        case 0xC: {
            keys[0] = package[currentOffset++];
            param1.len = 1;;
            break;
        }
        case 0x5:
        case 0x9:
        case 0xD: {
            keys[0] = package[currentOffset++];
            param1.len = 1;
            param2.modifier = package[currentOffset++];
            break;
        }
        case 0x6:
        case 0xA:
        case 0xE: {
            param1.len = package[currentOffset++];
            param2.modifier = package[currentOffset++];
            const uint8_t n = std::min(IVH_KEY_BUF_SIZE, static_cast<int>(param1.len));
            std::memcpy(keys, package + currentOffset, n);
            currentOffset += n;
            break;
        }
        case 0xB:
            param1.len = 0;
            param2.modifier = 0;
            break;
        default:
            command = IVH_COM_INVALID;
            break;
    }
    return command;
}

IVHCommand_t IVHMachine::_readButton(uint8_t key) {
    switch (key & 0xf) {
        case 0:
            param1.button = package[currentOffset++];
            return IVH_COM_BUTTONHOLD;
        case 1:
            param1.button = package[currentOffset++];
            return IVH_COM_BUTTONRELEASE;
        case 2:
            param1.button = package[currentOffset++];
            return IVH_COM_BUTTONPRESS;
        case 3:
            param1.button = 0;
            return IVH_COM_BUTTONRELEASE;
        default:
            return IVH_COM_INVALID;
    }
}

IVHCommand_t IVHMachine::_readMouse(uint8_t key) {
    IVHCommand_t command = IVH_COM_INVALID;
    switch (key & 0xf) {
        case 0:
            // Mousewheel(x=param, y=0)
            command = IVH_COM_MOUSEWHEEL;
            param1.delta = static_cast<int8_t>(package[currentOffset++]);
            param2.delta = 0;
            break;
        case 1:
            // Mousewheel(x=0, y=param)
            command = IVH_COM_MOUSEWHEEL;
            param1.delta = 0;
            param2.delta = static_cast<int8_t>(package[currentOffset++]);
            break;
        case 2:
            // Mousemove(x=param, y=0)
            command = IVH_COM_MOUSEMOVE;
            param1.delta = static_cast<int8_t>(package[currentOffset++]);
            param2.delta = 0;
            break;
        case 3:
            // Mousemove(x=0, y=param)
            command = IVH_COM_MOUSEMOVE;
            param1.delta = 0;
            param2.delta = static_cast<int8_t>(package[currentOffset++]);
            break;
        case 4:
            // Mousewheel(x=param, y=param)
            command = IVH_COM_MOUSEWHEEL;
            param1.delta = static_cast<int8_t>(package[currentOffset++]);
            param2.delta = static_cast<int8_t>(package[currentOffset++]);
            break;
        case 5:
            // Mousemove(x=param, y=param)
            command = IVH_COM_MOUSEMOVE;
            param1.delta = static_cast<int8_t>(package[currentOffset++]);
            param2.delta = static_cast<int8_t>(package[currentOffset++]);
            break;
        default:
            break;
    }
    return command;
}

IVHCommand_t IVHMachine::_readDelay(uint8_t key) {
    IVHCommand_t command = IVH_COM_DELAY;

    // Only 0x0 - 0x7 are allowed
    if ((key & 0xf) > 7)
        return IVH_COM_INVALID;

    uint8_t len = (key & 0b111) + 1;
    param1.duration = 0;
    for (uint8_t i = 0; i < len; i++) {
        param1.duration |= package[currentOffset++] << (8 * i);
    }
    return command;
}

IVHCommand_t IVHMachine::_readDelayRandom(uint8_t key) {
    // Start and stop len in bytes
    uint8_t start_len = 1 << (key & 0b11);
    uint8_t stop_len = 1 << ((key >> 2) & 0b11);

    param1.duration = 0;
    for (uint8_t i = 0; i < start_len; i++) {
        param1.duration |= package[currentOffset++] << (8 * i);
    }

    param2.duration = 0;
    for (uint8_t i = 0; i < stop_len; i++) {
        param2.duration |= package[currentOffset++] << (8 * i);
    }
    return IVH_COM_DELAYRANDOM;
}

IVHCommand_t IVHMachine::_readBlock(uint8_t key) {
    switch (key & 0xf) {
        case 0:
            param1.count = 0;
            return IVH_COM_LOOP;
        case 1:
            param1.count = package[currentOffset++];
            param1.count |= package[currentOffset++] << 8;
            return IVH_COM_LOOP;
        case 2:
            param1.count = package[currentOffset++];
            param1.count |= package[currentOffset++] << 8;
            param2.count = package[currentOffset++];
            param2.count |= package[currentOffset++] << 8;
            return IVH_COM_LOOPRANDOM;
        case 3:
            return _readRandomizeBlock();
        case 0xE:
            return IVH_COM_BREAK;
        case 0xF:
            return IVH_COM_END;
        default:
            return IVH_COM_INVALID;
    }
}

IVHCommand_t IVHMachine::_readRandomizeBlock() {
    uint32_t currentDepth = 1, offsetCount = 0, offset = currentOffset, selected = 0;
    uint8_t key = 0, len = 0;
    while (offset < maxOffset) {
        key = package[offset];
        len = IVH_COMMAND_LEN[key];
        if (len == 0)
            return IVH_COM_INVALID;
        if (len == 255) {
            // We add 3 to cover key + mod + len
            len = package[offset + 1] + 3;
        }
        if (currentDepth == 1) {
            // Reservoir sampling
            if (key != 0xEF)
                if (_interface->getRandom(0, offsetCount) == 0)
                    selected = offset;
            offsetCount++;
        }
        offset += len;

        if ((key & 0xF0) == 0xE0) {
            if (key == 0xEF) {
                currentDepth -= 1;
                if (currentDepth == 0)
                    break;
            } else if (key != 0xEE) {
                currentDepth += 1;
            }
        }
    }
    if (selected == 0) {
        return IVH_COM_INVALID;
    }
    currentOffset = selected;
    // fetch selected command
    IVHCommand_t command = fetch();
    // Store a return offset to force execution
    // to continue outside the randomize block
    _returnOffset = offset;
    return command;
}


bool IVHMachine::isBufferValid(const IVHBuffer *buffer) {
    return buffer->buffer != nullptr && buffer->length > 0;
}

uint64_t IVHMachine::read(const uint8_t *buf, uint8_t bytes) {
    uint64_t result = 0;
    for (uint8_t i = 0; i < std::min(static_cast<uint8_t>(8), bytes); i++) {
        result |= buf[i] << (8 * i);
    }
    return result;
}

IVHErr_t IVHMachine::push(uint64_t value, uint8_t bytes) {
    if ((stackPointer + bytes) >= stack.length) {
        return IVH_ERR_STACK_OVERFLOW;
    }
    for (uint8_t i = 0; i < bytes; i++) {
        stack.buffer[stackPointer++] = value & 0xff;
        value >>= 8;
    }
    return IVH_ERR_OK;
}

IVHErr_t IVHMachine::pop(uint64_t *value, uint8_t bytes) {
    if (stackPointer < bytes) {
        return IVH_ERR_STACK_UNDERFLOW;
    }
    uint64_t result = 0;
    for (uint8_t i = 0; i < bytes; i++) {
        result <<= 8;
        result |= stack.buffer[--stackPointer];
    }
    *value = result;
    return IVH_ERR_OK;
}

IVHErr_t IVHMachine::peek(uint64_t *value, uint64_t offset, uint8_t bytes) const {
    if (stackPointer < offset + bytes) {
        return IVH_ERR_STACK_UNDERFLOW;
    }
    uint32_t base = stackPointer - offset - bytes;
    uint64_t result = 0;
    for (uint8_t i = 0; i < bytes; i++) {
        result |= (stack.buffer[base++] << 8 * i);
    }
    *value = result;
    return IVH_ERR_OK;
}


IVHErr_t IVHMachine::beginLoop(uint16_t count) {
    uint32_t _return = 0;
    if (_returnOffset) {
        // consume and reset _returnOffset
        // the loop will jump to this offset once it is done
        // if it is zero, it will continue to the next offset instead
        _return = _returnOffset;
        _returnOffset = 0;
    }
    IVH_TRY(push(_return, sizeof(currentOffset)));
    IVH_TRY(push(currentOffset, sizeof(currentOffset)));
    IVH_TRY(push(count, sizeof(param1.count)));
    IVH_TRY(push(0, sizeof(param1.count)));
    depth++;
    return IVH_ERR_OK;
}


IVHErr_t IVHMachine::endLoop() {
    uint64_t offset = 0, count = 0, currentCount;
    IVH_TRY(peek(&count, sizeof(param1.count), sizeof(param1.count)));
    IVH_TRY(peek(&offset, sizeof(param1.count) * 2, sizeof(currentOffset)));
    if (count == 0) {
        // we are in an infinite loop
        currentOffset = offset;
        return IVH_ERR_OK;
    }
    IVH_TRY(pop(&currentCount, sizeof(param1.count)));

    if (++currentCount >= count) {
        // loop ended continue execution
        IVH_TRY(pop(&count, sizeof(param1.count)));
        IVH_TRY(pop(&offset, sizeof(currentOffset)));
        // return address
        IVH_TRY(pop(&offset, sizeof(currentOffset)));
        // jump to return offset if available
        if (offset > 0)
            currentOffset = offset;
        return IVH_ERR_OK;
    }

    IVH_TRY(push(currentCount, sizeof(param1.count)));
    currentOffset = offset;
    return IVH_ERR_OK;
}

IVHErr_t IVHMachine::breakLoop() {
    if (depth == 0) {
        return IVH_ERR_OK;
    }
    uint64_t dummy = 0;
    // pop all 8 bytes relating to the current loop
    IVH_TRY(pop(&dummy, sizeof(param1.count)*2+sizeof(currentOffset)*2));
    IVH_TRY(fastForwardBlock(nullptr));
    depth--;
    return IVH_ERR_OK;
}

IVHErr_t IVHMachine::fastForwardBlock(uint32_t* finalOffset) {
    if (depth == 0) {
        if (finalOffset != nullptr)
            *finalOffset = currentOffset;
        return IVH_ERR_OK;
    }
    uint32_t currentDepth = 1, offset = currentOffset;
    uint8_t key = 0, len = 0;
    while (offset < maxOffset) {
        key = package[offset];
        len = IVH_COMMAND_LEN[key];
        if (len == 0)
            return IVH_ERR_INVALID_COMMAND;
        if (len == 255) {
            // We add 3 to cover key + mod + len
            len = package[offset + 1] + 3;
        }
        offset += len;

        if ((key & 0xF0) == 0xE0) {
            if (key == 0xEF) {
                currentDepth -= 1;
                if (currentDepth == 0)
                    break;
            } else if (key != 0xEE) {
                currentDepth += 1;
            }
        }
    }
    if (finalOffset == nullptr)
        currentOffset = offset;
    else
        *finalOffset = offset;
    return IVH_ERR_OK;
}


IVHErr_t IVHMachine::start() {
    machineReady = false;
    state = IVH_ST_STOPPED;
    if (package == nullptr)
        return IVH_ERR_PACKAGE_UNSET;
    if (!isBufferValid(&stack))
        return IVH_ERR_STACK_UNSET;

    if (strncmp(reinterpret_cast<const char *>(package), IVH_MAGIC, 4) != 0)
        return IVH_ERR_INVALID_MAGIC;

    if (package[4] > IVH_MAX_VERSION || package[4] < 1)
        return IVH_ERR_UNSUPPORTED_VERSION;

    packageLength = read(package + 6, 4);
    if (packageLength == 0)
        return IVH_ERR_PACKAGE_EMPTY;

    currentOffset = IVH_HEADER_SIZE;
    maxOffset = IVH_HEADER_SIZE + packageLength;

    if (!CRC32IsValid(read(package + maxOffset, sizeof(uint32_t)), package, maxOffset))
        return IVH_ERR_PACKAGE_CORRUPT;

    // reset machine state
    machineReady = true;
    state = IVH_ST_RUNNING;
    _returnOffset = 0;
    depth = 0;
    stackPointer = 0;
    return IVH_ERR_OK;
}

IVHErr_t IVHMachine::execute() {
    if (!machineReady) {
        return IVH_ERR_MACHINE_INVALID;
    }

    if (state == IVH_ST_STOPPED || state == IVH_ST_PAUSED)
        return IVH_ERR_OK;

    currentMicro = _interface->getMicros();
    if (state == IVH_ST_WAITING || state == IVH_ST_WAITING_INTERNAL) {
        if (currentMicro < deadlineMicro) {
            return IVH_ERR_OK;
        }
        if (state == IVH_ST_WAITING)
            state = IVH_ST_RUNNING;
    }

    if (currentOffset >= maxOffset && state == IVH_ST_RUNNING) {
        state = IVH_ST_STOPPED;
        machineReady = false;
        return IVH_ERR_OK;
    }

    IVHCommand_t command = lastCommand;
    if (state == IVH_ST_RUNNING) {
        command = fetch();
        lastCommand = command;
        if (command == IVH_COM_INVALID) {
            machineReady = false;
            return IVH_ERR_INVALID_COMMAND;
        }
    }

    switch (command) {
        case IVH_COM_KEYHOLD:
            // Handle key hold
            _interface->keyHold(keys, param1.len, param2.modifier);
            break;

        case IVH_COM_KEYRELEASE:
            // Handle key release
            _interface->keyRelease(keys, param1.len, param2.modifier);
            break;

        case IVH_COM_KEYPRESS:
            // Handle key press
            if (state == IVH_ST_RUNNING) {
                _interface->keyHold(keys, param1.len, param2.modifier);
                // wait for a short duration before releasing the key
                state = IVH_ST_WAITING_INTERNAL;
                deadlineMicro = _interface->getMicros() + _pressInterval;
            } else if (state == IVH_ST_WAITING_INTERNAL) {
                _interface->keyRelease(keys, param1.len, param2.modifier);
                state = IVH_ST_RUNNING;
            }
            break;

        case IVH_COM_BUTTONHOLD:
            // Handle button hold
            _interface->buttonHold(param1.button);
            break;

        case IVH_COM_BUTTONRELEASE:
            // Handle button release
            _interface->buttonRelease(param1.button);
            break;

        case IVH_COM_BUTTONPRESS:
            // Handle button press
            if (state == IVH_ST_RUNNING) {
                _interface->buttonHold(param1.button);
                // wait for a short duration before releasing the key
                state = IVH_ST_WAITING_INTERNAL;
                deadlineMicro = _interface->getMicros() + _pressInterval;
            } else if (state == IVH_ST_WAITING_INTERNAL) {
                _interface->buttonRelease(param1.button);
                state = IVH_ST_RUNNING;
            }
            break;

        case IVH_COM_MOUSEMOVE:
            // Handle mouse move
            _interface->mouseMove(param1.delta, param2.delta);
            break;

        case IVH_COM_MOUSEWHEEL:
            // Handle mouse wheel
            _interface->mouseWheel(param1.delta, param2.delta);
            break;

        case IVH_COM_DELAY:
            // Handle delay
            state = IVH_ST_WAITING;
            deadlineMicro = _interface->getMicros() + param1.duration;
            break;

        case IVH_COM_DELAYRANDOM:
            // Handle random
            state = IVH_ST_WAITING;
            deadlineMicro = _interface->getMicros() + _interface->getRandom(param1.duration, param2.duration);
            break;

        case IVH_COM_LOOP:
            // Handle loop
            beginLoop(param1.count);
            break;

        case IVH_COM_LOOPRANDOM:
            // Handle random loop
            beginLoop(_interface->getRandom(param1.count, param2.count));
            break;

        case IVH_COM_BREAK:
            // Handle break
            breakLoop();
            break;

        case IVH_COM_END:
            // Handle end
            endLoop();
            break;

        default:
            // Optional: defensive fallback
            // Should never happen if enum is exhaustive
            break;
    }
    if (_returnOffset > 0) {
        // consume and reset return offset if available
        currentOffset = _returnOffset;
        _returnOffset = 0;
    }
    return IVH_ERR_OK;
}

const char* IVHCommandToString(IVHCommand_t cmd) {
    switch (cmd) {
        case IVH_COM_INVALID:       return "IVH_COM_INVALID";
        case IVH_COM_KEYHOLD:       return "IVH_COM_KEYHOLD";
        case IVH_COM_KEYRELEASE:    return "IVH_COM_KEYRELEASE";
        case IVH_COM_KEYPRESS:      return "IVH_COM_KEYPRESS";
        case IVH_COM_BUTTONHOLD:    return "IVH_COM_BUTTONHOLD";
        case IVH_COM_BUTTONRELEASE: return "IVH_COM_BUTTONRELEASE";
        case IVH_COM_BUTTONPRESS:   return "IVH_COM_BUTTONPRESS";
        case IVH_COM_MOUSEMOVE:     return "IVH_COM_MOUSEMOVE";
        case IVH_COM_MOUSEWHEEL:    return "IVH_COM_MOUSEWHEEL";
        case IVH_COM_DELAY:         return "IVH_COM_DELAY";
        case IVH_COM_DELAYRANDOM:   return "IVH_COM_DELAYRANDOM";
        case IVH_COM_LOOP:          return "IVH_COM_LOOP";
        case IVH_COM_LOOPRANDOM:    return "IVH_COM_LOOPRANDOM";
        case IVH_COM_RANDOMIZE:     return "IVH_COM_RANDOMIZE";
        case IVH_COM_BREAK:         return "IVH_COM_BREAK";
        case IVH_COM_END:           return "IVH_COM_END";
        default:                    return "UNKNOWN_COMMAND";
    }
}

const char* IVHErrToString(IVHErr_t err) {
    switch (err) {
        case IVH_ERR_OK:                  return "IVH_ERR_OK";
        case IVH_ERR_MACHINE_INVALID:     return "IVH_ERR_MACHINE_INVALID";
        case IVH_ERR_BUFFER_UNSET:        return "IVH_ERR_BUFFER_UNSET";
        case IVH_ERR_PACKAGE_UNSET:       return "IVH_ERR_PACKAGE_UNSET";
        case IVH_ERR_PACKAGE_CORRUPT:     return "IVH_ERR_PACKAGE_CORRUPT";
        case IVH_ERR_PACKAGE_EMPTY:       return "IVH_ERR_PACKAGE_EMPTY";
        case IVH_ERR_STACK_UNSET:         return "IVH_ERR_STACK_UNSET";
        case IVH_ERR_STACK_OVERFLOW:      return "IVH_ERR_STACK_OVERFLOW";
        case IVH_ERR_STACK_UNDERFLOW:     return "IVH_ERR_STACK_UNDERFLOW";
        case IVH_ERR_OFFSET_BUF_UNSET:    return "IVH_ERR_OFFSET_BUF_UNSET";
        case IVH_ERR_INVALID_MAGIC:       return "IVH_ERR_INVALID_MAGIC";
        case IVH_ERR_UNSUPPORTED_VERSION: return "IVH_ERR_UNSUPPORTED_VERSION";
        case IVH_ERR_INVALID_COMMAND:     return "IVH_ERR_INVALID_COMMAND";
        case IVH_ERR_INTERFACE_UNSET:     return "IVH_ERR_INTERFACE_UNSET";
        default:                          return "IVH_ERR_UNKNOWN_INTERNAL";
    }
}

// CRC-32 (IEEE 802.3, Ethernet/ZIP/PNG)
// poly: 0x04C11DB7 (reflected 0xEDB88320)
// init: 0xFFFFFFFF, xorout: 0xFFFFFFFF, refin/refout: true
bool CRC32IsValid(uint32_t expected, const uint8_t* data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;

    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; ++bit) {
            uint32_t mask = -(crc & 1u);
            crc = (crc >> 1) ^ (0xEDB88320u & mask);
        }
    }

    return (crc ^ 0xFFFFFFFFu) == expected;
}