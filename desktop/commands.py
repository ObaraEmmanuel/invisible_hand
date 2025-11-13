import tkinter as tk
from collections import defaultdict
from tkinter import PhotoImage

from formation import Builder

import tree
from color import to_hex, from_hsl
from keymaps import get_key, get_modifiers, is_modifier, Key, get_button


class WidgetFactory:
    _pool = defaultdict(set)

    def release(self, *_):
        self._pool[self.master].add(self)

    def acquire(self, *_):
        if self in self._pool[self.master]:
            return self._pool[self.master].remove(self)

    @classmethod
    def create(cls, master, *args, **kwargs):
        if pool := cls._pool[master]:
            print("cache hit")
            return pool.pop()
        obj = cls(master, *args, **kwargs)
        obj.bind("<Map>", obj.acquire)
        obj.bind("<Unmap>", obj.release)
        return obj


class CommandComponent:

    def __init__(self, *args, **kwargs):
        self.base: tk.Frame = None
        self.body: tk.Text = None
        self.label: tk.Label = None
        super().__init__(*args, **kwargs)

    @property
    def is_block(self):
        return False

    def select(self, *_):
        # self.base.configure(highlightbackground="#2f60d8")
        pass

    def deselect(self, *_):
        # self.base.configure(highlightbackground="#1c1c1c")
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


class KeyPressBase(Builder, CommandComponent):
    order = [Key.SHIFT, Key.ALT, Key.CONTROL]

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


class KeyPress(KeyPressBase):

    def __init__(self, master):
        super().__init__(master)
        self.set_color(to_hex(from_hsl((140, 55, 20))))

    def on_keypress(self, event):
        modifiers = get_modifiers(event.state)
        if modifiers:
            self.keys.clear()
            self.keys = {*modifiers, *self.keys}
        key = get_key(event.keycode)
        if any(not is_modifier(k) for k in self.keys) and not is_modifier(key):
            self.keys.clear()
        if key:
            self.keys.add(key)
        self.update_text()


class KeyHold(KeyPress):

    def __init__(self, master):
        super().__init__(master)
        self.set_label("Key Hold")
        self.set_color(to_hex(from_hsl((140, 55, 20))))

    def on_keypress(self, event):
        key = get_key(event.keycode)
        if key in self.keys:
            self.keys.remove(key)
        else:
            self.keys.add(key)
        self.update_text()


class KeyRelease(KeyHold):
    def __init__(self, master):
        super().__init__(master)
        self.set_color(to_hex(from_hsl((140, 55, 20))))
        self.set_label("Key Release")


class ButtonPress(KeyPressBase):
    def __init__(self, master):
        super().__init__(master)
        self.set_color(to_hex(from_hsl((40, 55, 20))))
        self.set_label("Button Press")
        self.img = PhotoImage(file="resources/mouse.png")
        self.set_label_img(self.img)

    def on_keypress(self, event):
        key = get_key(event.keycode)
        if is_modifier(key) and self.keys:
            if key in self.keys:
                self.keys.remove(key)
            else:
                self.keys.add(key)
            self.update_text()

    def on_buttonpress(self, event):
        super().on_buttonpress(event)
        if self.clicks_since_focus <= 1:
            return
        modifiers = get_modifiers(event.state)
        button = get_button(event.num)
        self.keys.clear()
        self.keys.update({*modifiers, button})
        self.update_text()


class Loop(Builder, CommandComponent):

    def __init__(self, master):
        super().__init__(master, path="layouts/command.json")
        self.set_color(to_hex(from_hsl((300, 55, 20))))
        self.set_label("Loop forever")
        self.img = PhotoImage(file="resources/loop.png")
        self.set_label_img(self.img)

    @property
    def is_block(self):
        return True


class Randomize(Loop):

    def __init__(self, master):
        super().__init__(master)
        self.img = PhotoImage(file="resources/random.png")
        self.set_label_img(self.img)
        self.set_label("Randomize")
        self.set_color(to_hex(from_hsl((220, 55, 20))))


class LoopFor(Builder, CommandComponent):

    def __init__(self, master):
        super().__init__(master, path="layouts/loopfor.json")

    @property
    def is_block(self):
        return True


class ButtonHold(KeyPressBase):

    def __init__(self, master):
        super().__init__(master)
        self.set_color(to_hex(from_hsl((40, 55, 20))))
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

    def __init__(self, master):
        self.base: tk.Frame = None
        self.delta: tk.IntVar = None
        self.label: tk.Label = None
        super().__init__(master, path="layouts/mousewheel.json")
        self.delta.set(1)
        self.set_color(to_hex(from_hsl((75, 55, 20))))


class MouseMove(Builder, CommandComponent):
    def __init__(self, master):
        self.base: tk.Frame = None
        self.delta_x: tk.IntVar = None
        self.delta_y: tk.IntVar = None
        self.label: tk.Label = None
        super().__init__(master, path="layouts/mousemove.json")
        self.delta_x.set(1)
        self.delta_y.set(1)
        self.set_color(to_hex(from_hsl((75, 55, 20))))


class Delay(Builder, CommandComponent):
    def __init__(self, master):
        super().__init__(master, path="layouts/delay.json")


class DelayRandom(Builder, CommandComponent):
    def __init__(self, master):
        super().__init__(master, path="layouts/delayrandom.json")


_components = (
    KeyPress,
    KeyHold,
    KeyRelease,
    ButtonPress,
    ButtonHold,
    ButtonRelease,
    MouseMove,
    MouseWheel,
    Loop,
    LoopFor,
    Randomize,
    Delay,
    DelayRandom,
)

_components_map = {
    component.__name__: component for component in _components
}


def get_component(key):
    return _components_map[key]


class ComponentTree(tree.TreeView):
    class Node(tree.Tree.Node):

        def __init__(self, master=None, **config):
            super().__init__(master, **config)
            klass = get_component(config.get("key"))
            self.command = klass(self.strip, *config.get("args", ()), **config.get("kwargs", {}))
            self.name_pad.grid_forget()
            self.icon_pad.grid_forget()
            self.expander.grid(row=0, column=1, padx=3)
            self.command.base.grid(row=0, column=3)
            self._init_binding()
            self.editable = True
            self.strict_mode = True
            self.is_terminal = not self.command.is_block

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

    def __init__(self, master=None, **config):
        super().__init__(master, **config)
        self.allow_multi_select(True)
