import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from formation import AppBuilder, Builder

import catalogue
from comm import COMManger, DeviceEventType, DeviceManager, COMCommand, IVHDevice, IVHFrame, BlankDevice, IVHState
from commands import ComponentTree
from device_select import DeviceSelector
from glue import GlueInterface
from macro import MacroList, Macro
from package import IVHPackage
from ui.tree import Tree, InsertType
from ui.utils import MouseWheelDispatcher
from utils.action import Action
from utils.system import unsigned_to_bytes


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


class UploadMacroDialog(Builder):
    def __init__(self, master, text: str):
        self._root: tk.Toplevel = None
        self.msg_lbl: ttk.Label = None
        self.progress: ttk.Progressbar = None
        self.progress_lbl: tk.Label = None
        super().__init__(master, path="layouts/upload_macro.json")
        self.msg_lbl["text"] = text
        self._root.transient(master)
        self.connect_callbacks(self)
        self.value = None
        center_window(self._root, master)
        self._root.grab_set()
        self._root.focus_force()

    def update_progress(self, done, total):
        self.progress['value'] = int(done * 100 / total)
        self.progress_lbl["text"] = f"{done}B / {total}B"

    def destroy(self):
        self._root.destroy()

    def exists(self):
        return self._root.winfo_exists()


class FlashMacroDialog(Builder):
    def __init__(self, master, on_flash):
        self._root: tk.Toplevel = None
        self.msg_lbl: ttk.Label = None
        self.progress: ttk.Progressbar = None
        self.progress_lbl: tk.Label = None
        self.cancel_btn: ttk.Button = None
        self.flash_btn: ttk.Button = None
        super().__init__(master, path="layouts/flash_macro.json")
        self.progress.grid_remove()
        self.msg_lbl["text"] = (
            "The uploaded macro will be permanently saved to the board.\n"
            "Note that doing this too often may wear out the flash on your board."
        )
        self._root.transient(master)
        self.connect_callbacks(self)
        self.value = None
        center_window(self._root, master)
        self._root.grab_set()
        self.cancel_btn.focus_set()
        self._on_flash = on_flash

    def flash(self):
        if self._on_flash:
            self._on_flash()
        self.msg_lbl["text"] = "Flashing uploaded macro to permanent storage..."
        self.progress.grid()
        self.progress.start()
        self.cancel_btn.grid_remove()
        self.flash_btn.grid_remove()

    def cancel(self):
        self._root.destroy()

    def completed(self, status: bool):
        self.progress.grid_remove()
        self.flash_btn.grid_remove()
        self.cancel_btn.grid()
        self.cancel_btn["text"] = "Finish"
        self.cancel_btn.focus_set()
        if status:
            self.msg_lbl["text"] = "Package was flashed successfully."
        else:
            self.msg_lbl["text"] = "Package flashing failed."

    def destroy(self):
        self._root.destroy()

    def exists(self):
        return self._root.winfo_exists()


