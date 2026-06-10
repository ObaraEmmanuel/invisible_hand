import tkinter as tk

from ui.itemlist import CompoundList
from ui.utils import Popup, chain, disable_all
from utils.animation import Animate, Easing


class Spinner(tk.Frame):
    """
    Combobox widget allowing easy customization of choice items
    """
    __icons_loaded = False
    EXPAND = None
    COLLAPSE = None
    EXPAND_DISABLED = None

    def __init__(self, master=None, **_):
        super().__init__(master)
        self._load_images()
        self._button = tk.Button(
            self,
            image=self.EXPAND,
            width=20, anchor="center", command=self._popup,
            relief=tk.FLAT, borderwidth=0
        )
        self._button.pack(side="right", fill="y")
        self._entry = tk.Frame(self)
        self._entry.body = self._entry
        self._entry.pack(side="left", fill="both", expand=True)
        # self._entry.pack_propagate(0)
        self._popup_window = None
        self._on_create_func = None
        self._on_change = None
        self._values = []
        self._value_item = None
        self._item_cls = CompoundList.BaseItem
        self.dropdown_height = 150

    @classmethod
    def _load_images(cls):
        if cls.__icons_loaded:
            return
        cls.EXPAND = tk.PhotoImage(file="resources/tri_down.png")
        cls.EXPAND_DISABLED = tk.PhotoImage(file="resources/tri_down.png")
        cls.COLLAPSE = tk.PhotoImage(file="resources/tri_up.png")
        cls.__icons_loaded = True

    def _popup(self, _=None):
        if self._popup_window is not None:
            self._popup_window.destroy()
            self._button.config(image=self.EXPAND)
            self._popup_window = None
            return
        self.update_idletasks()
        self.winfo_toplevel().update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        rec = x, y, self.winfo_width(), 0
        popup = self._popup_window = Popup(self.winfo_toplevel(), rec)

        options = self._options_list = CompoundList(popup.body)
        options.set_item_class(self._item_cls)
        options.set_values(self._values)
        options.on_change(self._make_selection)
        options.pack()
        options.update_idletasks()
        initial_height = min(options.content_height(), self.dropdown_height)
        # Sometimes there is no space for the drop-down so we need to check
        # If the initial_height + the distance of the bottom left corner of spinner from the top of the screen
        # is greater than the screen-height we animate upwards
        if y + initial_height + self.winfo_height() >= self.winfo_screenheight():
            direction = 'up'
            rec = x, y, options.max_width + 10, 0
        else:
            # Since we are animating downwards, the top of the dropdown begins at the bottom of the spinner
            y = y + self.winfo_height()
            rec = x, y, options.max_width + 10, 0
            direction = 'down'
        popup.set_geometry(rec)

        def update_popup(dx):
            if direction == 'up':
                # No space down so animate upwards
                popup.set_geometry((x, y - int(dx), rec[2], int(dx)))
            else:
                # Animate down by default
                popup.set_geometry((x, y, rec[2], int(dx)))

            options.update_idletasks()
            popup.update_idletasks()

        Animate(popup, 0, initial_height, update_popup,
                easing=Easing.SLING_SHOT, dur=0.2)
        update_popup(initial_height)
        self._button.config(image=self.COLLAPSE)
        popup.on_close(self._close_popup)

    def _close_popup(self):
        self._popup_window = None
        self._options_list = None
        # This fails at times during program close up
        try:
            self._button.config(image=self.EXPAND)
        except tk.TclError:
            pass

    def config_all(self, **cnf):
        self.config(**cnf)
        self._entry.config(**cnf)
        self._button.config(**cnf)

    @chain
    def on_create(self, func, *args, **kwargs):
        self._on_create_func = lambda: func(*args, **kwargs)

    def on_change(self, func, *args, **kwargs):
        self._on_change = lambda val: func(val, *args, **kwargs)

    def set_values(self, values):
        self._values = list(values)
        if values:
            self.set(values[0])

    def add_values(self, *values):
        self._values += values

    def remove_value(self, value):
        if value in self._values:
            self._values.remove(value)

    def set(self, value):
        if self.get() == value:
            return
        if value in self._values:
            if self._value_item:
                self._value_item.pack_forget()
            self._value_item = self._item_cls(self._entry, value, self._values.index(value), True)
            self._value_item.pack(fill="both")

    def set_item_class(self, class_):
        self._item_cls = class_

    def _make_selection(self, item):
        if self._value_item:
            self._value_item.pack_forget()
        self._value_item = item.clone_to(self._entry)
        self._value_item.pack(fill="both")
        if self._on_change is not None:
            self._on_change(item.get())
        self._popup()

    def disabled(self, flag):
        disable_all(self, flag)
        if flag:
            # use normal state to avoid the default disabled stipple
            self._button.config(image=self.EXPAND_DISABLED, state='normal')
        else:
            self._button.config(image=self.EXPAND)

    def get(self):
        if self._value_item is None:
            return None
        return self._value_item.get()
