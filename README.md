# Package Format Specification

## 1. Overview

Each package begins with a **magic header** and version identifier, followed by one or more command entries, and ends with a CRC checksum.

```

[Magic: "IVH\x99"][Version:8][Reserved:8]
[KEY_1:8][PARAM_1][PARAM_2]...[PARAM_N]
[KEY_2:8][PARAM_1][PARAM_2]...[PARAM_N]
...
[KEY_N:8][PARAM_1][PARAM_2]...[PARAM_N]
[CRC:32]

```

- **Magic (`IVH\x99`)** – 4-byte format identifier marking the start of a valid package.
- **Version (8-bit)** – Protocol version identifier for compatibility control.
- **Reserved (8-bit)** – Reserved 8 bit section. Should always be set to 0.
- **CRC** – Checksum verifying integrity of the entire message using CRC-32
- **Encoding** – All multibyte parameters are encoded in **little-endian** format.

---

## 2. Command Key Reference

| Key  | Name                 | Parameters                   | Description                                                                                                                      |
|:----:|----------------------|------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 0x00 | **KeyPress**         | `Key:8`, `Modifier:8`        | Simulates a keyboard key press event with optional modifier (e.g. Ctrl, Alt, Shift).                                             |
| 0x01 | **KeyPress**         | `Key:8`                      | Simulates a keyboard key press event.                                                                                            |
| 0x02 | **KeyHold**          | `Key:8`, `Modifier:8`        | Holds a key down with an optional modifier for continuous input or shortcut combos.                                              |
| 0x03 | **KeyHold**          | `Key:8`                      | Holds a key down.                                                                                                                |
| 0x04 | **KeyRelease**       | `Len:8`, `Key0:8`...`KeyN:8` | Releases any number of keys if they have been pressed or held. If `Len` is 0, all keys are released                              |
| 0x05 | **KeyReleaseAll**    | *None*                       | Releases all keys that have been pressed.                                                                                        |
| 0x10 | **ButtonPress**      | `ButtonMask:8`               | Performs a mouse click on the specified buttons (left, right, middle).                                                           |
| 0x11 | **ButtonHold**       | `ButtonMask:8`               | Holds down a mouse button for drag or selection actions.                                                                         |
| 0x12 | **ButtonRelease**    | `ButtonMask:8`               | Releases any number of buttons if they have been pressed or held. If `Len` is 0, all buttons are released                        |
| 0x13 | **ButtonReleaseAll** | *None*                       | Releases all buttons that have been pressed.                                                                                     |
| 0x20 | **MouseWheelX**      | `Dx:8`                       | Scrolls the mouse wheel horizontally by `Dx` units. `Dx` is a signed twos complement value.                                      |
| 0x21 | **MouseWheelY**      | `Dy:8`                       | Scrolls the mouse wheel vertically by `Dy` units. `Dy` is a signed twos complement value.                                        |
| 0x22 | **MouseMoveX**       | `Dx:8`                       | Moves the mouse pointer horizontally by `Dx` units. `Dx` is a signed twos complement value.                                      |
| 0x23 | **MouseMoveY**       | `Dy:8`                       | Moves the mouse pointer vertically by `Dy` units. `Dy` is a signed twos complement value.                                        |
| 0x24 | **MouseWheel**       | `Dx:8`, `Dy:8`               | Scrolls the mouse wheel horizontally by `Dx` units and vertically by `Dy` units. `Dx` and `Dy` are signed twos complement values |
| 0x25 | **MouseMove**        | `Dx:8`, `Dy:8`               | Moves the mouse pointer horizontally by `Dx` units and vertically by `Dy` units. `Dx` and `Dy` are signed twos complement values |
| 0x30 | **Delay**            | `Dur:64`                     | Delays execution for a specified duration (typically in milliseconds).                                                           |
| 0x31 | **DelayRandom**      | `From:64`, `To:64`           | Waits for a random duration within the specified range (`From`–`To`). Useful for human-like timing.                              |
| 0x40 | **Loop**             | *None*                       | Marks the beginning of a repeatable sequence of commands until an `EndLoop`.                                                     |
| 0x41 | **LoopFor**          | `Count:16`                   | Starts a loop that repeats the enclosed command block exactly `Count` times.                                                     |
| 0x42 | **LoopForRandom**    | `From:16`, `To:16`           | Starts a loop that repeats the enclosed command block exactly `Count` times.                                                     |
| 0x43 | **Randomize**        | *None*                       | Randomly selects one of the enclosed commands at runtime.                                                                        |
| 0x4E | **Break**            | *None*                       | Breaks out of a loop command like `Loop` or `LoopFor`.                                                                           |
| 0x4F | **End**              | *None*                       | Marks the end of a sequence initiated by a block command like `Randomize`, `Loop` or `LoopFor`.                                  |

---

## 3. Notes

- **Little-Endian Encoding** – All multibyte integers (`Dur:64`, `Delta:64`, `From:64`, `To:64`, `Count:32`) use little-endian order.
- **Units** – Durations are expressed in milliseconds unless otherwise specified.
- **CRC Coverage** – The CRC must include all bytes from `[Magic]` through the last parameter before the CRC itself.
- **Loop Behavior** – Nested loops are allowed if supported by the interpreter; `LoopFor` provides deterministic repetition.
- **Safety** – Always follow `KeyHold` or `MouseClickHold` with the appropriate release command to prevent stuck input states.

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
