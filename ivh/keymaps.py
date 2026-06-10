import json
from collections.abc import Iterable
from enum import Enum


class Button(Enum):
    LEFT = "LeftClick"
    RIGHT = "RightClick"
    MIDDLE = "MiddleClick"
    BACK = "BackClick"
    FORWARD = "ForwardClick"


class Key(Enum):
    # Letters
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    J = "J"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    O = "O"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"

    # Numbers (main keyboard)
    DIGIT_0 = "0"
    DIGIT_1 = "1"
    DIGIT_2 = "2"
    DIGIT_3 = "3"
    DIGIT_4 = "4"
    DIGIT_5 = "5"
    DIGIT_6 = "6"
    DIGIT_7 = "7"
    DIGIT_8 = "8"
    DIGIT_9 = "9"

    # Function keys
    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    F7 = "F7"
    F8 = "F8"
    F9 = "F9"
    F10 = "F10"
    F11 = "F11"
    F12 = "F12"

    # Modifier keys
    SHIFT = "Shift"
    LEFT_SHIFT = "Shift_L"
    RIGHT_SHIFT = "Shift_R"
    CONTROL = "Control"
    LEFT_CONTROL = "Control_L"
    RIGHT_CONTROL = "Control_R"
    ALT = "Alt"
    LEFT_ALT = "Alt_L"
    RIGHT_ALT = "Alt_R"
    CAPS_LOCK = "CapsLock"
    TAB = "Tab"
    ESCAPE = "Escape"
    WINDOWS = "Windows"
    MENU = "Menu"

    # Navigation keys
    ENTER = "Enter"
    BACKSPACE = "Backspace"
    SPACE = "Space"
    INSERT = "Insert"
    DELETE = "Delete"
    HOME = "Home"
    END = "End"
    PAGE_UP = "PageUp"
    PAGE_DOWN = "PageDown"
    UP_ARROW = "Up"
    DOWN_ARROW = "Down"
    LEFT_ARROW = "Left"
    RIGHT_ARROW = "Right"

    # Punctuation & symbols
    MINUS = "-"
    EQUAL = "="
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    BACKSLASH = "\\"
    SEMICOLON = ";"
    QUOTE = "'"
    COMMA = ","
    PERIOD = "."
    SLASH = "/"
    BACKQUOTE = "`"

    # Numpad keys
    NUMPAD_0 = "Numpad0"
    NUMPAD_1 = "Numpad1"
    NUMPAD_2 = "Numpad2"
    NUMPAD_3 = "Numpad3"
    NUMPAD_4 = "Numpad4"
    NUMPAD_5 = "Numpad5"
    NUMPAD_6 = "Numpad6"
    NUMPAD_7 = "Numpad7"
    NUMPAD_8 = "Numpad8"
    NUMPAD_9 = "Numpad9"
    NUMPAD_ADD = "NumpadAdd"
    NUMPAD_SUBTRACT = "NumpadSubtract"
    NUMPAD_MULTIPLY = "NumpadMultiply"
    NUMPAD_DIVIDE = "NumpadDivide"
    NUMPAD_DECIMAL = "NumpadDecimal"
    NUMPAD_ENTER = "NumpadEnter"
    NUM_LOCK = "NumLock"

    # Media keys
    PLAY_PAUSE = "PlayPause"
    STOP = "Stop"
    NEXT_TRACK = "NextTrack"
    PREVIOUS_TRACK = "PreviousTrack"
    MUTE = "Mute"
    VOLUME_UP = "VolumeUp"
    VOLUME_DOWN = "VolumeDown"
    MEDIA_SELECT = "MediaSelect"
    LAUNCH_MAIL = "LaunchMail"
    LAUNCH_MEDIA_PLAYER = "LaunchMediaPlayer"
    LAUNCH_APP1 = "LaunchApp1"
    LAUNCH_APP2 = "LaunchApp2"

    # System keys
    PRINT_SCREEN = "PrintScreen"
    SCROLL_LOCK = "ScrollLock"
    PAUSE = "Pause"