class App(AppBuilder, GlueInterface):
    NO_DEVICE = BlankDevice()

    def __init__(self):
        GlueInterface.set_instance(self)
        self.main: tk.Tk = None
        self.package_list: ttk.Treeview = None
        self.package_box: tk.Frame = None
        self.device_select: DeviceSelector = None
        self.upload_btn: ttk.Button = None
        self.play_btn: ttk.Button = None
        self.flash_btn: ttk.Button = None
        self.command_delete: ttk.Button = None
        self.command_undo: ttk.Button = None
        self.command_redo: ttk.Button = None
        self.command_copy: ttk.Button = None
        self.command_cut: ttk.Button = None
        self.command_paste: ttk.Button = None
        self.command_save: ttk.Button = None
        self.macro_canvas: ComponentTree = None
        self.macro_list: MacroList = None
        self.macro_menu: tk.Menu = None
        self.catalogue: catalogue.CatalogueList = None
        super().__init__(path="layouts/app.json")
        self.connect_callbacks(self)
        MouseWheelDispatcher.set_up_mousewheel(self.main)
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        center_window(self._root)
        self._devices = [self.NO_DEVICE]
        self._selected_device = self.NO_DEVICE
        self.device_select.on_change(self._on_device_selection)
        self.device_select.set_values((self.NO_DEVICE,))
        self._package_image = tk.PhotoImage(file="resources/package.png")
        self._play_image = tk.PhotoImage(file="resources/play.png")
        self._pause_image = tk.PhotoImage(file="resources/pause.png")
        self._items = {}
        self.active_macro: Macro = None
        self.macro_canvas._menu = self.macro_menu
        self.macro_canvas.on_select(self.on_command_select)

        self.button_criteria: dict[tk.Widget, list[Callable]] = {
            self.command_delete: {"action": "hide", "criteria": [self.has_selection]},
            self.command_undo: {"action": "disable", "criteria": [self.has_undo]},
            self.command_redo: {"action": "disable", "criteria": [self.has_redo]},
            self.command_copy: {"action": "hide", "criteria": [self.has_selection]},
            self.command_cut: {"action": "hide", "criteria": [self.has_selection]},
            self.command_save: {"action": "hide", "criteria": [lambda: True]},
        }

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
        self._flash_dialog: FlashMacroDialog = None
        self._upload_dialog: UploadMacroDialog = None
        self._upload_package = b''
        self._total_upload = 1
        self._last_state = IVHState.UNSET

    def _on_device_added(self, device: IVHDevice):
        if device in self._devices:
            return
        self._devices.append(device)
        self.device_select.add_values(device)
        if self.device_select.get() == self.NO_DEVICE:
            self.device_select.set(device)
            self._on_device_selection()

    def _on_device_removed(self, device: IVHDevice):
        if device not in self._devices:
            return
        self._devices.remove(device)
        if self.device_select.get() == device:
            for dev in self._devices:
                if dev != self.NO_DEVICE:
                    self.device_select.set(dev)
                    break
            else:
                self.device_select.set(self.NO_DEVICE)
            self._on_device_selection()
            self._on_active_device_removed()
            self._update_state()
        self.device_select.remove_value(device)

    def _on_device_selection(self, *_):
        if self._selected_device == self.device_select.get():
            return
        self._selected_device = self.device_select.get()
        self._update_state()
        if self.dev_manager:
            self.dev_manager.stop()
            self.dev_manager = None

        if self._selected_device is None:
            return
        self.dev_manager = DeviceManager(self._selected_device)
        self.dev_manager.start()
        self.dev_manager.add_listener(self._on_comm_event)

    def _on_active_device_removed(self):
        if self._upload_dialog:
            self._upload_dialog.destroy()
            self._upload_dialog = None

    def _on_comm_event(self, device: IVHDevice, frame: IVHFrame):
        match frame.command:
            case COMCommand.IDENT:
                if device.state != self._last_state:
                    self._update_state()
                self._last_state = device.state
            case COMCommand.PACKAGE_PROGRESS:
                uploaded = int.from_bytes(frame.body, byteorder="little")
                if self._total_upload > uploaded:
                    self.dev_manager.send(self._upload_package[uploaded: uploaded + 32])
                else:
                    self.dev_manager.send_command(COMCommand.RESTART)
                self._update_progress(uploaded)
            case COMCommand.FLASH:
                success = int.from_bytes(frame.body, byteorder="little")
                if self._flash_dialog and self._flash_dialog.exists():
                    self._flash_dialog.completed(bool(success))

    def _update_progress(self, uploaded):
        if not self._upload_dialog:
            return
        self._upload_dialog.update_progress(uploaded, self._total_upload)
        if self._total_upload <= uploaded:
            self._upload_dialog._root.after(2000, self._close_upload_dialog)

    def _close_upload_dialog(self):
        if self._upload_dialog:
            self._upload_dialog.destroy()
            self._upload_dialog = None

    def _update_state(self):
        dev = self.device_select.get()
        if (not self.active_macro) or dev is self.NO_DEVICE:
            self.upload_btn.grid_remove()
            self.play_btn.grid_remove()
            self.flash_btn.grid_remove()
        else:
            self.upload_btn.grid()
            if dev.state != IVHState.INVALID:
                self.play_btn.grid()
                self.flash_btn.grid()
                if dev.state in (IVHState.PAUSED, IVHState.STOPPED):
                    self.play_btn['image'] = self._play_image
                else:
                    self.play_btn['image'] = self._pause_image
            else:
                self.play_btn.grid_remove()
                self.flash_btn.grid_remove()

    def macro_changed(self, item):
        if not item:
            self.macro_canvas.load_macro(None)
            self.active_macro = None

        self.active_macro = item.value
        self.macro_canvas.load_macro(self.active_macro)
        self._update_state()
        self._update_macro_state()

    def add_macro(self):
        name = AddMacroDialog.get_name(self._root)
        if not name:
            return
        self.macro_list.add_macro(name)

    def save_macro(self):
        if self.active_macro:
            self.active_macro.update(self.macro_canvas.build_tree())

    def upload_macro(self):
        self._upload_package = IVHPackage(self.macro_canvas.build_tree()).as_bytes()
        self._upload_dialog = UploadMacroDialog(
            self.main,
            f"Uploading macro to {self._selected_device.board}"
        )
        self._total_upload = len(self._upload_package)
        self.dev_manager.send_command(COMCommand.PACKAGE, unsigned_to_bytes(self._total_upload))
        self.dev_manager.send(self._upload_package[:32])
        self._upload_dialog.update_progress(0, self._total_upload)

    def flash_macro(self):
        self._flash_dialog = FlashMacroDialog(self.main, self._flash)

    def _flash(self):
        self.dev_manager.send_command(COMCommand.FLASH)

    def toggle_machine_state(self):
        dev = self.device_select.get()
        if not dev or dev is self.NO_DEVICE:
            return

        if dev.state == IVHState.PAUSED:
            self.dev_manager.send_command(COMCommand.RESUME)
        elif dev.state == IVHState.STOPPED:
            self.dev_manager.send_command(COMCommand.RESTART)
        else:
            self.dev_manager.send_command(COMCommand.PAUSE)

    def config_board(self):
        pass

    def delete_macro(self):
        pass

    def clear_macro(self):
        pass

    def copy_commands(self):
        pass

    def cut_commands(self):
        pass

    def undo_command(self):
        if self.active_macro:
            self.active_macro.undo()
        self._update_macro_state()

    def redo_command(self):
        if self.active_macro:
            self.active_macro.redo()
        self._update_macro_state()

    def _update_macro_state(self):
        for button, criteria in self.button_criteria.items():
            if all(c() for c in criteria["criteria"]):
                if criteria["action"] == "hide":
                    button.grid()
                else:
                    button["state"] = tk.NORMAL
            else:
                if criteria["action"] == "hide":
                    button.grid_remove()
                else:
                    button["state"] = tk.DISABLED

    def has_selection(self) -> bool:
        return bool(self.macro_canvas.get())

    def has_undo(self) -> bool:
        if self.active_macro:
            return self.active_macro.has_undo()
        return False

    def has_redo(self) -> bool:
        if self.active_macro:
            return self.active_macro.has_redo()
        return False

    def on_command_select(self):
        self._update_macro_state()

    def delete_commands(self):
        if not self.macro_canvas.get():
            return
        to_delete = list(self.macro_canvas.get())
        for node in to_delete:
            self.macro_canvas.deselect(node)
        self.delete_nodes(to_delete, silent=False)
        self.on_command_select()

    def add_action(self, action: Action):
        if self.active_macro:
            self.active_macro.add_action(action)
            self._update_macro_state()

    # Glue logic

    def add_node(self, target: Tree.Node, node: Tree.Node, method: InsertType, silent: bool = True):
        if not self.active_macro:
            return
        match method:
            case InsertType.INSERT_BEFORE:
                target.insert_before(node)
            case InsertType.INSERT_INTO:
                target.insert(None, node)
            case InsertType.INSERT_INTO_TOP:
                target.insert(0, node)
            case InsertType.INSERT_AFTER:
                target.insert_after(node)
        if not silent:
            parent = node.parent_node
            index = node.index()
            self.add_action(Action(
                undo=lambda _: self.delete_nodes([node]),
                redo=lambda _: self.restore_nodes([node], [parent], [index])
            ))

    def delete_nodes(self, nodes: list[Tree.Node], silent: bool = True):
        if not self.active_macro:
            return
        nodes = self._compact(nodes)
        if not silent:
            old_parents = [node.parent_node for node in nodes]
            old_indices = [node.index() for node in nodes]
            self.add_action(Action(
                undo=lambda _: self.restore_nodes(nodes, old_parents, old_indices),
                redo=lambda _: self.delete_nodes(nodes)
            ))
        for node in nodes:
            node.remove()

    def on_nodes_moved(self, nodes: list[Tree.Node], old_parents: list[Tree.Node], old_indices: list[int]):
        indices = [node.index() for node in nodes]
        parents = [node.parent_node for node in nodes]
        self.add_action(Action(
            undo=lambda _: self._move_nodes(nodes, old_parents, old_indices),
            redo=lambda _: self._move_nodes(nodes, parents, indices)
        ))

    def _move_nodes(self, nodes: list[Tree.Node], parents: list[Tree.Node], indices: list[int]):
        for node in nodes:
            node.remove()
        for node, parent, index in sorted(zip(nodes, parents, indices), key=lambda x: x[2]):
            parent.insert(index, node)

    def restore_nodes(self, nodes: list[Tree.Node], old_parents: list[Tree.Node], old_indices: list[int]):
        for node, parent, index in sorted(zip(nodes, old_parents, old_indices), key=lambda p: p[2]):
            parent.insert(index, node)


def run():
    app = App()
    app._root.mainloop()


if __name__ == "__main__":
    run()
