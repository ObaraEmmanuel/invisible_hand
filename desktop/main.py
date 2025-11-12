from formation import AppBuilder, Builder
import tkinter as tk
from tkinter import ttk

import tree
from commands import get_component


def center_window(window, master=None):
    if master is None:
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        x, y = 0, 0
    else:
        master.update_idletasks()
        width = master.winfo_reqwidth()
        height = master.winfo_reqheight()
        x, y = master.winfo_x(), master.winfo_y()
    # window.update_idletasks()
    sub_width = window.winfo_reqwidth()
    sub_height = window.winfo_reqheight()
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
        self.package_list: ttk.Treeview = None
        self.package_box: ttk.Frame = None
        self.device_select: ttk.Frame = None
        self.device: tk.StringVar = None
        self.upload_btn: ttk.Button = None
        self.execute_btn: ttk.Button = None
        self.macro_name_lbl: ttk.Label = None
        self.macro_canvas: tree.MalleableTreeView = None
        super().__init__(self, path="layouts/app.json")
        self.device_select['font'] = None
        self.connect_callbacks(self)
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        center_window(self._root)
        self.device_select["values"] = ("Local PC",)
        self.device.set("Local PC")
        self.package_list.heading('#0', text="Macros", anchor=tk.CENTER)
        self._package_image = tk.PhotoImage(file="resources/package.png")
        self._items = {}
        self.load_packages()
        self._set_selection()
        self.macro_canvas.add_as_node(key="KeyPress")
        self.macro_canvas.add_as_node(key="KeyPress")
        self.macro_canvas.add_as_node(key="KeyRelease")
        self.macro_canvas.add_as_node(key="ButtonPress")
        self.macro_canvas.add_as_node(key="KeyHold")
        n = self.macro_canvas.add_as_node(key="MouseMove")
        n.add_as_node(key="KeyPress")
        n.add_as_node(key="KeyPress")
        n.add_as_node(key="KeyPress")
        n = n.add_as_node(key="KeyPress")
        n.add_as_node(key="KeyPress")
        n.add_as_node(key="KeyPress")
        self.macro_canvas.add_as_node(key="KeyPress")




    def load_packages(self):
        packages = [
            ("Macro 1", [
                ("KeyPress", ('', ''), {}),
                # ("Loop", (), {}),
                ("KeyPress", ('', ''), {}),
                ("KeyRelease", ('', ''), {}),
                ("ButtonPress", (), {}),
                ("MouseWheel", (), {}),
                ("KeyHold", (), {}),
                ("MouseMove", (), {}),
            ]),
            ("Macro 2", []),
            ("Macro 3", []),
            ("Macro 4", []),
        ]

        for package in packages:
            self._insert_macro(*package)

    def _set_selection(self, iid=None):
        children = self.package_list.get_children()
        if not len(children):
            return
        iid = iid if iid is not None else children[0]
        self.package_list.focus(iid)
        self.package_list.selection_set(iid)

    def _insert_macro(self, name, body):
        iid = self.package_list.insert('', tk.END, text="   " + name, image=self._package_image)
        self._items[iid] = (name, body, [])
        return iid

    def on_selection_change(self, event):
        selected = self.package_list.focus()
        if not selected:
            return
        self.select_macro(*self._items[selected])

    def select_macro(self, name, body: list, data: list):
        return
        self.macro_name_lbl['text'] = name

        if not data:
            for command in body:
                # data.append(CommandWidget.create(self.macro_canvas, command[0], *command[1], **command[2]))
                klass = get_component(command[0])
                data.append(klass(self.macro_canvas))

        for widget in self.macro_canvas.winfo_children():
            widget.pack_forget()

        for widget in data:
            widget.base.pack(side=tk.TOP, anchor=tk.W, pady='5 0', padx=5)

    def add_macro(self):
        name = AddMacroDialog.get_name(self._root)
        if not name:
            return
        iid = self._insert_macro(name, [])
        self._set_selection(iid)

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