KEYSYM_MAP = {
    "Control_L": Key.LEFT_CONTROL,
    "Control_R": Key.RIGHT_CONTROL,
    "Shift_L": Key.LEFT_SHIFT,
    "Shift_R": Key.RIGHT_SHIFT,
    "Alt_L": Key.LEFT_ALT,
    "Alt_R": Key.RIGHT_ALT,
    "Win_L": Key.WINDOWS
}

WINDOWS_CODES = {
    # Letters
    Key.A: 0x41, Key.B: 0x42, Key.C: 0x43, Key.D: 0x44, Key.E: 0x45,
    Key.F: 0x46, Key.G: 0x47, Key.H: 0x48, Key.I: 0x49, Key.J: 0x4A,
    Key.K: 0x4B, Key.L: 0x4C, Key.M: 0x4D, Key.N: 0x4E, Key.O: 0x4F,
    Key.P: 0x50, Key.Q: 0x51, Key.R: 0x52, Key.S: 0x53, Key.T: 0x54,
    Key.U: 0x55, Key.V: 0x56, Key.W: 0x57, Key.X: 0x58, Key.Y: 0x59, Key.Z: 0x5A,

    # Numbers
    Key.DIGIT_0: 0x30, Key.DIGIT_1: 0x31, Key.DIGIT_2: 0x32, Key.DIGIT_3: 0x33,
    Key.DIGIT_4: 0x34, Key.DIGIT_5: 0x35, Key.DIGIT_6: 0x36, Key.DIGIT_7: 0x37,
    Key.DIGIT_8: 0x38, Key.DIGIT_9: 0x39,

    # Function keys
    Key.F1: 0x70, Key.F2: 0x71, Key.F3: 0x72, Key.F4: 0x73, Key.F5: 0x74,
    Key.F6: 0x75, Key.F7: 0x76, Key.F8: 0x77, Key.F9: 0x78, Key.F10: 0x79,
    Key.F11: 0x7A, Key.F12: 0x7B,

    # Control & modifiers
    Key.SHIFT: 0x10,
    Key.CONTROL: 0x11,
    Key.ALT: 0x12,
    Key.CAPS_LOCK: 0x14,
    Key.TAB: 0x09,
    Key.ESCAPE: 0x1B,
    Key.WINDOWS: 0x5B,
    Key.MENU: 0x5D,

    # Navigation / editing
    Key.ENTER: 0x0D,
    Key.BACKSPACE: 0x08,
    Key.SPACE: 0x20,
    Key.INSERT: 0x2D,
    Key.DELETE: 0x2E,
    Key.HOME: 0x24,
    Key.END: 0x23,
    Key.PAGE_UP: 0x21,
    Key.PAGE_DOWN: 0x22,
    Key.UP_ARROW: 0x26,
    Key.DOWN_ARROW: 0x28,
    Key.LEFT_ARROW: 0x25,
    Key.RIGHT_ARROW: 0x27,

    # Symbols & punctuation
    Key.MINUS: 0xBD,
    Key.EQUAL: 0xBB,
    Key.LEFT_BRACKET: 0xDB,
    Key.RIGHT_BRACKET: 0xDD,
    Key.BACKSLASH: 0xDC,
    Key.SEMICOLON: 0xBA,
    Key.QUOTE: 0xDE,
    Key.COMMA: 0xBC,
    Key.PERIOD: 0xBE,
    Key.SLASH: 0xBF,
    Key.BACKQUOTE: 0xC0,

    # Media keys
    Key.NEXT_TRACK: 0xB0,  # VK_MEDIA_NEXT_TRACK
    Key.PREVIOUS_TRACK: 0xB1,  # VK_MEDIA_PREV_TRACK
    Key.STOP: 0xB2,  # VK_MEDIA_STOP
    Key.PLAY_PAUSE: 0xB3,  # VK_MEDIA_PLAY_PAUSE
    Key.MUTE: 0xAD,  # VK_VOLUME_MUTE
    Key.VOLUME_DOWN: 0xAE,  # VK_VOLUME_DOWN
    Key.VOLUME_UP: 0xAF,  # VK_VOLUME_UP
    Key.LAUNCH_MAIL: 0xB4,  # VK_LAUNCH_MAIL
    Key.LAUNCH_MEDIA_PLAYER: 0xB5,  # VK_LAUNCH_MEDIA_SELECT
    Key.LAUNCH_APP1: 0xB6,  # VK_LAUNCH_APP1
    Key.LAUNCH_APP2: 0xB7,  # VK_LAUNCH_APP2
}

