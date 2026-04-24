#!/usr/bin/env python3
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

import can
from keyexchange import KeyExchange, KeyExchangeError, TickResult

# ============================================================================
# User-provided wake-up / network configuration
# ============================================================================
CAN_CHANNEL = 0
INTERFACE = "vector"
APP_NAME = None

# CAN FD / bit timing
BITRATE = 500_000
DATA_BITRATE = 2_000_000
SJW_ABR = 16
TSEG1_ABR = 63
TSEG2_ABR = 16
SAM_ABR = 1
SJW_DBR = 8
TSEG1_DBR = 31
TSEG2_DBR = 8

# Unlock / UDS over ISO-TP
UNLOCK_RXID = 0x728  # frames received from anchor
UNLOCK_TXID = 0x708  # frames sent to anchor
CANTP_PADDING = 0x55
UDS_POLL_SLICE_S = 0.01
KEX_TIMEOUT_S = 30.0

# Wake-up / Network management
CAN_NM_MSG_ID = 0x14003800
CAN_NM_MSG_DATA = bytes([0x01, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
CAN_NM_PERIOD_S = 0.1
WAKEUP_LEAD_TIME_S = 0.3

# Security material: replace with your real values
FACTORY_PRIVATE_KEY_BLOB = bytes([
    0xE4, 0xC3, 0x2B, 0x6A, 0x84, 0xBC, 0x24, 0x3A,
    0xDF, 0xFC, 0xDA, 0x64, 0xF3, 0xBF, 0x44, 0x96,
    0x97, 0xAD, 0xC6, 0x52, 0x90, 0x73, 0x54, 0x4A,
    0xD1, 0x78, 0xF8, 0x9B, 0x8D, 0xFB, 0xA6, 0x57,
])
SECOC_KEY = bytes([
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16,
    0x17, 0x18, 0x19, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x30, 0x31, 0x32,
    0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
    0x49, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x60, 0x61, 0x62, 0x63, 0x64,
    0x65, 0x66, 0x67, 0x68, 0x69, 0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x80,
    0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96,
])
IV = bytes([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])
ANCHOR_IDX = 0
NO_RESPONSE_LIMIT = 1000
VERBOSE = True


@dataclass
class BusConfig:
    interface: str = INTERFACE
    channel: int | str = CAN_CHANNEL
    receive_own_messages: bool = False
    fd: bool = True
    bitrate: int = BITRATE
    data_bitrate: int = DATA_BITRATE
    sjw_abr: int = SJW_ABR
    tseg1_abr: int = TSEG1_ABR
    tseg2_abr: int = TSEG2_ABR
    sam_abr: int = SAM_ABR
    sjw_dbr: int = SJW_DBR
    tseg1_dbr: int = TSEG1_DBR
    tseg2_dbr: int = TSEG2_DBR
    app_name: Optional[str] = APP_NAME

    def create_bus(self) -> can.BusABC:
        return can.Bus(
            interface=self.interface,
            channel=self.channel,
            receive_own_messages=self.receive_own_messages,
            fd=self.fd,
            bitrate=self.bitrate,
            data_bitrate=self.data_bitrate,
            sjw_abr=self.sjw_abr,
            tseg1_abr=self.tseg1_abr,
            tseg2_abr=self.tseg2_abr,
            sam_abr=self.sam_abr,
            sjw_dbr=self.sjw_dbr,
            tseg1_dbr=self.tseg1_dbr,
            tseg2_dbr=self.tseg2_dbr,
            app_name=self.app_name,
        )


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


class CanNmWakeupThread:
    def __init__(self, bus: can.BusABC, verbose: bool = True):
        self._bus = bus
        self._verbose = verbose
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="can-nm-wakeup", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)

    def _run(self) -> None:
        msg = can.Message(
            arbitration_id=CAN_NM_MSG_ID,
            is_extended_id=True,
            is_fd=True,
            data=CAN_NM_MSG_DATA,
            dlc=len(CAN_NM_MSG_DATA),
        )
        if self._verbose:
            print("[CAN_NM] sender started")
        while not self._stop.is_set():
            self._bus.send(msg)
            if self._verbose:
                print(f"[CAN_NM] -> ID=0x{CAN_NM_MSG_ID:X} DATA={hex_bytes(bytes(msg.data))}")
            self._stop.wait(CAN_NM_PERIOD_S)
        if self._verbose:
            print("[CAN_NM] sender stopped")


class IsoTpCanTransport:
    """Minimal normal-addressing ISO-TP transport over a shared python-can bus."""

    def __init__(
        self,
        bus: can.BusABC,
        tx_id: int,
        rx_id: int,
        timeout_s: float,
        tx_padding: int = 0x55,
        verbose: bool = False,
    ):
        self._bus = bus
        self._tx_id = tx_id
        self._rx_id = rx_id
        self._timeout_s = timeout_s
        self._tx_padding = tx_padding & 0xFF
        self._verbose = verbose
        self._rx_queue: list[bytes] = []

    def send(self, payload: bytes) -> int:
        try:
            self._send_isotp(payload)
            return len(payload)
        except Exception as exc:
            if self._verbose:
                print(f"[ISO-TP] send failed: {exc}")
            return -1

    def recv(self, max_len: int) -> bytes:
        if not self._rx_queue:
            payload = self._recv_isotp()
            if payload:
                self._rx_queue.append(payload)
        if not self._rx_queue:
            return b""
        return self._rx_queue.pop(0)[:max_len]

    def _make_can_msg(self, data: bytes) -> can.Message:
        padded = data.ljust(8, bytes([self._tx_padding]))
        return can.Message(
            arbitration_id=self._tx_id,
            data=padded,
            is_extended_id=self._tx_id > 0x7FF,
            is_fd=False,
        )

    def _send_can(self, data: bytes) -> None:
        self._bus.send(self._make_can_msg(data))

    def _send_flow_control(self) -> None:
        fc = bytes([0x30, 0x00, 0x00])
        self._bus.send(self._make_can_msg(fc))

    def _send_isotp(self, payload: bytes) -> None:
        if self._verbose:
            print(f"[UDS] -> {hex_bytes(payload)}")

        if len(payload) <= 7:
            self._send_can(bytes([len(payload)]) + payload)
            return

        if len(payload) > 0xFFF:
            raise ValueError("ISO-TP payload too large for 12-bit length")

        first_frame = bytes([
            0x10 | ((len(payload) >> 8) & 0x0F),
            len(payload) & 0xFF,
        ]) + payload[:6]
        self._send_can(first_frame)

        if not self._wait_flow_control():
            raise TimeoutError("timed out waiting for ISO-TP flow control")

        offset = 6
        seq = 1
        while offset < len(payload):
            chunk = payload[offset:offset + 7]
            self._send_can(bytes([0x20 | (seq & 0x0F)]) + chunk)
            offset += len(chunk)
            seq = (seq + 1) & 0x0F

    def _wait_flow_control(self) -> bool:
        deadline = time.monotonic() + self._timeout_s
        while time.monotonic() < deadline:
            msg = self._bus.recv(timeout=UDS_POLL_SLICE_S)
            if msg is None or msg.arbitration_id != self._rx_id or not msg.data:
                continue
            data = bytes(msg.data)
            if data[0] >> 4 != 0x3:
                continue
            return (data[0] & 0x0F) == 0x0
        return False

    def _recv_isotp(self) -> bytes:
        deadline = time.monotonic() + self._timeout_s

        while time.monotonic() < deadline:
            msg = self._bus.recv(timeout=UDS_POLL_SLICE_S)
            if msg is None or msg.arbitration_id != self._rx_id or not msg.data:
                continue

            data = bytes(msg.data)
            frame_type = data[0] >> 4

            # Single Frame
            if frame_type == 0x0:
                # CAN FD extended single-frame: [00][len][payload...]
                if data[0] == 0x00:
                    if len(data) < 2:
                        return b""
                    length = data[1]
                    payload = data[2:2 + length]
                else:
                    length = data[0] & 0x0F
                    payload = data[1:1 + length]

                if self._verbose:
                    print(f"[UDS] <- {hex_bytes(payload)}")
                return payload

            # First Frame
            if frame_type == 0x1:
                total_len = ((data[0] & 0x0F) << 8) | data[1]

                # FF payload starts after 2-byte PCI.
                # For classic CAN DLC=8, this gives 6 bytes.
                # For CAN FD DLC=64, this gives 62 bytes.
                payload = bytearray(data[2:])
                expected_sn = 1

                self._send_flow_control()

                while len(payload) < total_len and time.monotonic() < deadline:
                    cf_msg = self._bus.recv(timeout=UDS_POLL_SLICE_S)
                    if cf_msg is None or cf_msg.arbitration_id != self._rx_id or not cf_msg.data:
                        continue

                    cf_data = bytes(cf_msg.data)
                    if cf_data[0] >> 4 != 0x2:
                        continue

                    sn = cf_data[0] & 0x0F
                    if sn != expected_sn:
                        raise RuntimeError(
                            f"Bad ISO-TP sequence number: expected {expected_sn}, got {sn}"
                        )

                    # CF payload starts after 1-byte PCI.
                    # For classic CAN DLC=8, this gives 7 bytes.
                    # For CAN FD DLC=64, this gives up to 63 bytes.
                    payload.extend(cf_data[1:])
                    expected_sn = (expected_sn + 1) & 0x0F

                if len(payload) < total_len:
                    return b""

                result = bytes(payload[:total_len])
                if self._verbose:
                    print(f"[UDS] <- {hex_bytes(result)}")
                return result

        return b""


class RealAnchorKeyExchangeRunner:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.bus = BusConfig().create_bus()
        self.nm = CanNmWakeupThread(self.bus, verbose=verbose)
        self.transport = IsoTpCanTransport(
            bus=self.bus,
            tx_id=UNLOCK_TXID,
            rx_id=UNLOCK_RXID,
            timeout_s=KEX_TIMEOUT_S,
            tx_padding=CANTP_PADDING,
            verbose=verbose,
        )

    def close(self) -> None:
        try:
            self.nm.stop()
        except Exception:
            pass
        try:
            self.bus.shutdown()
        except Exception:
            pass

    def run(self) -> None:
        self.nm.start()
        time.sleep(WAKEUP_LEAD_TIME_S)

        try:
            with KeyExchange(anchor_idx=0) as kex:
                kex.set_callbacks(self.transport.send, self.transport.recv)
                kex.set_factory_private_key(FACTORY_PRIVATE_KEY_BLOB)
                kex.set_secoc_key(SECOC_KEY)
                kex.set_iv(IV)

                kex.start()

                deadline = time.monotonic() + 10.0

                while not kex.is_complete and not kex.is_failed:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(
                            f"Timed out in step={kex.current_step.name}, "
                            f"last_request={kex.last_request.hex(' ')}, "
                            f"last_response={kex.last_response.hex(' ')}"
                        )

                    ret = kex.step()
                    print(f"[KEX] step={kex.current_step.name} ret={ret.name}")
                    print(f"[KEX] last request : {kex.last_request.hex(' ')}")
                    print(f"[KEX] last response: {kex.last_response.hex(' ')}")
                    time.sleep(0.01)

                if kex.is_failed:
                    raise RuntimeError(kex.last_error)

                print("Key exchange complete")
                print("Encrypted key:", kex.encrypted_key.hex(" "))

                with open("encrypted_key.txt", "w") as f:
                    f.write(kex.encrypted_key.hex(" ") + "\n")

        except KeyExchangeError as exc:
            raise RuntimeError(str(exc)) from exc
        finally:
            self.close()


def main() -> None:
    print("=" * 72)
    print("REAL ANCHOR KEY EXCHANGE")
    print("=" * 72)
    print(f"Channel     : {CAN_CHANNEL}")
    print(f"Interface   : {INTERFACE}")
    print(f"Unlock TX ID: 0x{UNLOCK_TXID:X}")
    print(f"Unlock RX ID: 0x{UNLOCK_RXID:X}")
    print(f"CAN NM ID   : 0x{CAN_NM_MSG_ID:X}")
    print()

    runner = RealAnchorKeyExchangeRunner(verbose=VERBOSE)
    runner.run()


if __name__ == "__main__":
    try:
        main()
    except KeyExchangeError as exc:
        raise SystemExit(f"KeyExchangeError: {exc}")
    except Exception as exc:
        raise SystemExit(f"ERROR: {exc}")
