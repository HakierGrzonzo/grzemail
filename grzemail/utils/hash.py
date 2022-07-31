from typing import Tuple
from hashlib import sha256


def static_hash(*strings: Tuple[str]) -> int:
    big_string = "".join(strings)
    raw_bytes = big_string.encode()
    return int.from_bytes(sha256(raw_bytes).digest()[:4], "little")