WINDOWS_CODES_REVERSE = {v: k for k, v in WINDOWS_CODES.items()}

WINDOWS_MODIFIERS = {
    0x01: Key.SHIFT,
    0x02: Key.CAPS_LOCK,
    0x04: Key.CONTROL,
    0x08: Key.ALT,
    0x10: Key.NUM_LOCK,
    0x80: Key.ALT,
}

BUTTONS = {
    1: Button.LEFT,
    2: Button.MIDDLE,
    3: Button.RIGHT,
    4: Button.FORWARD,
    5: Button.BACK,
}

BUTTONS_REVERSE = {v: k for k, v in BUTTONS.items()}

KEY_TO_HID = {
    # Letters
    Key.A: 0x04,
    Key.B: 0x05,
    Key.C: 0x06,
    Key.D: 0x07,
    Key.E: 0x08,
    Key.F: 0x09,
    Key.G: 0x0A,
    Key.H: 0x0B,
    Key.I: 0x0C,
    Key.J: 0x0D,
    Key.K: 0x0E,
    Key.L: 0x0F,
    Key.M: 0x10,
    Key.N: 0x11,
    Key.O: 0x12,
    Key.P: 0x13,
    Key.Q: 0x14,
    Key.R: 0x15,
    Key.S: 0x16,
    Key.T: 0x17,
    Key.U: 0x18,
    Key.V: 0x19,
    Key.W: 0x1A,
    Key.X: 0x1B,
    Key.Y: 0x1C,
    Key.Z: 0x1D,

    # Numbers (top row)
    Key.DIGIT_1: 0x1E,
    Key.DIGIT_2: 0x1F,
    Key.DIGIT_3: 0x20,
    Key.DIGIT_4: 0x21,
    Key.DIGIT_5: 0x22,
    Key.DIGIT_6: 0x23,
    Key.DIGIT_7: 0x24,
    Key.DIGIT_8: 0x25,
    Key.DIGIT_9: 0x26,
    Key.DIGIT_0: 0x27,

    # Control & modifiers
    Key.ENTER: 0x28,
    Key.ESCAPE: 0x29,
    Key.BACKSPACE: 0x2A,
    Key.TAB: 0x2B,
    Key.SPACE: 0x2C,

    # Symbols
    Key.MINUS: 0x2D,
    Key.EQUAL: 0x2E,
    Key.LEFT_BRACKET: 0x2F,
    Key.RIGHT_BRACKET: 0x30,
    Key.BACKSLASH: 0x31,
    Key.SEMICOLON: 0x33,
    Key.QUOTE: 0x34,
    Key.BACKQUOTE: 0x35,
    Key.COMMA: 0x36,
    Key.PERIOD: 0x37,
    Key.SLASH: 0x38,

    # Lock & system
    Key.CAPS_LOCK: 0x39,
    Key.PRINT_SCREEN: 0x46,
    Key.SCROLL_LOCK: 0x47,
    Key.PAUSE: 0x48,

    # Navigation
    Key.INSERT: 0x49,
    Key.HOME: 0x4A,
    Key.PAGE_UP: 0x4B,
    Key.DELETE: 0x4C,
    Key.END: 0x4D,
    Key.PAGE_DOWN: 0x4E,
    Key.RIGHT_ARROW: 0x4F,
    Key.LEFT_ARROW: 0x50,
    Key.DOWN_ARROW: 0x51,
    Key.UP_ARROW: 0x52,

    # Function keys
    Key.F1: 0x3A,
    Key.F2: 0x3B,
    Key.F3: 0x3C,
    Key.F4: 0x3D,
    Key.F5: 0x3E,
    Key.F6: 0x3F,
    Key.F7: 0x40,
    Key.F8: 0x41,
    Key.F9: 0x42,
    Key.F10: 0x43,
    Key.F11: 0x44,
    Key.F12: 0x45,

    # Numpad
    Key.NUM_LOCK: 0x53,
    Key.NUMPAD_DIVIDE: 0x54,
    Key.NUMPAD_MULTIPLY: 0x55,
    Key.NUMPAD_SUBTRACT: 0x56,
    Key.NUMPAD_ADD: 0x57,
    Key.NUMPAD_ENTER: 0x58,
    Key.NUMPAD_1: 0x59,
    Key.NUMPAD_2: 0x5A,
    Key.NUMPAD_3: 0x5B,
    Key.NUMPAD_4: 0x5C,
    Key.NUMPAD_5: 0x5D,
    Key.NUMPAD_6: 0x5E,
    Key.NUMPAD_7: 0x5F,
    Key.NUMPAD_8: 0x60,
    Key.NUMPAD_9: 0x61,
    Key.NUMPAD_0: 0x62,
    Key.NUMPAD_DECIMAL: 0x63,

    # Modifier keys (special: usually sent as modifier bits)
    Key.CONTROL: 0xE0,
    Key.LEFT_CONTROL: 0xE0,
    Key.SHIFT: 0xE1,
    Key.LEFT_SHIFT: 0xE1,
    Key.ALT: 0xE2,
    Key.LEFT_ALT: 0xE2,
    Key.WINDOWS: 0xE3,
    Key.RIGHT_CONTROL: 0xE4,
    Key.RIGHT_SHIFT: 0xE5,
    Key.RIGHT_ALT: 0xE6,
    Key.MENU: 0x65,

    # Media keys (Consumer page, NOT keyboard page)
    Key.PLAY_PAUSE: 0xCD,
    Key.STOP: 0xB7,
    Key.NEXT_TRACK: 0xB5,
    Key.PREVIOUS_TRACK: 0xB6,
    Key.MUTE: 0xE2,
    Key.VOLUME_UP: 0xE9,
    Key.VOLUME_DOWN: 0xEA,
    Key.MEDIA_SELECT: 0x183,
    Key.LAUNCH_MAIL: 0x18A,
    Key.LAUNCH_MEDIA_PLAYER: 0x192,
    Key.LAUNCH_APP1: 0x194,
    Key.LAUNCH_APP2: 0x196,
}

