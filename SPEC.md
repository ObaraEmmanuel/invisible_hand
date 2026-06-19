# Package Format Specification

## 1. Overview

Each package begins with a **magic header** and version identifier, followed by one or more command entries, and ends with a CRC checksum.

```

[Magic: "IVH\x99"][Version:8][Reserved:8]
[Len: 32]
[KEY_1:8][PARAM_1][PARAM_2]...[PARAM_N]
[KEY_2:8][PARAM_1][PARAM_2]...[PARAM_N]
...
[KEY_N:8][PARAM_1][PARAM_2]...[PARAM_N]
[CRC:32]

```

- **Magic (`IVH\x99`)** – 4-byte format identifier marking the start of a valid package.
- **Version (8-bit)** – Protocol version identifier for compatibility control.
- **Reserved (8-bit)** – Reserved 8 bit section. Should always be set to 0.
- **Len (32-bit)** – Length of the commands data (excluding CRC) in bytes.
- **CRC** – Checksum verifying integrity of the entire message using CRC-32.
- **Encoding** – All multibyte parameters are encoded in **little-endian** format.

---

## 2. Command Key Reference

|     Key     | Name                 | Parameters                                 | Description                                                                                                                                                                                                                 |
|:-----------:|----------------------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|    0x00     | Reserved             |                                            | Reserved                                                                                                                                                                                                                    |
|    0x04     | **KeyHold**          | `Key:8`,                                   | Holds a key down a key.                                                                                                                                                                                                     |
|    0x05     | **KeyHold**          | `Key:8`, `Modifier:8`                      | Holds a key down with modifiers.                                                                                                                                                                                            |
|    0x06     | **KeyHold**          | `Len:8`, `Modifier:8`, `Key0:8`...`KeyN:8` | Holds down upto 256 keys at once with modifiers. The number of keys is specified by `Len`. If N-KRO is not supported, only the first 6 keys will registered.                                                                |
|    0x08     | **KeyRelease**       | `Key:8`                                    | Releases one key                                                                                                                                                                                                            |
|    0x09     | **KeyRelease**       | `Key:8`, `Modifier:8`                      | Releases a key with modifiers                                                                                                                                                                                               |
|    0x0A     | **KeyRelease**       | `Len:8`, `Modifier:8`, `Key0:8`...`KeyN:8` | Releases upto 256 keys at once with modifiers. The number of keys is specified by `Len`. Keys not currently pressed will be ignored                                                                                         |
|    0x0B     | **KeyReleaseAll**    | *None*                                     | Releases all keys that have been pressed.                                                                                                                                                                                   |
|    0x0C     | **KeyPress**         | `Key:8`,                                   | Simulates a keypress. it performs a keyhold, delay and keyrelease.                                                                                                                                                          |
|    0x0D     | **KeyPress**         | `Key:8`, `Modifier:8`                      | Simulates a keypress with modifiers.                                                                                                                                                                                        |
|    0x0E     | **KeyPress**         | `Len:8`, `Modifier:8`, `Key0:8`...`KeyN:8` | Simulates pressing upto 256 keys at once with modifiers. The number of keys is specified by `Len`. If N-KRO is not supported, only the first 6 keys will registered.                                                        |
|    0x10     | **ButtonHold**       | `ButtonMask:8`                             | Holds down a mouse button for drag or selection actions.                                                                                                                                                                    |
|    0x11     | **ButtonRelease**    | `ButtonMask:8`                             | Releases any number of buttons if they have been pressed or held. If `Len` is 0, all buttons are released                                                                                                                   |
|    0x12     | **ButtonPress**      | `ButtonMask:8`                             | Performs a mouse click on the specified buttons (left, right, middle).                                                                                                                                                      |
|    0x13     | **ButtonReleaseAll** | *None*                                     | Releases all buttons that have been pressed.                                                                                                                                                                                |
|    0x20     | **MouseWheelX**      | `Dx:8`                                     | Scrolls the mouse wheel horizontally by `Dx` units. `Dx` is a signed twos complement value ranging from -127 to 127.                                                                                                        |
|    0x21     | **MouseWheelY**      | `Dy:8`                                     | Scrolls the mouse wheel vertically by `Dy` units. `Dy` is a signed twos complement value ranging from -127 to 127.                                                                                                          |
|    0x22     | **MouseMoveX**       | `Dx:8`                                     | Moves the mouse pointer horizontally by `Dx` units. `Dx` is a signed twos complement value ranging from -127 to 127.                                                                                                        |
|    0x23     | **MouseMoveY**       | `Dy:8`                                     | Moves the mouse pointer vertically by `Dy` units. `Dy` is a signed twos complement value ranging from -127 to 127.                                                                                                          |
|    0x24     | **MouseWheel**       | `Dx:8`, `Dy:8`                             | Scrolls the mouse wheel horizontally by `Dx` units and vertically by `Dy` units. `Dx` and `Dy` are signed twos complement values -127 to 127.                                                                               |
|    0x25     | **MouseMove**        | `Dx:8`, `Dy:8`                             | Moves the mouse pointer horizontally by `Dx` units and vertically by `Dy` units. `Dx` and `Dy` are signed twos complement values -127 to 127.                                                                               |
| 0x30 - 0x37 | **Delay**            | `Dur:8-64`                                 | Specify delay in microseconds. The size of the parameter is determined by the last three bits of the key. See `More on Delays`.                                                                                             |
| 0x40 - 0x4F | **DelayRandom**      | `Start:8-64`, `Stop:8-64`                  | Delay for a random duration (microseconds) within the specified closed range `[Start, Stop]`. Useful for human-like timing. The size of the parameter is determined by the last three bits of the key.See `More on Delays`. |
|    0xE0     | **Loop**             | *None*                                     | Marks the beginning of a repeatable sequence of commands until an `EndLoop`.                                                                                                                                                |
|    0xE1     | **LoopFor**          | `Count:16`                                 | Starts a loop that repeats the enclosed command block exactly `Count` times.                                                                                                                                                |
|    0xE2     | **LoopForRandom**    | `Start:16`, `Stop:16`                      | Starts a loop that repeats the enclosed command block exactly `Count` times.                                                                                                                                                |
|    0xE3     | **Randomize**        | *None*                                     | Randomly selects one of the enclosed commands at runtime.                                                                                                                                                                   |
|    0xEE     | **Break**            | *None*                                     | Breaks out of a loop command like `Loop` or `LoopFor`.                                                                                                                                                                      |
|    0xEF     | **End**              | *None*                                     | Marks the end of a sequence initiated by a block command like `Randomize`, `Loop` or `LoopFor`.                                                                                                                             |

