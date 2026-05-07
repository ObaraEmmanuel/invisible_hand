import json
import os
import pathlib
from tkinter import Label, PhotoImage

import platformdirs

import constants
from keymaps import EnumEncoder, as_enum
from ui.itemlist import CompoundList
from ui.utils import EmptyScreen
from utils.action import Action


class Macro:

    def __init__(self, macro_path: pathlib.Path):
        self.macro_path = macro_path
        if not self.macro_path.exists():
            with open(macro_path, "w") as f:
                f.write("[]")
        self.name = macro_path.stem
        self.data = None
        self._undo_stack = []
        self._redo_stack = []

    def add_action(self, action: Action):
        self._redo_stack.clear()
        self._undo_stack.append(action)

    def undo(self):
        if self._undo_stack:
            action = self._undo_stack.pop()
            action.undo()
            self._redo_stack.append(action)

    def redo(self):
        if self._redo_stack:
            action = self._redo_stack.pop()
            action.redo()
            self._undo_stack.append(action)

    def has_redo(self) -> bool:
        return bool(self._redo_stack)

    def has_undo(self) -> bool:
        return bool(self._undo_stack)

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
            self.macros[file_path] = macro

        self.set_values(
            self.macros.values()
        )
        if self._items:
            self.select(0)
