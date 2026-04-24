from __future__ import annotations

import ctypes
import os
from ctypes import CFUNCTYPE, POINTER, c_char_p, c_int, c_uint8, c_void_p
from enum import IntEnum
from pathlib import Path
from typing import Callable


class RunState(IntEnum):
    IDLE = 0
    RUNNING = 1
    COMPLETE = 2
    FAILED = 3


class Step(IntEnum):
    IDLE = 0
    DEFAULT_SESSION = 1
    EXTENDED_SESSION = 2
    REQUEST_SEED = 3
    SECURITY_UNLOCK = 4
    PUBLIC_KEY_EXCHANGE = 5
    DELIVER_ENCRYPTED_KEY = 6
    COMPLETE = 7
    FAILED = 8


class TickResult(IntEnum):
    OK = 0
    PENDING = 1
    COMPLETE = 2
    FAILED = -1
    BAD_ARGUMENT = -2
    NOT_CONFIGURED = -3
    CAN_CALLBACK_MISSING = -4


class KeyExchangeError(RuntimeError):
    pass


SEND_FUNC = CFUNCTYPE(c_int, POINTER(c_uint8), c_int)
RECV_FUNC = CFUNCTYPE(c_int, POINTER(c_uint8), c_int)


def _candidate_library_names() -> list[str]:
    return [
        "key_exchange_library.dll",
        "libkey_exchange_library.dll",
        "libkey_exchange_library.so",
        "key_exchange_library.so",
        "libkey_exchange_library.dylib",
        "key_exchange_library.dylib",
    ]


def find_library_path(explicit_path: str | os.PathLike[str] | None = None) -> Path:
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"DLL/shared library not found: {path}")
        return path

    env_value = os.environ.get("KEYEXCHANGE_DLL")
    if env_value:
        path = Path(env_value).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"KEYEXCHANGE_DLL points to a missing file: {path}")
        return path

    package_dir = Path(__file__).resolve().parent
    for folder in [package_dir, package_dir / "bin", package_dir.parent, Path.cwd()]:
        for name in _candidate_library_names():
            candidate = folder / name
            if candidate.exists():
                return candidate.resolve()

    searched = []
    for folder in [package_dir, package_dir / "bin", package_dir.parent, Path.cwd()]:
        for name in _candidate_library_names():
            searched.append(str(folder / name))
    raise FileNotFoundError(
        "Could not locate the native key exchange library. "
        "Pass dll_path=..., set KEYEXCHANGE_DLL, or place the DLL next to the package. "
        f"Searched: {searched}"
    )


