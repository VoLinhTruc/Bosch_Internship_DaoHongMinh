from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import can
from keyexchange import KeyExchange, KeyExchangeError

FACTORY_PRIVATE_KEY_BLOB = bytes.fromhex(
    "e4c32b6a84bc243adffcda64f3bf449697adc6529073544ad178f89b8dfba657"
)


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


@dataclass(slots=True)
class BusConfig:
    interface: str = "vector"
    channel: int | str = 0
    receive_own_messages: bool = False
    fd: bool = True
    bitrate: int = 500_000
    data_bitrate: int = 2_000_000
    sjw_abr: int = 16
    tseg1_abr: int = 63
    tseg2_abr: int = 16
    sam_abr: int = 1
    sjw_dbr: int = 8
    tseg1_dbr: int = 31
    tseg2_dbr: int = 8
    app_name: Optional[str] = None

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


@dataclass(slots=True)
class UdsConfig:
    anchor_id: int
    cantp_padding: int = 0x55
    poll_slice_s: float = 0.01
    timeout_s: float = 30.0

    @property
    def unlock_txid(self) -> int:
        return 0x700 + self.anchor_id

    @property
    def unlock_rxid(self) -> int:
        return 0x720 + self.anchor_id


@dataclass(slots=True)
class AnchorKeyExchangeConfig:
    bus: BusConfig
    uds: UdsConfig
    verbose: bool = True
    overall_timeout_s: float = 10.0
    settle_delay_s: float = 0.0
    secoc_output_path: Optional[Path] = None
    iv: bytes = bytes(16)


@dataclass(slots=True)
class KeyExchangeResult:
    completed: bool
    secoc_key: bytes
    secoc_key_path: Path
    final_step: str
    last_request: bytes
    last_response: bytes


class IsoTpCanTransport:
    def __init__(self, bus: can.BusABC, uds: UdsConfig, verbose: bool = False):
        self._bus = bus
        self._tx_id = uds.unlock_txid
        self._rx_id = uds.unlock_rxid
        self._timeout_s = uds.timeout_s
        self._poll_slice_s = uds.poll_slice_s
        self._tx_padding = uds.cantp_padding & 0xFF
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
            msg = self._bus.recv(timeout=self._poll_slice_s)
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
            msg = self._bus.recv(timeout=self._poll_slice_s)
            if msg is None or msg.arbitration_id != self._rx_id or not msg.data:
                continue

            data = bytes(msg.data)
            frame_type = data[0] >> 4

            if frame_type == 0x0:
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

            if frame_type == 0x1:
                total_len = ((data[0] & 0x0F) << 8) | data[1]
                payload = bytearray(data[2:])
                expected_sn = 1

                self._send_flow_control()

                while len(payload) < total_len and time.monotonic() < deadline:
                    cf_msg = self._bus.recv(timeout=self._poll_slice_s)
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

                    payload.extend(cf_data[1:])
                    expected_sn = (expected_sn + 1) & 0x0F

                if len(payload) < total_len:
                    return b""

                result = bytes(payload[:total_len])
                if self._verbose:
                    print(f"[UDS] <- {hex_bytes(result)}")
                return result

        return b""


class AnchorKeyExchangeClient:
    def __init__(self, config: AnchorKeyExchangeConfig):
        self.config = config
        self.bus = self.config.bus.create_bus()
        self.transport = IsoTpCanTransport(self.bus, self.config.uds, verbose=self.config.verbose)

    @classmethod
    def from_json(
        cls,
        json_path: str | Path,
        *,
        verbose: bool = True,
        overall_timeout_s: float = 10.0,
        settle_delay_s: float = 0.0,
        secoc_output_path: str | Path | None = None,
    ) -> "AnchorKeyExchangeClient":
        path = Path(json_path)
        data = json.loads(path.read_text(encoding="utf-8"))

        anchor_id = int(data["anchor_id"])
        if not 0 <= anchor_id <= 0xF:
            raise ValueError("anchor_id must fit in one hex digit (0-15)")

        bus_cfg = BusConfig(
            interface=str(data["interface"]),
            channel=data["channel"],
        )
        uds_cfg = UdsConfig(anchor_id=anchor_id)

        output_path = Path(secoc_output_path) if secoc_output_path else path.with_name(
            f"secoc_key_anchor_{anchor_id}.txt"
        )

        cfg = AnchorKeyExchangeConfig(
            bus=bus_cfg,
            uds=uds_cfg,
            verbose=verbose,
            overall_timeout_s=overall_timeout_s,
            settle_delay_s=settle_delay_s,
            secoc_output_path=output_path,
        )
        return cls(cfg)

    def close(self) -> None:
        try:
            self.bus.shutdown()
        except Exception:
            pass

    def __enter__(self) -> "AnchorKeyExchangeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def run_keyexchange(self) -> tuple[str, str]:
        result = self.run_exchange()
        return (
            "Key exchange completed successfully",
            str(result.secoc_key_path),
        )

    def run_exchange(self) -> KeyExchangeResult:
        if self.config.settle_delay_s > 0:
            time.sleep(self.config.settle_delay_s)

        secoc_key = secrets.token_bytes(96)
        secoc_path = self.config.secoc_output_path or Path("secoc_key.txt")

        try:
            with KeyExchange(anchor_idx=self.config.uds.anchor_id) as kex:
                kex.set_callbacks(self.transport.send, self.transport.recv)
                kex.set_factory_private_key(FACTORY_PRIVATE_KEY_BLOB)
                kex.set_secoc_key(secoc_key)
                kex.set_iv(self.config.iv)

                kex.start()
                deadline = time.monotonic() + self.config.overall_timeout_s

                while not kex.is_complete and not kex.is_failed:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(
                            f"Timed out in step={kex.current_step.name}, "
                            f"last_request={kex.last_request.hex(' ')}, "
                            f"last_response={kex.last_response.hex(' ')}"
                        )

                    ret = kex.step()
                    if self.config.verbose:
                        print(f"[KEX] step={kex.current_step.name} ret={ret.name}")
                        print(f"[KEX] last request : {kex.last_request.hex(' ')}")
                        print(f"[KEX] last response: {kex.last_response.hex(' ')}")
                    time.sleep(0.01)

                if kex.is_failed:
                    raise RuntimeError(kex.last_error)

                secoc_path.write_text(secoc_key.hex(" ") + "\n", encoding="utf-8")

                return KeyExchangeResult(
                    completed=True,
                    secoc_key=secoc_key,
                    secoc_key_path=secoc_path,
                    final_step=kex.current_step.name,
                    last_request=kex.last_request,
                    last_response=kex.last_response,
                )
        except KeyExchangeError as exc:
            raise RuntimeError(str(exc)) from exc
