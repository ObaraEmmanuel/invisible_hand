import tkinter as tk
from tkinter import PhotoImage
from typing import Any

from formation import Builder

import ui.tree
from glue import GlueInterface
from keymaps import get_key, is_modifier, Key, get_button
from macro import Macro
from ui.menu import MenuUtils
from ui.utils import EmptyScreen
from utils.color import to_hex, from_hsl


class CommandComponent:
    color = to_hex(from_hsl((140, 55, 20)))
    image = ""
    type = ""

    def __init__(self, *args, **kwargs):
        self.base: tk.Frame = None
        self.body: tk.Text = None
        self.label: tk.Label = None
        super().__init__(*args, **kwargs)

    @property
    def is_block(self):
        return False

    def select(self, *_):
        pass

    def deselect(self, *_):
        pass

    def as_text(self, *_):
        return self.label['text']

    def set_color(self, color):
        self.label['bg'] = color
        self.base['bg'] = color

    def set_label(self, label):
        self.label['text'] = "   " + label

    def set_label_img(self, img):
        self.label['image'] = img

    def load_data(self, data: dict[str, Any]):
        pass

    def to_data(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
        }


class KeyPressBase(Builder, CommandComponent):
    order = [
        Key.RIGHT_SHIFT,
        Key.LEFT_SHIFT,
        Key.RIGHT_ALT,
        Key.LEFT_ALT,
        Key.RIGHT_CONTROL,
        Key.LEFT_CONTROL
    ]

    def __init__(self, master):
        super().__init__(master, path="layouts/keypress.json")
        self.connect_callbacks(self)
        self.keys = set()
        self.clicks_since_focus = 0

    def clear(self):
        self.keys = set()
        self.update_text()

    def get_key_text(self):
        return " + ".join([i.value for i in sorted(
            self.keys,
            key=lambda x: self.order.index(x) if x in self.order else -1,
            reverse=True
        )])

    def update_text(self):
        text = self.get_key_text()
        self.body.configure(width=max(10, len(text)))
        self.body['state'] = 'normal'
        self.body.delete('0.0', tk.END)
        self.body.insert('0.0', text)
        self.body['state'] = 'disabled'

    def on_keypress(self, event):
        pass

    def on_buttonpress(self, event):
        self.body.focus_force()
        self.clicks_since_focus += 1

    def on_focus_out(self, _):
        self.clicks_since_focus = 0

    def as_text(self, *_):
        return f"{self.label['text']} <{self.get_key_text()}>"

    def load_data(self, data):
        if data:
            self.keys = set(data["keys"])
            self.update_text()

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "keys": list(self.keys),
        }


class KeyPress(KeyPressBase):
    color = to_hex(from_hsl((140, 55, 20)))
    image = "keypress"
    type = "keypress"

    def __init__(self, master):
        super().__init__(master)
        self.set_color(self.color)

    def on_keypress(self, event):
        key = get_key(event.keycode, event.keysym)
        if key in self.keys:
            self.keys.remove(key)
            print(self.keys)
            self.update_text()
            return
        # clear the non-modifier key
        if not is_modifier(key):
            self.keys = {k for k in self.keys if is_modifier(k)}
        if key:
            self.keys.add(key)

        print(self.keys)
        self.update_text()


class KeyHold(KeyPress):
    image = "keypress"

    def __init__(self, master):
        super().__init__(master)
        self.set_label("Key Hold")

    def on_keypress(self, event):
        key = get_key(event.keycode, event.keysym)
        if key in self.keys:
            self.keys.remove(key)
        else:
            self.keys.add(key)
        self.update_text()


class KeyRelease(KeyHold):
    image = "keypress"

    def __init__(self, master):
        super().__init__(master)
        self.set_label("Key Release")


class ButtonPress(KeyPressBase):
    color = to_hex(from_hsl((40, 55, 20)))
    image = "mouse"
    type = "button"

    def __init__(self, master):
        super().__init__(master)
        self.set_color(self.color)
        self.set_label("Button Press")
        self.img = PhotoImage(file="resources/mouse.png")
        self.set_label_img(self.img)

    def on_keypress(self, event):
        # ignore
        pass

    def on_buttonpress(self, event):
        super().on_buttonpress(event)
        if self.clicks_since_focus <= 1:
            return
        button = get_button(event.num)
        self.keys.clear()
        self.keys.update({button})
        self.update_text()


class ButtonHold(KeyPressBase):
    color = to_hex(from_hsl((40, 55, 20)))
    image = "mouse"
    type = "button"

    def __init__(self, master):
        super().__init__(master)
        self.set_color(self.color)
        self.set_label("Button Hold")
        self.img = PhotoImage(file="resources/mouse.png")
        self.set_label_img(self.img)

    def on_buttonpress(self, event):
        super().on_buttonpress(event)
        if self.clicks_since_focus <= 1:
            return
        button = get_button(event.num)
        if button in self.keys:
            self.keys.remove(button)
        else:
            self.keys.add(button)
        self.update_text()


