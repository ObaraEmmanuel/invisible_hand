import queue
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


@dataclass
class DeviceEvent:
    device: ListPortInfo
    type: DeviceEventType


class COMManger:
    BAUDRATE = 115200
    WRITE_TIMEOUT = 0.5
    READ_TIMEOUT = 0.8
    POST_OPEN_DELAY = 0.25  # seconds (some boards reset on open; give them a moment)
    PORT_POLL_INTERVAL = 0.5
    DELIMITER = b"\x99\x99"

    def __init__(self):
        self.devices: set[ListPortInfo] = set()
        self.ivh_devices: set[ListPortInfo] = set()
        self._listener_thread: threading.Thread = None
        self._is_listening: bool = False
        self._event_queue: queue.Queue[DeviceEvent] = queue.Queue()
        self._listeners: dict[list[Callable[ListPortInfo]]] = defaultdict(list)
        self._widget = None

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

    def add_listener(self, listener: Callable[ListPortInfo], event_type: DeviceEventType) -> None:
        self._listeners[event_type].append(listener)

    def remove_listener(self, listener: Callable[ListPortInfo], event_type: DeviceEventType) -> None:
        if listener in self._listeners[type]:
            self._listeners[event_type].remove(listener)

    def _com_port_listener(self) -> None:
        while self._is_listening:
            dev_list = set(list_ports.comports())
            added = dev_list - self.devices
            removed = self.devices - dev_list

            for dev in added:
                self.devices.add(dev)
                if self.probe(dev.device):
                    self.ivh_devices.add(dev)
                    self._event_queue.put(DeviceEvent(dev, DeviceEventType.ADDED))
            for dev in removed:
                self.devices.remove(dev)
                if dev in self.ivh_devices:
                    self.ivh_devices.remove(dev)
                    self._event_queue.put(DeviceEvent(dev, DeviceEventType.REMOVED))

            time.sleep(self.PORT_POLL_INTERVAL)

        self._listener_thread = None

    def probe(self, port: str) -> bool:
        if self._wait_command(port, 5) == b"IVH":
            return True
        return False

    def _serial_from_port(self, port) -> serial.Serial:
        return serial.Serial(
            port=port,
            baudrate=self.BAUDRATE,
            timeout=self.READ_TIMEOUT,
            write_timeout=self.WRITE_TIMEOUT,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            dsrdtr=None,
        )

    def _extract_frame(self, response: bytes) -> bytes:
        offset = 0
        delim_len = len(self.DELIMITER)
        while True:
            start = response.find(self.DELIMITER, offset)
            if start == -1:
                return None

            length_pos = start + delim_len
            if length_pos >= len(response):
                # Too short to read length
                return None

            payload_length = response[length_pos]
            payload_start = length_pos + 1
            payload_end = payload_start + payload_length

            if payload_end + delim_len > len(response):
                # Too short to read full frame
                offset = start + delim_len
                continue

            if response[payload_end: payload_end + delim_len] != self.DELIMITER:
                # Invalid un-delimited frame, find next delimiter start
                offset = start + delim_len
                continue

            return response[payload_start: payload_start + payload_length]

    def _wait_command(self, port: str, timeout: float) -> bytes:
        try:
            with self._serial_from_port(port) as ser:
                ser.rts = False
                ser.dtr = False
                time.sleep(self.POST_OPEN_DELAY)
                full_response = bytearray()
                start = time.time()
                deadline = start + timeout
                while True:
                    response = ser.read(ser.in_waiting)
                    if response:
                        full_response.extend(response)
                        frame = self._extract_frame(full_response)
                        if frame:
                            return frame
                    tick = time.time()
                    if tick > deadline or tick < start:
                        break
                    time.sleep(0.3)
        except (serial.SerialException, OSError) as e:
            # Port busy, permission denied, vanished, etc.
            pass
        return None
