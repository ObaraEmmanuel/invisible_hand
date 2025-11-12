import functools
import tkinter as tk

from platform_utils import platform_is, MAC


class EventMask:
    """
    Event mask values to be used to test events occurring with these
    states set. For instance, to check whether control button was
    down the following check can be performed

    .. code:: python

        def on_event(event):
            if event.state & EventMask.CONTROL:
                print("Control button pressed")

    .. table::

        ============================  ========================
        Event Mask                    Event status
        ============================  ========================
        EventMask.SHIFT               Shift key down
        EventMask.CAPS_LOCK           Caps lock key down
        EventMask.CONTROL             Control key down
        EventMask.L_ALT               Left Alt key down
        EventMask.NUM_LOCK            Num lock key down
        EventMask.MOUSE_BUTTON_1      Right mouse button down
        EventMask.MOUSE_BUTTON_2      Mouse wheel down
        EventMask.MOUSE_BUTTON_3      Left mouse button down
        ============================  ========================

    """
    SHIFT = 0x0001
    CAPS_LOCK = 0x0002
    CONTROL = 0x0004
    L_ALT = 0x0008
    NUM_LOCK = 0x0010
    R_ALT = 0x0080
    MOUSE_BUTTON_1 = 0x0100
    MOUSE_BUTTON_2 = 0x0200
    MOUSE_BUTTON_3 = 0x0400


def chain(func):
    """
    Decorator function that allows class methods to be chained by implicitly returning the object. Any method
    decorated with this function returns its object.

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        func(self, *args, **kwargs)
        return self

    return wrap


def clean_styles(widget, styles) -> dict:
    """
    Ensures safety while passing styles to tkinter objects. Normally tkinter objects raise errors for declaring
    styles that are not allowed for a given widget. This function takes in the styles dictionary and removes
    invalid styles for the particular widget returning the cleaned styles dictionary. As a bonus, duplicate definitions
    are overwritten.

    :param widget:
    :param styles:
    :return: dict cleaned_styles
    """
    allowed_styles = widget.config() or {}
    cleaned_styles = {}
    for style in styles:
        if style in allowed_styles:
            cleaned_styles[style] = styles[style]
    return cleaned_styles


class DragWindow(tk.Toplevel):

    def __init__(self, master, **cnf):
        super().__init__(master, **cnf)
        self.window = self
        self.pos = (0, 0)
        self.overrideredirect(True)
        self.attributes("-alpha", 0.6)  # Default transparency
        if platform_is(MAC):
            # needed for macos to make window visible
            self.lift()

    def get_center(self):
        w, h, = self.winfo_width(), self.winfo_height()
        return self.pos[0] + int(w / 2), self.pos[1] + int(h / 2)

    def set_geometry(self, rec):
        self.geometry("{}x{}+{}+{}".format(*rec))
        return self

    def set_position(self, x, y):
        self.geometry(f"+{x}+{y}")
        self.pos = x, y
        return self

    def move(self, delta_x, delta_y):
        self.pos = (self.pos[0] + delta_x, self.pos[1] + delta_y)
        self.set_position(*self.pos)

    def set_transparency(self, alpha):
        self.attributes("-alpha", float(alpha))


class WidgetTree:
    @staticmethod
    def ancestor_first(start_from, class_: type, ignore=None):
        """
        Gets the first widget belonging to `class\\_` starting from `start_from`. This widget
        may be the top widget or it's parents and grandparents deep down the hierarchy.
        Useful when you want to access a widget's first ancestor of a given type
        down the stacking order

        :param start_from: widget whose ancestor is to be determined
        :param class_: the class of the widget we are interested in
        :param ignore: widget to be ignored if any
        :return: the first widget belonging to `class\\_`, if no widget is found None is returned
        """
        check = start_from.nametowidget(start_from.winfo_parent())
        while not isinstance(check, tk.Tk) and check is not None:
            if isinstance(check, class_) and check != ignore:
                return check
            check = check.nametowidget(check.winfo_parent())  # noqa

    @staticmethod
    def containing(x, y, widget):
        """
        A safer alternative for tk winfo_containing that does extra checks
        just in case the widget at the target position is not recognized
        or managed by our tk instance

        :param x: x coordinate
        :param y: y coordinate
        :param widget: widget to be checked.
        :return: name of widget at position
        """
        try:
            return widget.winfo_containing(x, y)
        except KeyError:
            # thrown when widget at position is not managed by our tk instance
            return None

    @staticmethod
    def event_in(event, widget):
        """
        Check whether event has occurred within a widget

        :param event: event object containing position data
        :param widget: the widget to be checked
        :return: True if event occurred in within widget else False
        """
        x, y = event.x_root, event.y_root
        x1, y1, x2, y2 = (
            widget.winfo_rootx(),
            widget.winfo_rooty(),
            widget.winfo_rootx() + widget.winfo_width(),
            widget.winfo_rooty() + widget.winfo_height(),
        )
        return x1 < x < x2 and y1 < y < y2

    @staticmethod
    def event_first(event, widget, class_: type, ignore=None):
        """
        Gets the first widget belonging to `class\\_` at the event position. This widget
        may be the top widget or it's parents and grandparents deep down the hierarchy.
        Useful when you want to ignore widgets and cascade the event to a specific lower
        level widget.

        :param event: a tk event object containing the position data
        :param widget: any widget preferably the toplevel widget
        :param class_: the class of the widget we are interested in
        :param ignore: widget to be ignored if any
        :return: the first widget belonging to `class\\_`, if no widget is found None is returned
        """
        check = WidgetTree.containing(event.x_root, event.y_root, widget)
        while not isinstance(check, tk.Tk) and check is not None:
            if isinstance(check, class_) and check != ignore:
                return check
            check = check.nametowidget(check.winfo_parent())  # noqa
        return None
