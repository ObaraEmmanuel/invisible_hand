import json
import queue
import subprocess
import sys
import threading
import time
import tkinter
from copy import deepcopy
from tkinter import ttk

from formation import Builder
from serial.tools import list_ports

import glue
from comm import DeviceEventType
from ui.utils import center_window


class FlashDialog(Builder):

    def __init__(self, parent, spec):
        self.main: tkinter.Toplevel = None
        self.flash_message: ttk.Label = None
        self.log_text: tkinter.Text = None
        self.flash_progress: ttk.Progressbar = None
        self.close_btn: ttk.Button = None
        super().__init__(parent, path="layouts/flash_firmware.json")
        self.connect_callbacks(self)
        self.main.withdraw()
        center_window(self.main, parent)
        self.main.transient(parent)
        self.main.grab_set()
        self.main.focus_set()
        self.main.deiconify()
        self.spec = spec
        threading.Thread(target=self._flash).start()

    def destroy(self):
        self.main.destroy()

    def _build_command(self) -> list:
        if getattr(sys, 'frozen', False):
            # running in pyinstaller
            command = ["flash.exe"]
        else:
            command = [sys.executable, "flash.py"]

        for option in self.spec["options"]:
            command.append(option)
            if self.spec["options"][option] != '':
                command.append(self.spec["options"][option])
        for offset, image in self.spec["images"].items():
            command.extend([offset, image])
        return command

    def _flash(self):
        glue.GlueInterface.instance().close_connections()
        self.flash_progress.start(10)
        env = self.spec["env"]
        self.flash_message["text"] = f"Uploading <{env}> firmware..."
        process = subprocess.Popen(
            self._build_command(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
        )

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break

            if line:
                self.log_text["state"] = "normal"
                self.log_text.insert("end", f"{line.strip()} \n")
                self.log_text.see('end')
                self.log_text["state"] = "disabled"

        return_code = process.wait()
        self.flash_progress.stop()

        if return_code == 0:
            self.flash_message["text"] = f"Successfully uploaded <{env}> firmware!"
            self.flash_progress.config(mode="determinate", value=100)
        else:
            self.flash_message["text"] = f"Firmware <{env}> upload failed. [{return_code}]"
            self.log_text["fg"] = "#d12121"
            self.flash_progress.config(mode="determinate", value=0)

        self.close_btn["state"] = "normal"
        self.close_btn.focus_set()

    @classmethod
    def upload(cls, parent, spec) -> 'FlashDialog':
        dialog = FlashDialog(parent, spec)
        return dialog


class ConfigWindow(Builder):
    _active_instance = None

    def __init__(self, parent=None):
        self.main: tkinter.Toplevel = None
        # Firmware flash
        self.com_selector: ttk.Combobox = None
        self.board_selector: ttk.Combobox = None
        self.com_advisory_lbl: ttk.Label = None
        self.flash_btn: ttk.Button = None
        super().__init__(parent, path="layouts/config.json")
        self.connect_callbacks(self)
        self.com_advisory_lbl["text"] = (
            "Unplug then plug in your board to detrmine port\n"
            "Make sure the cable in use supports data transfer"
        )
        self.com_selector["state"] = "disabled"
        self.main.withdraw()
        center_window(self.main, parent)
        self.main.transient(parent)
        self.main.grab_set()
        self.main.focus_set()
        self.main.deiconify()
        self.main.wm_protocol("WM_DELETE_WINDOW", self._exit)
        self._listening = False
        self._dev_list = set(list_ports.comports())
        threading.Thread(target=self._listen, daemon=True).start()
        self._device_event_queue = queue.Queue()
        self.main.after(1000, self._update_advisory)
        self.board_selector.bind("<<ComboboxSelected>>", self._on_value_change)
        self.com_selector.bind("<<ComboboxSelected>>", self._on_value_change)
        self._on_value_change()
        self.board_selector["values"] = ["test", "test2", "test3"]
        self.upload_spec = {}
        with open("upload_spec.json", "r") as f:
            self.upload_spec = json.load(f)
        self.board_selector["values"] = list(self.upload_spec.keys())

    def _exit(self):
        self.main.destroy()

    def lift(self):
        self.main.lift()

    def exists(self):
        return self.main.winfo_exists()

    def flash(self):
        env = self.board_selector.get()
        spec = deepcopy(self.upload_spec[env])
        spec["options"]["--port"] = self.com_selector.get()
        spec["env"] = env
        FlashDialog.upload(self.main, spec)

    def _update_advisory(self):
        last = None
        while not self._device_event_queue.empty():
            last = self._device_event_queue.get()
        if last:
            ev_type, dev = last
            if ev_type == DeviceEventType.ADDED:
                self.com_advisory_lbl["text"] = f"{dev.device} plugged in"
            else:
                self.com_advisory_lbl["text"] = f"{dev.device} unplugged"
        ports = [p.device for p in self._dev_list]
        self.com_selector["values"] = ports
        if not ports:
            self.com_selector["state"] = "disabled"
        else:
            self.com_selector["state"] = "readonly"
        self.main.after(1000, self._update_advisory)

    def _listen(self):
        self._listening = True
        while self._listening:
            new_devs = set(list_ports.comports())
            added = new_devs - self._dev_list
            removed = self._dev_list - new_devs
            self._dev_list = new_devs

            for dev in added:
                self._device_event_queue.put((DeviceEventType.ADDED, dev))

            for dev in removed:
                self._device_event_queue.put((DeviceEventType.REMOVED, dev))

            time.sleep(0.7)

    def _on_value_change(self, *_):
        port = self.com_selector.get()
        board = self.board_selector.get()
        if port and board:
            self.flash_btn["state"] = "normal"
        else:
            self.flash_btn["state"] = "disabled"
        self.board_selector.selection_clear()
        self.com_selector.selection_clear()

    @classmethod
    def show(cls, parent) -> 'ConfigWindow':
        if cls._active_instance is None or not cls._active_instance.exists():
            cls._active_instance = ConfigWindow(parent)
        cls._active_instance.lift()
        return cls._active_instance
