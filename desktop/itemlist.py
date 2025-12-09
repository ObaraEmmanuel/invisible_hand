from tkinter import Frame, Label

from scrolledframe import ScrolledFrame
from ui_utils import EventMask, config_all, clear_children, bind_all


class CompoundList(ScrolledFrame):
    """
    ListBox widget allowing for more flexibility with custom items extending
    :py:class:`CompoundList.BaseItem`. Here is an example:

    .. code-block:: python

        from hoverset.ui.widgets import CompoundList, Application, Label

        app = Application()

        my_list = CompoundList(app)

        class CustomItem(CompoundList.BaseItem):
            # Custom class to display two fields in a single item

            def render(self):
                occupation, name = self.value
                Label(self, text=f"Occupation: {occupation}").pack(side="top")
                Label(self, text=f"Name: {name}").pack(side="top")

        my_list.set_item_class(CustomItem)
        my_list.set_values([["Engineer", "John"], ["Professor", "Sir Isaac"]])
        my_list.pack()

        app.mainloop()

    """
    MULTI_MODE = 0x001
    SINGLE_MODE = 0x002
    BROWSE_MODE = 0x003

    class BaseItem(Frame):
        """
        Base class for all custom list items
        """

        def __init__(self, master: 'CompoundList', value, index, isolated=False):
            super().__init__(master.body)
            self._value = value
            self._parent: CompoundList = master
            self._index = index
            self._selected = False
            self._allow_selection = True
            self._isolated = isolated
            self.render()
            if not self._isolated:
                bind_all(self, "<Enter>", self._on_hover)
                bind_all(self, "<Leave>", self._on_hover_ended)
                bind_all(self, "<Button-1>", self.select_self, add="+")

        def render(self):
            """
            Create the custom section of a custom item. Override this
            method and add new widgets to the item. The default rendering
            is a label containing the value of the item
            """
            self._text = Label(self, text=self._value, anchor="w")
            self._text.pack(fill="both")

        @property
        def value(self):
            """
            The value the item is supposed to display. Can be any object
            depending on what is set through :py:attr:`CompoundList.set_values`

            :return: Value represented by item
            """
            return self._value

        def select_self(self, event=None, *_):
            """
            Set the item as selected in its parent list

            :param event: event causing the selection. Default is ``None``
            """
            if not self._allow_selection:
                return
            self._parent.select(self._index, event)

        def select(self, *_):
            """
            Marks item as selected and applies the required styles and
            configuration to make it appear selected such as the color
            """
            self._selected = True
            self.on_hover()

        def deselect(self):
            """
            Marks item as deselected and applies the required styles and
            configuration to make it return to its normal state
            """
            self._selected = False
            self.on_hover_ended()

        # We need to add implementation details separate from library
        # user interference
        # Users are therefore free to override the non-private wrappers
        # without breaking core functionality
        def _on_hover(self, *_):
            if self._parent.get_mode() == CompoundList.BROWSE_MODE:
                self._parent.select(self._index)
            else:
                self.on_hover(*_)

        def _on_hover_ended(self, *_):
            if not self._selected:
                self.on_hover_ended(*_)

        def on_hover(self, *_):
            """
            Applies styles and config required when item is hovered
            """
            config_all(self, bg="#2a2a2a")

        def on_hover_ended(self, *_):
            """
            Revert the item config when no longer under hover
            """
            config_all(self, bg="#1c1c1c")

        def get(self):
            """
            Get the value represented by the item

            :return: Value represented by the item
            """
            return self._value

        def clone_to(self, parent):
            """
            Create a copy of the item for positioning in a new parent

            :param parent: New intended parent
            :return: the new item clone
            """
            return self.__class__(parent, self._value, self._index, True)

    # ----------------------------------------- CompoundList -----------------------------------------------

    def __init__(self, master=None, **cnf):
        super().__init__(master, **cnf)
        self._cls = CompoundList.BaseItem  # Default
        self._values = []
        self._current_indices = []
        self._items = []
        self._mode = CompoundList.SINGLE_MODE  # Default
        self._on_change = None

    @property
    def items(self):
        return self._items

    def set_mode(self, mode):
        """
        Set the mode of selection

        :param mode: mode value which can be one of the following

            * :py:attr:`CompoundList.SINGLE_MODE`: allows selection of one
              item at a time
            * :py:attr:`CompoundList.MULTI_MODE`: allows selection of multiple
              items by holding down the control key
            * :py:attr:`CompoundList.BROWSE_MODE`: allows selection of one item
              at a time. Selection will follow the currently hovered item

        """
        self._mode = mode

    def get_mode(self):
        """
        Get currently set mode
        """
        return self._mode

    def set_item_class(self, cls):
        """
        Set the class used to render the list items in the case of custom
        items.

        :param cls: A a subclass of :py:class:`CompoundList.BaseItem`
        """
        self._cls = cls

    def get_class(self):
        """
        Get the item class currently in use

        :return: current item class
        """
        return self._cls

    def set_values(self, values):
        """
        Set the values to be displayed by the list box. Clears current values.
        to add new values use ``add_values``

        :param values: an iterable containing the item values to be displayed
        """
        clear_children(self.body)
        self._items.clear()
        self._current_indices.clear()
        # make a copy
        self._values = list(values)
        self._render(values)

    def _render(self, values):
        for i, val in enumerate(values, start=len(self._items)):
            item = self._cls(self, val, i)
            self._items.append(item)
            item.pack(side="top", fill="x", pady=1)
            item.update_idletasks()

    def add_values(self, values):
        """
        Append new values to the list

        :param values: an iterable containing items to be added
        :return:
        """
        self._values += values
        self._render(values)

    def select(self, index, event=None):
        """
        Select item at given index

        :param index: index to be selected
        :param event: event generating the selection if any
        """
        if event and event.state & EventMask.CONTROL and self._mode == CompoundList.MULTI_MODE:
            self._multi_selector(index)
        else:
            self._single_selector(index)
        if self._on_change:
            self._on_change(self.get())

    def _single_selector(self, index):
        for item in self._current_indices:
            self._items[item].deselect()
        self._current_indices = [index]
        self._items[index].select()

    def _multi_selector(self, index):
        if index in self._current_indices:
            self._current_indices.remove(index)
            self._items[index].deselect()
        else:
            self._current_indices.append(index)
            self._items[index].select()

    def get(self):
        """
        Get currently selected item(s)

        .. note::

            This does not return the underlying value but the rendered item
            currently selected which is a :class:`CompoundList.BaseItem`
            object. To obtain the value use its ``value`` property or ``get``
            method

        :return: selected item if mode is not set to MULTI_MODE otherwise
          a list of all selected items. If no item is selected ``None`` is
          returned
        """
        if self._mode == CompoundList.MULTI_MODE:
            return [self._items[index] for index in self._current_indices]
        if self._current_indices:
            return self._items[self._current_indices[0]]
        return None

    def on_change(self, func, *args, **kwargs):
        """
        Set a callback function to be called on selection change

        :param func: callback function
        :param args: extra positional arguments to be passed to callback
          in addition to the selected item
        :param kwargs: keyword arguments to be passed to callback function
        """
        self._on_change = lambda value: func(value, *args, **kwargs)