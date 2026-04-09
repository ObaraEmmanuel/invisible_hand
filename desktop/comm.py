import queue
import struct
import threading
import time
import tkinter
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class DeviceEventType(Enum):
    ADDED = 1
    REMOVED = 2


class COMCommand(Enum):
    INVALID = 0
    PACKAGE = 0x10
    RESTART = 0x11
    PAUSE = 0x12
    RESUME = 0x13
    FLASH = 0x14
    PACKAGE_PROGRESS = 0x30
    IDENT = 0x31


class IVHState(Enum):
    UNSET = -1
    INVALID = 0
    STOPPED = 1
    WAITING = 2
    WAITING_INTERNAL = 3
    RUNNING = 4
    PAUSED = 5


class IVHInputTypes(Enum):
    NONE = 0
    USB = 1
    BLE = 1 << 1
    KEYBOARD = 1 << 2
    MOUSE = 1 << 3


@dataclass
class IVHIdent:
    input_type: int
    state: IVHState
    mem_size: int
    board: str


class IVHDevice:

    def __init__(self, dev: ListPortInfo):
        self.port = self.name = self.info = None
        if dev:
            self.port = dev.device
            self.name = dev.name
            self.info = dev
        self.board = "Unknown"
        self.mem = 0
        self.input_type = 0
        self.valid = True
        self.state = 0

    def update(self, ident: IVHIdent):
        self.board = ident.board
        self.mem = ident.mem_size
        self.input_type = ident.input_type
        self.state = ident.state

    def __eq__(self, other):
        if isinstance(other, IVHDevice):
            return self.port == other.port

    def __hash__(self):
        return hash(self.port)


class BlankDevice(IVHDevice):

    def __init__(self):
        super().__init__(None)
        self.valid = False
        self.port = "----"
        self.board = "No device"
        self.name = "No device"


@dataclass
class DeviceEvent:
    device: IVHDevice
    type: DeviceEventType


@dataclass
class IVHFrame:
    device: IVHDevice
    command: COMCommand
    body: bytes


class DeviceManager:
    WRITE_TIMEOUT = 0.5
    READ_TIMEOUT = 0.8
    POST_OPEN_DELAY = 0.25  # seconds (some boards reset on open; give them a moment)
    START_DELIMITER = b"\x99\x00"
    END_DELIMITER = b"\x00\x99"
    MAX_BODY_SIZE = 256

    def __init__(self, device: IVHDevice | ListPortInfo, baudrate: int = 115200):
        self.device: IVHDevice | ListPortInfo = device
        if isinstance(device, IVHDevice):
            self.port: str = device.port
        else:
            self.port: str = device.device
        self.baudrate: int = baudrate
        self.buffer = bytearray()
        self._send_queue: queue.Queue[bytes] = queue.Queue()
        self._listening: bool = False
        self._listeners: Callable[IVHDevice, IVHFrame] = []
        self.last_ident: IVHIdent = None

    def add_listener(self, listener: Callable[IVHDevice, IVHFrame]):
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[IVHDevice, IVHFrame]):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _emit_event(self, frame: IVHFrame):
        for listener in self._listeners:
            listener(self.device, frame)

    def _get_serial(self) -> serial.Serial:
        return serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.READ_TIMEOUT,
            write_timeout=self.WRITE_TIMEOUT,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            dsrdtr=None,
        )

    def _feed(self, data: bytes):
        """Feed new serial data and yield parsed frames."""
        self.buffer.extend(data)

        frames = []
        s_delim_len = len(self.START_DELIMITER)
        e_delim_len = len(self.END_DELIMITER)
        payload_start = s_delim_len + 2  # delim + len + cmd
        while True:
            start = self.buffer.find(self.START_DELIMITER)
            if start == -1:
                # no delimiter at all: discard garbage before buffer end
                self.buffer.clear()
                break

            if start > 0:
                # discard leading noise
                print(self.buffer[:start].decode(errors='ignore'), end='')
                del self.buffer[:start]

            # need at least: delim + len
            if len(self.buffer) < s_delim_len + 1:
                break

            length = self.buffer[s_delim_len]

            frame_len = payload_start + length + e_delim_len  # delim + len + cmd + payload + delim

            if len(self.buffer) < frame_len:
                break  # incomplete

            # verify end delimiter
            if self.buffer[payload_start + length:frame_len] != self.END_DELIMITER:
                # bad frame: resync by dropping first byte
                print(chr(self.buffer[0]), end='')
                del self.buffer[0]
                continue

            cmd = self.buffer[s_delim_len + 1]
            payload = self.buffer[payload_start:payload_start + length]
            frames.append(IVHFrame(device=self.device, command=COMCommand(cmd), body=payload))

            # remove parsed frame
            del self.buffer[:frame_len]

        return frames

    def stop(self):
        self._listening = False

    def start(self):
        threading.Thread(target=self.listen, args=(0,), daemon=True).start()

    def send_command(self, command: COMCommand, data: bytes = b''):
        if not self._listening:
            raise RuntimeError("Device manager not listening")
        if len(data) > self.MAX_BODY_SIZE:
            raise ValueError("Data too long")
        payload = bytearray()
        payload.extend(self.START_DELIMITER)
        payload.append(len(data))
        payload.append(int(command.value))
        payload.extend(data)
        payload.extend(self.END_DELIMITER)
        self._send_queue.put(payload)

    def send(self, data: bytes = b''):
        self._send_queue.put(data)

    def listen(self, timeout: float, wait_ident: bool = False) -> bool:
        self._listening = True
        success = False
        ident_found = False
        try:
            with self._get_serial() as ser:
                ser.rts = False
                ser.dtr = False
                time.sleep(self.POST_OPEN_DELAY)
                start = time.time()
                deadline = start + timeout

                while self._listening:
                    while not self._send_queue.empty():
                        ser.write(self._send_queue.get())
                    response = ser.read(ser.in_waiting)
                    if response:
                        frames = self._feed(response)
                        for frame in frames:
                            self._emit_event(frame)
                            if frame.command == COMCommand.IDENT:
                                ident_found = True
                                input_type, state, mem = struct.unpack(
                                    "<BBQ", frame.body[:10]
                                )
                                self.last_ident = IVHIdent(
                                    input_type, IVHState(state), mem,
                                    frame.body[10:].decode(errors="ignore")
                                )
                                if isinstance(self.device, IVHDevice):
                                    self.device.update(self.last_ident)
                                success = True
                        if ident_found and wait_ident:
                            break
                    if timeout > 0:
                        tick = time.time()
                        if tick > deadline or tick < start:
                            success = False
                            break
                    time.sleep(0.1)
        except (serial.SerialException, OSError):
            success = False

        self._listening = False
        return success