class ButtonRelease(ButtonHold):
    def __init__(self, master):
        super().__init__(master)
        self.set_color(to_hex(from_hsl((40, 55, 20))))
        self.set_label("Button Release")


class MouseWheel(Builder, CommandComponent):
    color = to_hex(from_hsl((75, 55, 20)))
    image = "mouse"
    type = "mouse"

    def __init__(self, master):
        self.base: tk.Frame = None
        self.delta_x: tk.IntVar = None
        self.delta_y: tk.IntVar = None
        self.label: tk.Label = None
        super().__init__(master, path="layouts/mousewheel.json")
        self.delta_x.set(1)
        self.delta_y.set(1)
        self.set_color(self.color)

    def load_data(self, data):
        if data:
            self.delta_x.set(data.get("delta_x", 1))
            self.delta_y.set(data.get("delta_y", 1))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "delta_x": self.delta_x.get(),
            "delta_y": self.delta_y.get(),
        }


class MouseMove(Builder, CommandComponent):
    color = to_hex(from_hsl((75, 55, 20)))
    image = "mouse"
    type = "mouse"

    def __init__(self, master):
        self.base: tk.Frame = None
        self.delta_x: tk.IntVar = None
        self.delta_y: tk.IntVar = None
        self.label: tk.Label = None
        super().__init__(master, path="layouts/mousemove.json")
        self.delta_x.set(1)
        self.delta_y.set(1)
        self.set_color(self.color)

    def load_data(self, data):
        if data:
            self.delta_x.set(data.get("delta_x", 1))
            self.delta_y.set(data.get("delta_y", 1))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "delta_x": self.delta_x.get(),
            "delta_y": self.delta_y.get(),
        }


class Loop(Builder, CommandComponent):
    color = to_hex(from_hsl((300, 55, 20)))
    image = "loop"
    type = "control"

    def __init__(self, master):
        super().__init__(master, path="layouts/command.json")
        self.set_color(self.color)
        self.set_label("Loop forever")
        self.img = PhotoImage(file="resources/loop.png")
        self.set_label_img(self.img)

    @property
    def is_block(self):
        return True


class LoopFor(Builder, CommandComponent):
    color = to_hex(from_hsl((300, 55, 20)))
    image = "loop"
    type = "control"

    def __init__(self, master):
        self.count: tk.IntVar = None
        super().__init__(master, path="layouts/loopfor.json")

    @property
    def is_block(self):
        return True

    def load_data(self, data):
        if data:
            self.count.set(data.get("count", 1))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "count": abs(self.count.get()),
        }


class LoopForRandom(Builder, CommandComponent):
    color = to_hex(from_hsl((300, 55, 20)))
    image = "loop"
    type = "control"

    def __init__(self, master):
        self.start: tk.IntVar = None
        self.stop: tk.IntVar = None
        super().__init__(master, path="layouts/loopforrandom.json")

    @property
    def is_block(self):
        return True

    def load_data(self, data):
        if data:
            self.start.set(data.get("start", 1))
            self.stop.set(data.get("stop", 1))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "start": abs(self.start.get()),
            "stop": abs(self.stop.get()),
        }


class Randomize(Loop):
    color = to_hex(from_hsl((220, 55, 20)))
    image = "random"
    type = "control"

    def __init__(self, master):
        super().__init__(master)
        self.img = PhotoImage(file="resources/random.png")
        self.set_label_img(self.img)
        self.set_label("Randomize")


class Break(Builder, CommandComponent):
    color = to_hex(from_hsl((340, 55, 20)))
    image = "break"
    type = "control"

    def __init__(self, master):
        super().__init__(master, path="layouts/command.json")
        self.set_color(self.color)
        self.set_label("Break")
        self.img = PhotoImage(file="resources/break.png")
        self.set_label_img(self.img)


class Delay(Builder, CommandComponent):
    color = to_hex(from_hsl((75, 55, 20)))
    image = "time"
    type = "time"

    def __init__(self, master):
        self.duration: tk.DoubleVar = None
        super().__init__(master, path="layouts/delay.json")

    def load_data(self, data):
        if data:
            self.duration.set(round(data.get("duration", 1) / 1000, 3))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "duration": int(self.duration.get() * 1000),
        }


class DelayRandom(Builder, CommandComponent):
    color = to_hex(from_hsl((75, 55, 20)))
    image = "time"
    type = "time"

    def __init__(self, master):
        self.stop: tk.DoubleVar = None
        self.start: tk.DoubleVar = None
        super().__init__(master, path="layouts/delayrandom.json")

    def load_data(self, data):
        if data:
            self.stop.set(round(data.get("stop", 0) / 1000, 3))
            self.start.set(round(data.get("start", 1) / 1000, 3))

    def to_data(self):
        return {
            "type": self.__class__.__name__,
            "stop": int(self.stop.get() * 1000),
            "start": int(self.start.get() * 1000),
        }


