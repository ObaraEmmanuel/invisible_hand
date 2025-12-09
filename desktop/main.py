import tkinter as tk
from tkinter import ttk

from formation import AppBuilder, Builder

import catalogue
from commands import ComponentTree
from macro import MacroList, Macro
from ui_utils import MouseWheelDispatcher


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
    window.geometry(f"+{x + (width - sub_width)//2}+{y + (height - sub_height)//2}")


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

    def __init__(self):
        self.main: tk.Tk = None
        self.package_list: ttk.Treeview = None
        self.package_box: tk.Frame = None
        self.device_select: ttk.Frame = None
        self.device: tk.StringVar = None
        self.upload_btn: ttk.Button = None
        self.execute_btn: ttk.Button = None
        self.macro_name_lbl: ttk.Label = None
        self.macro_canvas: ComponentTree = None
        self.macro_list: MacroList = None
        self.catalogue: catalogue.CatalogueList = None
        super().__init__(self, path="layouts/app.json")
        self.device_select['font'] = None
        self.connect_callbacks(self)
        MouseWheelDispatcher.set_up_mousewheel(self.main)
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        center_window(self._root)
        self.device_select["values"] = ("Local PC",)
        self.device.set("Local PC")
        self._package_image = tk.PhotoImage(file="resources/package.png")
        self._items = {}
        self.active_macro: Macro = None
        self.macro_canvas.load_macro(None)

        self.catalogue.load()
        self.macro_list.on_change(self.macro_changed)
        self.macro_list.load()
        self.main.wm_protocol("WM_DELETE", lambda: [print("exiting"), self.main.destroy()])

    def macro_changed(self, item):
        if not item:
            self.macro_canvas.load_macro(None)
            self.active_macro = None

        self.active_macro = item.value
        self.macro_canvas.load_macro(self.active_macro)
        self.macro_name_lbl.config(text=self.active_macro.name)

    def add_macro(self):
        name = AddMacroDialog.get_name(self._root)
        if not name:
            return
        self.macro_list.add_macro(name)

    def save_macro(self):
        if self.active_macro:
            self.active_macro.update(self.macro_canvas.build_tree())

    def upload_macro(self):
        pass

    def execute_macro(self):
        pass

    def delete_macro(self):
        pass

    def clear_macro(self):
        pass


if __name__ == "__main__":
    app = App()
    app._root.mainloop()
