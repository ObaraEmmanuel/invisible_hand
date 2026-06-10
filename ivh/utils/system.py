def unsigned_to_bytes(n: int, max_bytes: int = 8) -> bytes:
    if n < 0:
        raise ValueError("Only non-negative integers are allowed")
    byte_count = max(1, (n.bit_length() + 7) // 8)
    if byte_count > max_bytes:
        raise ValueError(f"Integer too large to fit within {max_bytes} bytes")
    return n.to_bytes(byte_count, byteorder="little")
