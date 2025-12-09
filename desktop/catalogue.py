from collections import defaultdict
from tkinter import Label, PhotoImage

import commands
import itemlist
from commands import CommandComponent, ComponentTree
from tree import InsertType
from ui_utils import DraggableMixin, WidgetTree


class CatalogueItem(DraggableMixin, itemlist.CompoundList.BaseItem):
    def __init__(self, parent, val, i):
        self.command: type[CommandComponent] | str = val
        self._image = None
        self._text = None
        self._prev_node: ComponentTree | ComponentTree.Node = None
        super().__init__(parent, val, i)
        if isinstance(self.command, type):
            self.allow_drag = True

    def render(self):
        if isinstance(self.command, type):
            self._image = PhotoImage(file=f"resources/{self.command.image}.png")
            self._text = Label(self, text=f"  {self.command.__name__}", anchor="w", image=self._image, compound="left")
            self._text.pack(fill="both", padx=10, pady="0 5")
        else:
            self._text = Label(self, text=self.command.title(), anchor="w", fg="#aaaaaa")
            self._text.pack(fill="both", padx=10, pady="5")

    def render_drag(self, window):
        Label(window, text=self.command.__name__, image=self._image, compound="left").pack(fill="both")

    def on_hover(self, *_):
        if isinstance(self.command, str):
            return
        super().on_hover(*_)

    def on_hover_ended(self, *_):
        if isinstance(self.command, str):
            return
        super().on_hover_ended(*_)

    def on_drag(self, event):
        node: ComponentTree.Node | ComponentTree = WidgetTree.event_first(
            event, self.winfo_toplevel(),
            (ComponentTree.Node, ComponentTree)
        )
        if node:
            if isinstance(node, ComponentTree.Node):
                node._edge_scroll(event)
            node.react(event)
            self._prev_node = node
        elif self._prev_node:
            self._prev_node.clear_highlight()
            self._prev_node.clear_indicators()
            self._prev_node = None

    def on_drag_end(self, event):
        node: ComponentTree.Node | ComponentTree = WidgetTree.event_first(
            event, self.winfo_toplevel(),
            (ComponentTree.Node, ComponentTree)
        )
        if node:
            new_node = node.add_as_node(key=self.command.__name__)
            action = node.react(event)
            node.clear_highlight()
            node.clear_indicators()
            match action:
                case InsertType.INSERT_BEFORE:
                    node.insert_before(new_node)
                case InsertType.INSERT_INTO:
                    node.insert(None, new_node)
                case InsertType.INSERT_AFTER:
                    node.insert_after(new_node)


class CatalogueList(itemlist.CompoundList):

    def __init__(self, parent, **config):
        super().__init__(parent, **config)
        self.set_item_class(CatalogueItem)

    def load(self):
        table = defaultdict(list)

        for command in commands._components:
            table[command.type].append(command)

        items = []
        for key, command_list in table.items():
            items.append(key)
            items.extend(command_list)

        self.add_values(items)