_components = (
    KeyPress,
    KeyHold,
    KeyRelease,
    ButtonPress,
    ButtonHold,
    ButtonRelease,
    MouseWheel,
    MouseMove,
    Delay,
    DelayRandom,
    Loop,
    LoopFor,
    LoopForRandom,
    Randomize,
    Break,
)

_components_map = {
    component.__name__: component for component in _components
}


def get_component(key):
    return _components_map[key]


class ComponentTree(ui.tree.TreeView):
    class Node(ui.tree.Tree.Node):

        def __init__(self, master=None, **config):
            super().__init__(master, **config)
            klass = get_component(config.get("key"))
            self.command = klass(self.strip)
            self.command.load_data(config.get("data", {}))
            self.expander.grid(row=0, column=1, padx=3)
            self.command.base.grid(row=0, column=3)
            self._init_binding()
            self.editable = True
            self.strict_mode = True
            self.is_terminal = not self.command.is_block
            self.tree.on_node_created(self)

        def _bind_widgets(self):
            return self.strip, self.command.label

        def select(self, event=None, silently=False):
            super().select(event, silently)
            if self._selected:
                self.strip.config(background="#2a2a2a")
                self.expander.config(background="#2a2a2a")
                self.strip.focus_force()

        def deselect(self, *_):
            super().deselect(*_)
            if not self._selected:
                self.strip.config(background="#1c1c1c")
                self.expander.config(background="#1c1c1c")

        @property
        def name(self):
            return self.command.as_text()

        @property
        def icon(self):
            return self.command.label['image']

        def end_drag(self, event):
            if self.tree.drag_active and self.tree.drag_select:
                glue = GlueInterface.instance()
                nodes: list[ComponentTree.Node] = list(self.tree.get())
                old_indices = [n.index() for n in nodes]
                old_parents = [n.parent_node for n in nodes]
                super().end_drag(event)
                glue.on_nodes_moved(nodes, old_parents, old_indices)
            else:
                super().end_drag(event)

    def __init__(self, master=None, **config):
        super().__init__(master, **config)
        self.allow_multi_select(True)
        self._empty_screen = None
        self._node_cache = {}
        self._selection_cache = {}
        self._active_macro = None
        self._menu: tk.Menu = None

    def on_node_created(self, node):
        MenuUtils.bind_all_context(node, lambda event: MenuUtils.popup(event, self._menu))

    @property
    def empty_screen(self):
        if self._empty_screen:
            return self._empty_screen
        self._no_file_image = PhotoImage(file="resources/empty.png")
        self._no_command_image = PhotoImage(file="resources/add.png")
        self._empty_screen = EmptyScreen(self)
        return self._empty_screen

    def remove(self, node):
        if not self._active_macro:
            return
        super().remove(node)
        if not self.nodes:
            self._show_empty_command()

    def add(self, node):
        if not self._active_macro:
            return
        super().add(node)
        self.empty_screen.hide()

    def insert(self, index=None, *nodes):
        if not self._active_macro:
            return
        super().insert(index, *nodes)
        self.empty_screen.hide()

    def _show_empty_file(self):
        self.empty_screen.show(
            text="Select macro file to start",
            image=self._no_file_image
        )

    def _show_empty_command(self):
        self.empty_screen.show(
            text="Drag action from command list",
            image=self._no_command_image
        )

    def _generate_tree(self, parent_node=None, parent_data=None) -> dict:
        if parent_node is None:
            parent_node = self
        if parent_data is None:
            parent_data = {}
        for node in parent_node.nodes:
            node_data = node.command.to_data()
            if "nodes" not in parent_data:
                parent_data["nodes"] = []
            self._generate_tree(node, node_data)
            parent_data["nodes"].append(node_data)
        return parent_data

    def build_tree(self, nodes: list[ComponentTree.Node] = None) -> list[dict]:
        if nodes is None:
            nodes = self.nodes
        data = []
        for node in nodes:
            node_data = node.command.to_data()
            self._generate_tree(node, node_data)
            data.append(node_data)
        return data

    def load_node(self, parent_node: 'ComponentTree.Node', data: dict) -> ComponentTree.Node:
        node = parent_node.add_as_node(key=data.get("type"), data=data)

        for sub_node_data in data.get("nodes", []):
            self.load_node(node, sub_node_data)
        return node

    def load_macro(self, macro: Macro):
        if macro == self._active_macro:
            return

        if self._active_macro:
            self._node_cache[self._active_macro] = list(self.nodes)
            self._selection_cache[self._active_macro] = self.get()

        self.clear()
        self.clear_selection()
        self._active_macro = macro

        if not macro:
            self._show_empty_file()
            return

        if macro in self._node_cache:
            for node in self._node_cache[macro]:
                self.add(node)
        if macro in self._selection_cache:
            for node in self._selection_cache[macro]:
                node.select()
        else:
            # Load afresh
            for sub_node_data in macro.get():
                self.load_node(self, sub_node_data)

        if not self.nodes:
            self._show_empty_command()
        else:
            self.empty_screen.hide()