class _Library:
    def __init__(self, dll_path: str | os.PathLike[str] | None = None):
        self.path = find_library_path(dll_path)
        self._dll_dir_handles = []
        if os.name == "nt":
            self._add_windows_dll_dirs()
        self.lib = ctypes.CDLL(str(self.path))
        self._bind()

    def _add_windows_dll_dirs(self) -> None:
            if not hasattr(os, "add_dll_directory"):
                return

            package_dir = Path(__file__).resolve().parent
            candidates = [
                self.path.parent,
                package_dir,
                package_dir / "bin",
                Path(r"C:\msys64\ucrt64\bin"),
            ]

            seen = set()
            for candidate in candidates:
                resolved = candidate.resolve()
                if resolved in seen or not resolved.exists():
                    continue
                seen.add(resolved)
                self._dll_dir_handles.append(os.add_dll_directory(str(resolved)))


    def _bind(self) -> None:
        lib = self.lib
        lib.KeyExchange_Create.argtypes = [c_int]
        lib.KeyExchange_Create.restype = c_void_p
        lib.KeyExchange_Destroy.argtypes = [c_void_p]
        lib.KeyExchange_Destroy.restype = None

        lib.KeyExchange_SetCanCallbacks.argtypes = [c_void_p, SEND_FUNC, RECV_FUNC]
        lib.KeyExchange_SetCanCallbacks.restype = c_int
        lib.KeyExchange_ClearCanCallbacks.argtypes = [c_void_p]
        lib.KeyExchange_ClearCanCallbacks.restype = c_int

        lib.KeyExchange_SetAnchorIdx.argtypes = [c_void_p, c_int]
        lib.KeyExchange_SetAnchorIdx.restype = c_int
        lib.KeyExchange_SetFactoryPrivateKey.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_SetFactoryPrivateKey.restype = c_int
        lib.KeyExchange_SetSecocKey.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_SetSecocKey.restype = c_int
        lib.KeyExchange_SetIV.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_SetIV.restype = c_int
        lib.KeyExchange_SetNoResponseLimit.argtypes = [c_void_p, c_int]
        lib.KeyExchange_SetNoResponseLimit.restype = c_int

        lib.KeyExchange_Start.argtypes = [c_void_p]
        lib.KeyExchange_Start.restype = c_int
        lib.KeyExchange_Step.argtypes = [c_void_p]
        lib.KeyExchange_Step.restype = c_int
        lib.KeyExchange_Reset.argtypes = [c_void_p]
        lib.KeyExchange_Reset.restype = None

        lib.KeyExchange_GetState.argtypes = [c_void_p]
        lib.KeyExchange_GetState.restype = c_int
        lib.KeyExchange_GetStep.argtypes = [c_void_p]
        lib.KeyExchange_GetStep.restype = c_int
        lib.KeyExchange_IsRunning.argtypes = [c_void_p]
        lib.KeyExchange_IsRunning.restype = c_int
        lib.KeyExchange_IsComplete.argtypes = [c_void_p]
        lib.KeyExchange_IsComplete.restype = c_int
        lib.KeyExchange_IsFailed.argtypes = [c_void_p]
        lib.KeyExchange_IsFailed.restype = c_int

        lib.KeyExchange_GetEncryptedKey.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_GetEncryptedKey.restype = c_int
        lib.KeyExchange_GetLastRequest.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_GetLastRequest.restype = c_int
        lib.KeyExchange_GetLastResponse.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        lib.KeyExchange_GetLastResponse.restype = c_int
        lib.KeyExchange_GetLastError.argtypes = [c_void_p]
        lib.KeyExchange_GetLastError.restype = c_char_p