---

## 3. More on Delays
### Delay / DelayRandom Size Encoding

The **lower bits** of the opcode encode the **parameter size(s)**. All delay values are interpreted as **microseconds** and encoded in **little-endian**.

---

### Delay (`0x30 – 0x37`)

**Single parameter:** `Dur`
The **lower 3 bits** select the size of `Dur`, allowing **8 distinct sizes**.

| Key  | Size selector (bbb) | Dur size (bits) | Dur size (bytes) |
|------|---------------------|-----------------|------------------|
| 0x30 | 000                 | 8               | 1                |
| 0x31 | 001                 | 16              | 2                |
| 0x32 | 010                 | 24              | 3                |
| 0x33 | 011                 | 32              | 4                |
| 0x34 | 100                 | 40              | 5                |
| 0x35 | 101                 | 48              | 6                |
| 0x36 | 110                 | 56              | 7                |
| 0x37 | 111                 | 64              | 8                |

**Layout**

```
[KEY][Dur:N]
```

---

## DelayRandom (`0x40 – 0x4F`)

**Two parameters:** `Start`, `Stop`
The **lower 4 bits** are split into two independent size selectors:

* **Bits 0–1** → size of `Start`
* **Bits 2–3** → size of `Stop`

Each selector provides **4 possible sizes**.

### Size Code Mapping

| Code | Size (bits) | Size (bytes) |
|------|-------------|--------------|
| 00   | 8           | 1            |
| 01   | 16          | 2            |
| 10   | 32          | 4            |
| 11   | 64          | 8            |

### Size Encoding

```
Key = 0x4F
      └─┬─┘
        │
        ├─ bits 0–1: Start size code
        └─ bits 2–3: Stop size code
```

| Key  | Start size (bits 3–2) | Stop size (bits 1–0) |
|------|-----------------------|----------------------|
| 0x40 | 00                    | 00                   |
| 0x44 | 01                    | 00                   |
| 0x45 | 01                    | 01                   |
| 0x48 | 10                    | 00                   |
| 0x49 | 10                    | 01                   |
| 0x4A | 10                    | 10                   |
| 0x4C | 11                    | 00                   |
| 0x4D | 11                    | 01                   |
| 0x4E | 11                    | 10                   |
| 0x4F | 11                    | 11                   |

**Layout**

```
[KEY][Start:N][Stop:M]
```

---

### Notes

* `Start ≤ Stop` is required, so 0x41, 0x42, 0x43, 0x46, 0x47, 0x4B are not valid delay random keys. These should be ignored as they can be repurposed for future commands.
* Independent size selection allows **4 sizes per parameter**


## 3. Notes

- **Little-Endian Encoding** – All multibyte integers e.g. `Dur:64`, `Start:64`, `Stop:64`, `Count:16` use little-endian order.
- **Units** – Durations are expressed in microseconds unless otherwise specified.
- **CRC Coverage** – The CRC must include all bytes from `[Magic]` through the last parameter before the CRC itself.
- **Loop Behavior** – Nested loops are allowed if supported by the interpreter; `LoopFor` provides deterministic repetition.
- **Safety** – Always follow `KeyHold` or `MouseClickHold` with the appropriate release command to prevent stuck input states.
- **Unassigned keys** - Encountering any unsupported keys should stop execution immediately.

---

## 4. Example Sequence

**Example:** Type “A”, wait randomly between 100–250 ms, then release.

```

[Magic: "IVH\x99"][Version:1]
[0x01][0x04][0x00]     ; KeyPress ‘A’ (no modifier)
[0x31][100][250]       ; DelayRandom 100–250 ms (little endian)
[0x03][0x01][0x04]     ; KeyRelease ‘A’
[CRC-32]

```
