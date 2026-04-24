# keyexchange import wrapper

This package hides all `ctypes` details behind a normal Python import.

```python
from keyexchange import KeyExchange
```

## Install

From this folder:

```powershell
pip install .
```

## Example

```python
from keyexchange import KeyExchange, KeyExchangeError

tx_queue = []
rx_queue = []

P256_G_PUBLIC_KEY = bytes.fromhex(
    "6b17d1f2e12c4247f8bce6e563a440f2"
    "77037d812deb33a0f4a13945d898c296"
    "4fe342e2fe1a7f9b8ee7eb4a7c0f9e16"
    "2bce33576b315ececbb6406837bf51f5"
)
P256_PRIVATE_KEY_ONE = bytes.fromhex("00" * 31 + "01")
FACTORY_PRIVATE_KEY_BLOB = P256_G_PUBLIC_KEY + P256_PRIVATE_KEY_ONE

def mock_response_for(request: bytes) -> bytes | None:
    sid = request[0]
    if request == b"\x10\x01":
        return b"\x50\x01"
    if request == b"\x10\x03":
        return b"\x50\x03"
    if request == b"\x27\x65":
        return b"\x67\x65" + bytes.fromhex("01 02 03 04 05 06 07 08")
    if sid == 0x27 and len(request) >= 2 and request[1] == 0x66:
        return b"\x67\x66"
    if sid == 0x31 and request[:4] == b"\x31\x01\xfb\x40":
        return b"\x71\x01\xfb\x40" + P256_G_PUBLIC_KEY
    if sid == 0x31 and request[:4] == b"\x31\x01\xfb\x41":
        return b"\x71\x01\xfb\x41"
    return None

def send_can(data: bytes) -> int:
    print("TX:", data.hex(" "))
    tx_queue.append(data)
    response = mock_response_for(data)
    if response is not None:
        rx_queue.append(response)
    return len(data)

def recv_can(max_len: int) -> bytes:
    if not rx_queue:
        return b""
    data = rx_queue.pop(0)
    print("RX:", data.hex(" "))
    return data[:max_len]

try:
    with KeyExchange(anchor_idx=0) as kex:
        kex.set_callbacks(send_can, recv_can)
        kex.set_factory_private_key(FACTORY_PRIVATE_KEY_BLOB)
        kex.set_secoc_key(bytes.fromhex("11" * 16))
        kex.set_iv(bytes.fromhex("22" * 16))

        kex.start()

        while not kex.is_complete and not kex.is_failed:
            ret = kex.step()
            print("STEP:", ret.name)

        if kex.is_failed:
            raise RuntimeError(kex.last_error)

        print("Key exchange complete")
        print("Encrypted key:", kex.encrypted_key.hex(" "))

except KeyExchangeError as exc:
    raise RuntimeError(str(exc)) from exc
```
