from formation import Builder
import tkinter as tk

from ivh.comm import IVHDevice
from ivh.ui.itemlist import CompoundList
from ivh.ui.spinner import Spinner
from ivh.ui.utils import bind_all


class DeviceItemBuilder(Builder):

    def __init__(self, parent, **kwargs):
        self.board: tk.Label = None
        self.port: tk.Label = None
        self.img: tk.Label = None
        super().__init__(parent, **kwargs)


class DeviceItem(CompoundList.BaseItem):

    def __init__(self, master, value: IVHDevice, index, isolated=False):
        self._value: IVHDevice = value
        super().__init__(master, value, index, isolated)
        if self._isolated:
            bind_all(self, "<Enter>", self.on_hover)
            bind_all(self, "<Leave>", self.on_hover_ended)

    def render(self):
        self._build = DeviceItemBuilder(self, path="layouts/device.json")
        self._build._root.grid(sticky='nswe')
        self.update_render()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.update_render()

    def update_render(self):
        if not self._build:
            return
        if self._value:
            self._build.board["text"] = self._value.board
            self._build.port["text"] = self._value.port


class DeviceSelector(Spinner):

    def __init__(self, parent, **kwargs):
        self._value_item: DeviceItem = None
        super().__init__(parent, **kwargs)
        self.config(highlightthickness=1, highlightbackground="#2a2a2a")
        self._item_cls = DeviceItem
        self._button.pack_forget()
        bind_all(self, "<Button-3>", self._popup)

    @classmethod
    def _load_images(cls):
        pass

    def set(self, value):
        if self.get() == value:
            return
        super().set(value)
        if self._value_item:
            bind_all(self._value_item, "<Button-1>", self._popup)

    def _make_selection(self, item):
        super()._make_selection(item)
        if self._value_item:
            bind_all(self._value_item, "<Button-1>", self._popup)

    def _popup(self, _=None):
        super()._popup()
        if self._options_list:
            self._options_list.configure(highlightthickness=1, highlightbackground="#2a2a2a")

    def update_value(self, item: IVHDevice):
        if self.get() == item:
            if self._value_item:
                self._value_item.value = item
