from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "python"))

from keyexchange_ctypes import KeyExchangeDLL

dll = ROOT / "build" / "libkey_exchange_library.dll"

tx_queue = []
rx_queue = []

def send_can(data_ptr, length):
    data = bytes(data_ptr[i] for i in range(length))
    print("TX:", data.hex(" "))
    tx_queue.append(data)
    return length  # return negative on send failure

def recv_can(buffer, max_len):
    if not rx_queue:
        return 0  # no response yet

    data = rx_queue.pop(0)
    n = min(len(data), max_len)
    for i in range(n):
        buffer[i] = data[i]
    return n  # return negative on receive failure

with KeyExchangeDLL(dll, anchor_idx=0) as kex:
    kex.set_callbacks(send_can, recv_can)

    # Required before start()
    kex.set_factory_private_key(bytes.fromhex("00" * 32))  # replace with real private key
    kex.set_secoc_key(bytes.fromhex("11" * 16))            # must be multiple of 16 bytes
    kex.set_iv(bytes.fromhex("22" * 16))                   # must be exactly 16 bytes

    ret = kex.start()
    if ret != 0:
        raise RuntimeError(kex.last_error())

    while not kex.is_complete() and not kex.is_failed():
        ret = kex.step()

        # ret meanings:
        #  0  OK
        #  1  pending / waiting for response
        #  2  complete
        # -1  failed
        # -2  bad argument
        # -3  not configured
        # -4  CAN callback missing

        if ret < 0:
            raise RuntimeError(kex.last_error())

    if kex.is_failed():
        raise RuntimeError(kex.last_error())

    print("Key exchange complete")
