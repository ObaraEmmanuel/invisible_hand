import tkinter as tk
from tkinter import ttk

from formation import AppBuilder, Builder

import catalogue
from comm import COMManger, DeviceEventType, DeviceManager, COMCommand, IVHDevice, IVHFrame
from commands import ComponentTree
from macro import MacroList, Macro
from package import IVHPackage
from ui.utils import MouseWheelDispatcher


def center_window(window, master=None):
    if master is None:
        window.update_idletasks()
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        x, y = 0, 0
    else:
        master.update_idletasks()
        width = master.winfo_width()
        height = master.winfo_height()
        x, y = master.winfo_x(), master.winfo_y()
    # window.update_idletasks()
    sub_width = window.winfo_width()
    sub_height = window.winfo_height()
    window.geometry(f"+{x + (width - sub_width) // 2}+{y + (height - sub_height) // 2}")


class AddMacroDialog(Builder):
    def __init__(self, master):
        self._root: tk.Toplevel = None
        self.macro_name: ttk.Entry = None
        super().__init__(master, path="layouts/add_macro.json")
        self._root.transient(master)
        self.connect_callbacks(self)
        self.value = None
        center_window(self._root, master)
        self._root.grab_set()
        self.macro_name.focus_set()

    def on_cancel(self):
        self._root.destroy()

    def on_submit(self):
        self.value = self.macro_name.get()
        self._root.destroy()

    @classmethod
    def get_name(cls, master):
        obj = cls(master)
        master.wait_window(obj._root)
        return obj.value


class App(AppBuilder):
    NO_DEVICE = "No device"

    def __init__(self):
        self.main: tk.Tk = None
        self.package_list: ttk.Treeview = None
        self.package_box: tk.Frame = None
        self.device_select: ttk.Frame = None
        self.device: tk.StringVar = None
        self.upload_btn: ttk.Button = None
        self.flash_btn: ttk.Button = None
        self.command_delete: ttk.Button = None
        self.macro_name_lbl: ttk.Label = None
        self.macro_canvas: ComponentTree = None
        self.macro_list: MacroList = None
        self.macro_menu: tk.Menu = None
        self.catalogue: catalogue.CatalogueList = None
        super().__init__(self, path="layouts/app.json")
        self.connect_callbacks(self)
        MouseWheelDispatcher.set_up_mousewheel(self.main)
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        center_window(self._root)
        self._devices = {}
        self._selected_device = None
        self.device_select["values"] = (self.NO_DEVICE,)
        self.device_select["font"] = None
        self.device.set(self.NO_DEVICE)
        self.device.trace_add("write", self._on_device_selection)
        self._package_image = tk.PhotoImage(file="resources/package.png")
        self._items = {}
        self.active_macro: Macro = None
        self.macro_canvas._menu = self.macro_menu
        self.macro_canvas.on_select(self.on_command_select)
        self.on_command_select()
        self.macro_canvas.load_macro(None)

        self.catalogue.load()
        self.macro_list.on_change(self.macro_changed)
        self.macro_list.load()
        self.main.wm_protocol("WM_DELETE_WINDOW", lambda: [print("exiting"), self.main.destroy()])
        self._update_state()

        self.comm: COMManger = COMManger()
        self.comm.bind(self.main)
        self.comm.start()
        self.comm.add_listener(self._on_device_added, DeviceEventType.ADDED)
        self.comm.add_listener(self._on_device_removed, DeviceEventType.REMOVED)
        self.dev_manager: DeviceManager = None

    def _on_device_added(self, device: IVHDevice):
        if device.port in self._devices:
            return
        self._devices[device.port] = device
        self.device_select["values"] = [self.NO_DEVICE] + [d for d in self._devices]
        if self.device.get() == self.NO_DEVICE:
            self.device.set(device.port)

    def _on_device_removed(self, device: IVHDevice):
        if device.port not in self._devices:
            return
        self._devices.pop(device.port)
        self.device_select["values"] = [self.NO_DEVICE] + [d for d in self._devices]
        if self.device.get() == device.port:
            if self._devices:
                self.device.set(self._devices[0].device)
            else:
                self.device.set(self.NO_DEVICE)

    def _on_device_selection(self, *args):
        if self._selected_device == self.device.get():
            return
        self._selected_device = self.device.get()
        self._update_state()
        if self.dev_manager:
            self.dev_manager.stop()
            self.dev_manager = None
        device = self._devices.get(self.device.get())
        if device is None:
            return
        self.dev_manager = DeviceManager(device)
        self.dev_manager.start()
        self.dev_manager.add_listener(self._on_comm_event)
        self.dev_manager.send(COMCommand.BOARD)
        self.dev_manager.send(COMCommand.MEM)
        self.dev_manager.send(COMCommand.INPUT_TYPE)

    def _on_comm_event(self, device: IVHDevice, frame: IVHFrame):
        match frame.command:
            case COMCommand.BOARD:
                device.board = frame
            case COMCommand.MEM:
                device.memory = frame.body.decode()
            case COMCommand.INPUT_TYPE:
                device.input_type = int.from_bytes(frame.body)

    def _update_state(self):
        if (not self.active_macro) or self.device.get() == self.NO_DEVICE:
            self.upload_btn.grid_remove()
        else:
            self.upload_btn.grid()

    def macro_changed(self, item):
        if not item:
            self.macro_canvas.load_macro(None)
            self.active_macro = None

        self.active_macro = item.value
        self.macro_canvas.load_macro(self.active_macro)
        self.macro_name_lbl.config(text=self.active_macro.name)
        self._update_state()

    def add_macro(self):
        name = AddMacroDialog.get_name(self._root)
        if not name:
            return
        self.macro_list.add_macro(name)

    def save_macro(self):
        if self.active_macro:
            self.active_macro.update(self.macro_canvas.build_tree())

    def upload_macro(self):
        self.dev_manager.send(COMCommand.BOARD)
        print(IVHPackage(self.macro_canvas.build_tree()).as_bytes())

    def execute_macro(self):
        pass

    def delete_macro(self):
        pass

    def clear_macro(self):
        pass

    def on_command_select(self):
        if self.macro_canvas.get():
            self.command_delete.pack(side="right")
        else:
            self.command_delete.pack_forget()

    def delete_command(self):
        if not self.macro_canvas.get():
            return
        to_delete = list(self.macro_canvas.get())
        for node in to_delete:
            self.macro_canvas.deselect(node)
            node.remove()
        self.on_command_select()


if __name__ == "__main__":
    app = App()
    app._root.mainloop()