KEY_MODIFIER_HID_MASK = {
    Key.LEFT_CONTROL: 1,
    Key.LEFT_SHIFT: 1 << 1,
    Key.LEFT_ALT: 1 << 2,
    Key.WINDOWS: 1 << 3,
    Key.RIGHT_CONTROL: 1 << 4,
    Key.RIGHT_SHIFT: 1 << 5,
    Key.RIGHT_ALT: 1 << 6,
}


def get_hid_usage(key: Key) -> int:
    return KEY_TO_HID.get(key)


def is_modifier(key: Key) -> bool:
    return key in KEY_MODIFIER_HID_MASK


def create_key_mask(modifiers: Iterable[Key]) -> int:
    mask = 0
    for modifier in modifiers:
        bit = KEY_MODIFIER_HID_MASK.get(modifier)
        if bit is not None:
            mask |= bit
    return mask


def create_button_mask(buttons: Iterable[Button]) -> int:
    mask = 0
    for button in buttons:
        bit = BUTTONS_REVERSE.get(button)
        if bit is not None:
            mask |= bit
    return mask


def get_key(keycode: int, keysym: str) -> Key:
    if keysym in KEYSYM_MAP:
        return KEYSYM_MAP[keysym]
    return WINDOWS_CODES_REVERSE.get(keycode)


def get_button(number: int) -> Button:
    return BUTTONS[number]


# Source - https://stackoverflow.com/a
# Posted by Zero Piraeus, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-09, License - CC BY-SA 4.0

PUBLIC_ENUMS = {
    'Key': Key,
    'Button': Button,
}


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d