class KeyExchange:
    def __init__(self, dll_path: str | os.PathLike[str] | None = None, anchor_idx: int = 0):
        self._dll = _Library(dll_path)
        self._handle = self._dll.lib.KeyExchange_Create(anchor_idx)
        if not self._handle:
            raise KeyExchangeError("failed to create KeyExchange handle")

        self._send_cb_ref = None
        self._recv_cb_ref = None
        self._closed = False

    def close(self) -> None:
        if not self._closed and self._handle:
            self._dll.lib.KeyExchange_Destroy(self._handle)
            self._handle = None
            self._closed = True

    def __enter__(self) -> "KeyExchange":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    @staticmethod
    def _as_u8_array(data: bytes | bytearray | memoryview):
        raw = bytes(data)
        return (c_uint8 * len(raw)).from_buffer_copy(raw), len(raw)

    def _check_open(self) -> None:
        if self._closed or not self._handle:
            raise KeyExchangeError("KeyExchange handle is closed")

    def _check_result(self, ret: int, action: str) -> int:
        if ret < 0:
            raise KeyExchangeError(f"{action} failed with code {ret}: {self.last_error}")
        return ret

    def _read_variable_buffer(self, getter_name: str) -> bytes:
        self._check_open()
        getter = getattr(self._dll.lib, getter_name)
        needed = getter(self._handle, None, 0)
        if needed < 0:
            raise KeyExchangeError(f"{getter_name} failed with code {needed}: {self.last_error}")
        if needed == 0:
            return b""
        buf = (c_uint8 * needed)()
        actual = getter(self._handle, buf, needed)
        if actual < 0:
            raise KeyExchangeError(f"{getter_name} failed with code {actual}: {self.last_error}")
        return bytes(buf[:actual])

    def set_anchor_idx(self, anchor_idx: int) -> None:
        self._check_open()
        self._check_result(self._dll.lib.KeyExchange_SetAnchorIdx(self._handle, anchor_idx), "set_anchor_idx")

    def set_factory_private_key(self, data: bytes | bytearray | memoryview) -> None:
        self._check_open()
        buf, length = self._as_u8_array(data)
        self._check_result(self._dll.lib.KeyExchange_SetFactoryPrivateKey(self._handle, buf, length), "set_factory_private_key")

    def set_secoc_key(self, data: bytes | bytearray | memoryview) -> None:
        self._check_open()
        buf, length = self._as_u8_array(data)
        self._check_result(self._dll.lib.KeyExchange_SetSecocKey(self._handle, buf, length), "set_secoc_key")

    def set_iv(self, data: bytes | bytearray | memoryview) -> None:
        self._check_open()
        buf, length = self._as_u8_array(data)
        self._check_result(self._dll.lib.KeyExchange_SetIV(self._handle, buf, length), "set_iv")

    def set_no_response_limit(self, value: int) -> None:
        self._check_open()
        self._check_result(self._dll.lib.KeyExchange_SetNoResponseLimit(self._handle, value), "set_no_response_limit")

    def set_callbacks(
        self,
        send: Callable[[bytes], int],
        recv: Callable[[int], bytes | bytearray | memoryview],
    ) -> None:
        self._check_open()

        def _send(data_ptr, length):
            payload = bytes(data_ptr[:length]) if length > 0 else b""
            return int(send(payload))

        def _recv(buffer_ptr, max_len):
            data = bytes(recv(int(max_len)))
            count = min(len(data), int(max_len))
            if count > 0:
                ctypes.memmove(buffer_ptr, data, count)
            return count

        self._send_cb_ref = SEND_FUNC(_send)
        self._recv_cb_ref = RECV_FUNC(_recv)
        self._check_result(
            self._dll.lib.KeyExchange_SetCanCallbacks(self._handle, self._send_cb_ref, self._recv_cb_ref),
            "set_callbacks",
        )

    def clear_callbacks(self) -> None:
        self._check_open()
        self._check_result(self._dll.lib.KeyExchange_ClearCanCallbacks(self._handle), "clear_callbacks")
        self._send_cb_ref = None
        self._recv_cb_ref = None

    def start(self) -> None:
        self._check_open()
        self._check_result(self._dll.lib.KeyExchange_Start(self._handle), "start")

    def step(self) -> TickResult:
        self._check_open()
        ret = self._dll.lib.KeyExchange_Step(self._handle)
        if ret < 0:
            raise KeyExchangeError(f"step failed with code {ret}: {self.last_error}")
        return TickResult(ret)

    def reset(self) -> None:
        self._check_open()
        self._dll.lib.KeyExchange_Reset(self._handle)

    @property
    def state(self) -> RunState:
        self._check_open()
        return RunState(self._dll.lib.KeyExchange_GetState(self._handle))

    @property
    def current_step(self) -> Step:
        self._check_open()
        return Step(self._dll.lib.KeyExchange_GetStep(self._handle))

    @property
    def is_running(self) -> bool:
        self._check_open()
        return bool(self._dll.lib.KeyExchange_IsRunning(self._handle))

    @property
    def is_complete(self) -> bool:
        self._check_open()
        return bool(self._dll.lib.KeyExchange_IsComplete(self._handle))

    @property
    def is_failed(self) -> bool:
        self._check_open()
        return bool(self._dll.lib.KeyExchange_IsFailed(self._handle))

    @property
    def encrypted_key(self) -> bytes:
        return self._read_variable_buffer("KeyExchange_GetEncryptedKey")

    @property
    def last_request(self) -> bytes:
        return self._read_variable_buffer("KeyExchange_GetLastRequest")

    @property
    def last_response(self) -> bytes:
        return self._read_variable_buffer("KeyExchange_GetLastResponse")

    @property
    def last_error(self) -> str:
        self._check_open()
        ptr = self._dll.lib.KeyExchange_GetLastError(self._handle)
        return ptr.decode("utf-8") if ptr else ""
