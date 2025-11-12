# Package Format Specification

## 1. Overview

Each package begins with a **magic header** and version identifier, followed by one or more command entries, and ends with a CRC checksum.

```

[Magic: "INVHND"][Version:8]
[KEY_1:8][PARAM_1][PARAM_2]...[PARAM_N]
[KEY_2:8][PARAM_1][PARAM_2]...[PARAM_N]
...
[KEY_N:8][PARAM_1][PARAM_2]...[PARAM_N]
[CRC]

```

- **Magic (`INVHND`)** – 6-byte ASCII identifier marking the start of a valid package.
- **Version (8-bit)** – Protocol version identifier for compatibility control.
- **CRC** – Checksum verifying integrity of the entire message.
- **Encoding** – All multi-byte parameters are encoded in **little-endian** format.

---

## 2. Command Key Reference

| Key  | Name               | Parameters               | Description                                                                                         |
|:----:|--------------------|--------------------------|-----------------------------------------------------------------------------------------------------|
| 0x01 | **KeyPress**       | `Key:8`, `Modifier:8`    | Simulates a keyboard key press event with optional modifier (e.g. Ctrl, Alt, Shift).                |
| 0x02 | **KeyHold**        | `Key:8`, `Modifier:8`    | Holds a key down with an optional modifier for continuous input or shortcut combos.                 |
| 0x03 | **KeyRelease**     | `Key:8`                  | Releases a single key that was previously pressed or held.                                          |
| 0x04 | **KeyReleaseAll**  | *None*                   | Releases all keys currently held down to reset keyboard state.                                      |
| 0x05 | **MouseClick**     | `Button:8`, `Modifier:8` | Performs a mouse click on the specified button (left, right, middle) with optional modifiers.       |
| 0x06 | **MouseClickHold** | `Button:8`, `Modifier:8` | Holds down a mouse button for drag or selection actions.                                            |
| 0x07 | **MouseWheel**     | `Dir:8`, `Delta:64`      | Scrolls the mouse wheel in the given direction (`Dir`) by `Delta` units.                            |
| 0x08 | **Wait**           | `Dur:64`                 | Pauses execution for a specified duration (typically in milliseconds).                              |
| 0x09 | **WaitRandom**     | `From:64`, `To:64`       | Waits for a random duration within the specified range (`From`–`To`). Useful for human-like timing. |
| 0x0A | **Loop**           | *None*                   | Marks the beginning of a repeatable sequence of commands until an `EndLoop`.                        |
| 0x0B | **LoopFor**        | `Count:32`               | Starts a loop that repeats the enclosed command block exactly `Count` times.                        |
| 0x0C | **EndLoop**        | *None*                   | Marks the end of a loop sequence initiated by `Loop` or `LoopFor`.                                  |

---

## 3. Notes

- **Little-Endian Encoding** – All multi-byte integers (`Dur:64`, `Delta:64`, `From:64`, `To:64`, `Count:32`) use little-endian order.
- **Units** – Durations are expressed in milliseconds unless otherwise specified.
- **CRC Coverage** – The CRC must include all bytes from `[Magic]` through the last parameter before the CRC itself.
- **Loop Behavior** – Nested loops are allowed if supported by the interpreter; `LoopFor` provides deterministic repetition.
- **Safety** – Always follow `KeyHold` or `MouseClickHold` with the appropriate release command to prevent stuck input states.

---

## 4. Example Sequence

**Example:** Type “A”, wait randomly between 100–250 ms, then release.

```

[Magic: "INVHND"][Version:1]
[0x01][0x04][0x00]     ; KeyPress ‘A’ (no modifier)
[0x09][100][250]       ; WaitRandom 100–250 ms (little endian)
[0x03][0x04]           ; KeyRelease ‘A’
[CRC]

```