class COMManger:
    BAUDRATE = 115200
    PORT_POLL_INTERVAL = 0.3
    PROBE_TIMEOUT = 5

    def __init__(self):
        self.devices: set[ListPortInfo] = set()
        self.ivh_devices: dict[ListPortInfo: IVHDevice] = {}
        self._listener_thread: threading.Thread = None
        self._is_listening: bool = False
        self._event_queue: queue.Queue[DeviceEvent] = queue.Queue()
        self._probe_queue: queue.Queue[IVHDevice] = queue.Queue()
        self._listeners: dict[list[Callable[IVHDevice]]] = defaultdict(list)
        self._widget = None
        self.buffer = bytearray()

    def start(self) -> None:
        if self._listener_thread is not None and self._is_listening:
            return
        self._is_listening = True
        self._listener_thread = threading.Thread(target=self._com_port_listener, daemon=True)
        self._listener_thread.start()

    def stop(self) -> None:
        self.is_listening = False

    def bind(self, widget: tkinter.Widget) -> None:
        self._widget = widget
        if self._widget is not None:
            self._widget.after(int(self.PORT_POLL_INTERVAL * 1000), self._emit_events)

    def _emit_events(self) -> None:
        while not self._event_queue.empty():
            event: DeviceEvent = self._event_queue.get()
            for listener in self._listeners[event.type]:
                listener(event.device)
        if self._widget:
            self._widget.after(int(self.PORT_POLL_INTERVAL * 1000), self._emit_events)

    def add_listener(self, listener: Callable[IVHDevice], event_type: DeviceEventType) -> None:
        self._listeners[event_type].append(listener)

    def remove_listener(self, listener: Callable[IVHDevice], event_type: DeviceEventType) -> None:
        if listener in self._listeners[type]:
            self._listeners[event_type].remove(listener)

    def _com_port_listener(self) -> None:
        while self._is_listening:
            dev_list = set(list_ports.comports())
            added = dev_list - self.devices
            removed = self.devices - dev_list

            for dev in added:
                self.devices.add(dev)
                threading.Thread(target=self.probe, args=(dev,), daemon=True).start()

            for dev in removed:
                self.devices.remove(dev)
                if dev in self.ivh_devices:
                    ivh_dev = self.ivh_devices.pop(dev)
                    self._event_queue.put(DeviceEvent(ivh_dev, DeviceEventType.REMOVED))

            while not self._probe_queue.empty():
                dev = self._probe_queue.get()
                if dev.info in self.devices:
                    self.ivh_devices[dev.info] = dev
                    self._event_queue.put(DeviceEvent(dev, DeviceEventType.ADDED))

            time.sleep(self.PORT_POLL_INTERVAL)

        self._listener_thread = None

    def probe(self, device: ListPortInfo):
        dev_manager = DeviceManager(device, self.BAUDRATE)
        if status := dev_manager.listen(self.PROBE_TIMEOUT, True):
            dev = IVHDevice(device)
            dev.update(dev_manager.last_ident)
            self._probe_queue.put(dev)
        return status
