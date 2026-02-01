import binascii

from keymaps import is_modifier, get_hid_usage, create_key_mask, create_button_mask

VERSION = 1


class IVHPackage:
    _delay_size_map = {1: 0b00, 2: 0b01, 4: 0b10, 8: 0b11}

    def __init__(self, package: list):
        self._bytes = bytearray()
        self._bytes.extend(b'IVH\x99')
        self._bytes.extend([VERSION, 0])
        payload = self._generate(package)
        self._bytes.extend(len(payload).to_bytes(4, byteorder='little'))
        self._bytes.extend(payload)
        crc = binascii.crc32(self._bytes, 0)
        self._bytes.extend(crc.to_bytes(4, byteorder='little'))

    def as_bytes(self):
        return self._bytes

    def _generate(self, package: list) -> bytearray:
        output = bytearray()
        for command in package:
            emitter = getattr(self, f"_emit_{command['type'].lower()}")
            output.extend(emitter(command))
        return output

    def _emit_keyhold(self, data: dict, key_base: int = 0x04) -> bytes:
        all_keys = set(data.get("keys", []))
        if not all_keys:
            return b''

        mod = {k for k in all_keys if is_modifier(k)}
        keys = list(all_keys - mod)
        if not keys and mod:
            # insert placeholder key so modifiers can be sent
            keys.append(0)

        if len(keys) == 1 and not mod:
            return key_base.to_bytes(1) + get_hid_usage(keys[0]).to_bytes(1)

        if len(keys) == 1 and mod:
            return b''.join([
                (key_base + 1).to_bytes(1),
                get_hid_usage(keys[0]).to_bytes(1),
                create_key_mask(mod).to_bytes(1)
            ])

        return b''.join([
            (key_base + 2).to_bytes(1),
            len(keys).to_bytes(1),
            create_key_mask(mod).to_bytes(1),
            *[get_hid_usage(k).to_bytes(1) for k in keys]
        ])

    def _emit_keypress(self, data: dict) -> bytes:
        return self._emit_keyhold(data, key_base=0x0C)

    def _emit_keyrelease(self, data: dict) -> bytes:
        all_keys = set(data.get("keys", []))
        if not all_keys:
            return b'\x0B'
        return self._emit_keyhold(data, key_base=0x08)

    def _emit_buttonhold(self, data: dict, key_base=0x10) -> bytes:
        buttons = data.get("keys", [])
        if not buttons:
            return b''
        return key_base.to_bytes(1) + create_button_mask(buttons).to_bytes(1)

    def _emit_buttonrelease(self, data: dict) -> bytes:
        buttons = data.get("keys", [])
        if not buttons:
            return b'\x13'
        return self._emit_buttonhold(data, key_base=0x11)

    def _emit_buttonpress(self, data: dict) -> bytes:
        return self._emit_buttonhold(data, key_base=0x12)

    def _emit_mousewheel(self, data: dict) -> bytes:
        dx = data.get("delta_x", 0)
        dy = data.get("delta_y", 0)

        if dx == 0 and dy == 0:
            return b''
        if dy == 0:
            return b'\x20' + dx.to_bytes(1, signed=True)
        if dx == 0:
            return b'\x21' + dy.to_bytes(1, signed=True)

        return b'\x24' + dx.to_bytes(1, signed=True) + dx.to_bytes(1, signed=True)

    def _emit_mousemove(self, data: dict) -> bytes:
        dx = data.get("delta_x", 0)
        dy = data.get("delta_y", 0)

        if dx == 0 and dy == 0:
            return b''
        if dy == 0:
            return b'\x22' + dx.to_bytes(1, signed=True)
        if dx == 0:
            return b'\x23' + dy.to_bytes(1, signed=True)

        return b'\x25' + dx.to_bytes(1, signed=True) + dx.to_bytes(1, signed=True)

    def _bytes_required(self, n: int, max_bytes: int = 8) -> int:
        if n < 0:
            raise ValueError("Only non-negative integers are supported")
        return min(max_bytes, max(1, (n.bit_length() + 7) // 8))

    def _bytes_required_pow2(self, n: int) -> int:
        if n < 0:
            raise ValueError("Only non-negative integers are supported")

        bits = max(1, n.bit_length())

        if bits <= 8:
            return 1
        elif bits <= 16:
            return 2
        elif bits <= 32:
            return 4
        else:
            return 8

    def _emit_delay(self, data: dict) -> bytes:
        dur = data.get("duration", 0)
        if dur == 0:
            return b''
        byte_len = self._bytes_required(dur)
        return b''.join([
            (0x30 | (byte_len-1)).to_bytes(1),
            dur.to_bytes(byte_len, byteorder='little'),
        ])

    def _emit_delayrandom(self, data: dict) -> bytes:
        start = data.get("start", 0)
        stop = data.get("stop", 0)
        if start >= stop:
            raise ValueError("Start should be greater than Stop")
        start_byte_len = self._bytes_required_pow2(start)
        stop_byte_len = self._bytes_required_pow2(stop)
        return b''.join([
            (0x40 | self._delay_size_map[start_byte_len] | (self._delay_size_map[stop_byte_len] << 2)).to_bytes(1),
            start.to_bytes(start_byte_len, byteorder='little'),
            stop.to_bytes(stop_byte_len, byteorder='little'),
        ])

    def _emit_loop(self, data: dict) -> bytearray:
        nodes = data.get('nodes', [])
        if not nodes:
            return b''

        body = self._generate(nodes)
        if not body:
            return b''
        output = bytearray([0xE0])
        output.extend(body)
        # append block end
        output.extend([0xEF])
        return output

    def _emit_loopfor(self, data: dict) -> bytearray:
        count = data.get("count", 0)
        nodes = data.get('nodes', [])
        if not count or not nodes:
            return b''

        body = self._generate(nodes)
        if not body:
            return b''
        output = bytearray([0xE1])
        output.extend(count.to_bytes(2, byteorder='little'))
        output.extend(body)
        # append block end
        output.extend([0xEF])
        return output

    def _emit_loopforrandom(self, data: dict) -> bytearray:
        start = data.get("start", 0)
        stop = data.get("stop", 0)
        if start >= stop:
            raise ValueError("Start should be greater than Stop")
        nodes = data.get('nodes', [])
        if not nodes:
            return b''

        body = self._generate(nodes)
        if not body:
            return b''
        output = bytearray([0xE2])
        output.extend(start.to_bytes(2, byteorder='little'))
        output.extend(stop.to_bytes(2, byteorder='little'))
        output.extend(body)
        # append block end
        output.extend([0xEF])
        return output

    def _emit_break(self, _) -> bytes:
        return b'\xEE'

    def _emit_randomize(self, data: dict) -> bytes:
        nodes = data.get('nodes', [])
        if not nodes:
            return b''

        body = self._generate(nodes)
        if not body:
            return b''
        output = bytearray([0xE3])
        output.extend(body)
        # append block end
        output.extend([0xEF])
        return output
