import os
from tkinter import Label, PhotoImage
import platformdirs
import constants
from itemlist import CompoundList
import pathlib
import json

from keymaps import EnumEncoder, as_enum
from ui_utils import EmptyScreen


class Macro:

    def __init__(self, macro_path: pathlib.Path):
        self.macro_path = macro_path
        if not self.macro_path.exists():
            with open(macro_path, "w") as f:
                f.write("[]")
        self.name = macro_path.stem
        self.data = None

    def get(self):
        if self.data:
            return self.data
        with open(self.macro_path, "r") as f:
            try:
                self.data = json.load(f, object_hook=as_enum)
            except json.decoder.JSONDecodeError:
                self.data = []
        return self.data

    def update(self, data):
        with open(self.macro_path, "w") as f:
            json.dump(data, f, cls=EnumEncoder)
        self.data = data


class MacroItem(CompoundList.BaseItem):

    def __init__(self, parent, val: Macro, i):
        self._value: Macro = val
        super().__init__(parent, val, i)

    def render(self):
        self._image = PhotoImage(file="resources/file.png")
        self._text = Label(self, text=f"   {self._value.name}", anchor='w', image=self._image, compound="left")
        self._text.pack(fill="x", padx=10, pady="0 5")


class MacroList(CompoundList):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.set_item_class(MacroItem)
        self.macros: dict = {}
        self._path: pathlib.Path = pathlib.Path(platformdirs.user_data_dir(
            constants.APP_NAME,
            constants.APP_AUTHOR,
            ensure_exists=True
        ))
        self._macros_path: pathlib.Path = self._path / "macros"
        os.makedirs(self._macros_path, exist_ok=True)

        self._empty_screen = None

    @property
    def empty_screen(self):
        if self._empty_screen:
            return self._empty_screen
        self._image = PhotoImage(file="resources/add_file.png")
        self._empty_screen = EmptyScreen(self, text="Add new macro file", image=self._image)
        return self._empty_screen
        
    def set_values(self, values):
        if not values:
            self.empty_screen.show()
        else:
            self.empty_screen.hide()
        super().set_values(values)

    def add_macro(self, macro):
        macro = f"{macro}.json" if not macro.endswith(".json") else macro
        macro_path = self._macros_path / macro
        if macro_path.exists():
            return
        macro = Macro(macro_path)
        self.add_values((macro,))
        self.select(len(self._items) - 1)
        self.empty_screen.hide()

    def load(self):
        for file in os.listdir(self._macros_path):
            file_path = self._macros_path / file
            if not file_path.is_file():
                continue

            macro = Macro(file_path)
            self.macros[macro] = macro

        self.set_values(
            self.macros.values()
        )
        if self._items:
            self.select(0)
