#!/usr/bin/env python3
# Generate C style array from blob
import argparse
from pathlib import Path


def to_c_byte_string(data: bytes, cols: int = 16) -> str:
    # C string literal with \xHH escapes (safe for any binary)
    parts = []
    for i, b in enumerate(data):
        if i % cols == 0:
            parts.append('"')
        parts.append(f'\\x{b:02x}')
        if i % cols == cols - 1:
            parts.append('"\n')
    if data and (len(data) % cols) != 0:
        parts.append('"\n')
    return ''.join(parts) if data else '""\n'


def main():
    ap = argparse.ArgumentParser(description="Read a binary file and output a C string literal of its contents.")
    ap.add_argument("input", type=Path, help="Input binary file")
    ap.add_argument("-n", "--name", default="blob", help="C variable name (default: blob)")
    ap.add_argument("-c", "--cols", type=int, default=16, help="Bytes per line (default: 16)")
    ap.add_argument("--static", action="store_true", help="Emit as static const")
    args = ap.parse_args()

    data = args.input.read_bytes()
    cstr = to_c_byte_string(data, cols=max(1, args.cols))

    storage = "static const" if args.static else "const"
    out = [
        f"// Generated from: {args.input.name}\n",
        f"{storage} unsigned char {args.name}[{len(data) + 1}] =\n",
        cstr.rstrip('\n'),
        "",
        ";\n"
    ]

    print(''.join(out), end="")


if __name__ == "__main__":
    main()
