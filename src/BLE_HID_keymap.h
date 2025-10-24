#pragma once
#include "HIDTypes.h"

// The report map describes the HID device (a keyboard in this case) and
// the messages (reports in HID terms) sent and received.
static const uint8_t REPORT_MAP[] = {
        USAGE_PAGE(1),      0x01,       // Generic Desktop Controls
        USAGE(1),           0x06,       // Keyboard
        COLLECTION(1),      0x01,       // Application
        REPORT_ID(1),       0x01,       //   Report ID (1)
        USAGE_PAGE(1),      0x07,       //   Keyboard/Keypad
        USAGE_MINIMUM(1),   0xE0,       //   Keyboard Left Control
        USAGE_MAXIMUM(1),   0xE7,       //   Keyboard Right Control
        LOGICAL_MINIMUM(1), 0x00,       //   Each bit is either 0 or 1
        LOGICAL_MAXIMUM(1), 0x01,
        REPORT_COUNT(1),    0x08,       //   8 bits for the modifier keys
        REPORT_SIZE(1),     0x01,
        HIDINPUT(1),        0x02,       //   Data, Var, Abs
        REPORT_COUNT(1),    0x01,       //   1 byte (unused)
        REPORT_SIZE(1),     0x08,
        HIDINPUT(1),        0x01,       //   Const, Array, Abs
        REPORT_COUNT(1),    0x06,       //   6 bytes (for up to 6 concurrently pressed keys)
        REPORT_SIZE(1),     0x08,
        LOGICAL_MINIMUM(1), 0x00,
        LOGICAL_MAXIMUM(1), 0x65,       //   101 keys
        USAGE_MINIMUM(1),   0x00,
        USAGE_MAXIMUM(1),   0x65,
        HIDINPUT(1),        0x00,       //   Data, Array, Abs
        REPORT_COUNT(1),    0x05,       //   5 bits (Num lock, Caps lock, Scroll lock, Compose, Kana)
        REPORT_SIZE(1),     0x01,
        USAGE_PAGE(1),      0x08,       //   LEDs
        USAGE_MINIMUM(1),   0x01,       //   Num Lock
        USAGE_MAXIMUM(1),   0x05,       //   Kana
        LOGICAL_MINIMUM(1), 0x00,
        LOGICAL_MAXIMUM(1), 0x01,
        HIDOUTPUT(1),       0x02,       //   Data, Var, Abs
        REPORT_COUNT(1),    0x01,       //   3 bits (Padding)
        REPORT_SIZE(1),     0x03,
        HIDOUTPUT(1),       0x01,       //   Const, Array, Abs
        END_COLLECTION(0),               // End application collection
        // ------------------ mouse -------------------------------------
        USAGE_PAGE(1),       0x01, // USAGE_PAGE (Generic Desktop)
        USAGE(1),            0x02, // USAGE (Mouse)
        COLLECTION(1),       0x01, // COLLECTION (Application)
        USAGE(1),            0x01, //   USAGE (Pointer)
        COLLECTION(1),       0x00, //   COLLECTION (Physical)
        REPORT_ID(1),        0x02, //     REPORT_ID (1)
        // ------------------------------------------------- Buttons (Left, Right, Middle, Back, Forward)
        USAGE_PAGE(1),       0x09, //     USAGE_PAGE (Button)
        USAGE_MINIMUM(1),    0x01, //     USAGE_MINIMUM (Button 1)
        USAGE_MAXIMUM(1),    0x05, //     USAGE_MAXIMUM (Button 5)
        LOGICAL_MINIMUM(1),  0x00, //     LOGICAL_MINIMUM (0)
        LOGICAL_MAXIMUM(1),  0x01, //     LOGICAL_MAXIMUM (1)
        REPORT_SIZE(1),      0x01, //     REPORT_SIZE (1)
        REPORT_COUNT(1),     0x05, //     REPORT_COUNT (5)
        HIDINPUT(1),         0x02, //     INPUT (Data, Variable, Absolute) ;5 button bits
        // ------------------------------------------------- Padding
        REPORT_SIZE(1),      0x03, //     REPORT_SIZE (3)
        REPORT_COUNT(1),     0x01, //     REPORT_COUNT (1)
        HIDINPUT(1),         0x03, //     INPUT (Constant, Variable, Absolute) ;3 bit padding
        // ------------------------------------------------- X/Y position, Wheel
        USAGE_PAGE(1),       0x01, //     USAGE_PAGE (Generic Desktop)
        USAGE(1),            0x30, //     USAGE (X)
        USAGE(1),            0x31, //     USAGE (Y)
        USAGE(1),            0x38, //     USAGE (Wheel)
        LOGICAL_MINIMUM(1),  0x81, //     LOGICAL_MINIMUM (-127)
        LOGICAL_MAXIMUM(1),  0x7f, //     LOGICAL_MAXIMUM (127)
        REPORT_SIZE(1),      0x08, //     REPORT_SIZE (8)
        REPORT_COUNT(1),     0x03, //     REPORT_COUNT (3)
        HIDINPUT(1),         0x06, //     INPUT (Data, Variable, Relative) ;3 bytes (X,Y,Wheel)
        // ------------------------------------------------- Horizontal wheel
        USAGE_PAGE(1),       0x0c, //     USAGE PAGE (Consumer Devices)
        USAGE(2),      0x38, 0x02, //     USAGE (AC Pan)
        LOGICAL_MINIMUM(1),  0x81, //     LOGICAL_MINIMUM (-127)
        LOGICAL_MAXIMUM(1),  0x7f, //     LOGICAL_MAXIMUM (127)
        REPORT_SIZE(1),      0x08, //     REPORT_SIZE (8)
        REPORT_COUNT(1),     0x01, //     REPORT_COUNT (1)
        HIDINPUT(1),         0x06, //     INPUT (Data, Var, Rel)
        END_COLLECTION(0),         //   END_COLLECTION
        END_COLLECTION(0)
};
