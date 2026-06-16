import functools
import tkinter as tk
from typing import Union

from ivh.utils.platform import platform_is, MAC, LINUX, WINDOWS


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


def config_all(widget, **styles):
    widget.configure(**clean_styles(widget, styles))
    for child in widget.winfo_children():
        config_all(child, **styles)


def bind_all(widget, *args, **kwargs):
    widget.bind(*args, **kwargs)
    for child in widget.winfo_children():
        bind_all(child, *args, **kwargs)


def disable_all(widget: tk.Widget, flag: bool):
    config = {"state": tk.DISABLED} if not flag else {"state": tk.NORMAL}
    if "state" in widget.keys():
        widget.configure(**config)
    for child in widget.winfo_children():
        disable_all(child, flag)


def clear_children(widget):
    for child in widget.winfo_children():
        child.pack_forget()
        child.grid_forget()
        child.place_forget()


def center_window(window, master=None):
    if platform_is(WINDOWS):
        window.withdraw()
    if master is None:
        window.update_idletasks()
        width = window.winfo_screenwidth()
        height = window.winfo_screenheight()
        x, y = 0, 0
    else:
        master.update_idletasks()
        width = master.winfo_width()
        height = master.winfo_height()
        x, y = master.winfo_x(), master.winfo_y()
    # window.update_idletasks()
    sub_width = window.winfo_width()
    sub_height = window.winfo_height()
    window.geometry(f"+{x + (width - sub_width) // 2}+{y + (height - sub_height) // 2}")
    if platform_is(WINDOWS):
        window.deiconify()


class EmptyScreen(tk.Label):

    def __init__(self, master, **kwargs):
        if "fg" not in kwargs:
            kwargs["fg"] = "#aaaaaa"
        if "compound" not in kwargs:
            kwargs["compound"] = tk.TOP
        super().__init__(master, **kwargs)

    def show(self, **kwargs):
        self.config(**kwargs)
        self.lift()
        self.place(x=0, y=0, relwidth=1, relheight=1)

    def hide(self):
        self.place_forget()


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


class Popup(tk.Toplevel):

    def __init__(self, master, pos=None, **cnf):
        super().__init__(master, **cnf)
        if pos is not None:
            self.set_geometry(pos)
        self._close_func = None
        self.overrideredirect(True)
        self.attributes("-topmost", 1)
        if platform_is(MAC):
            # needed for proper positioning in mac
            self.lift(master)
        self._grabbed = self.grab_current()  # Store the widget that currently has the grab
        # Grab all events so we can tell whether someone is clicking outside the popup
        self.bind("<Visibility>", self._on_visibility)
        self.bind("<Button-1>", self._exit)
        self.body = self

    def _on_visibility(self, _):
        self.grab_set_global()

    def _exit(self, event):
        if not WidgetTree.event_in(event, self):
            # Someone has clicked outside the popup so close it
            self.destroy()

    @chain
    def set_geometry(self, rec):
        x, y, width, height = rec if len(rec) == 4 else rec + (None, None)
        try:
            if width is None:
                self.geometry("+{}+{}".format(x, y))
            else:
                self.geometry("{}x{}+{}+{}".format(width, height, x, y))
        except tk.TclError:
            pass

    def hide(self):
        self.attributes("-alpha", 0)

    def show(self):
        self.attributes("-alpha", 1)

    def destroy(self):
        self.grab_release()
        if self._grabbed:
            try:
                self._grabbed.grab_set()  # Return the grab to whichever widget had it if any
            except tk.TclError:
                pass
        super().destroy()
        if self._close_func is not None:
            self._close_func()

    def re_calibrate(self):
        pass

    def on_close(self, func, *args, **kwargs):
        self._close_func = lambda: func(*args, **kwargs)

    def get_pos(self, widget, **kwargs):
        """
        Get the position of a popup window anchored around a widget

        :param widget: A tk widget to be used as an anchor point
        :param kwargs:
            -side: a string value "nw", "ne", "sw", "se", "auto" representing where the
              dialog is to be position relative the anchor widget
            -padding: an integer indicating how much space to allow between the popup and the
              anchor widget
            -width: prospected width of the popup which can be used even before the
              popup is initialized by tkinter. If not provided its obtained
              from the popup hence the popup must have been initialized by tkinter
            -height: prospected height of the popup. Same rules on ``width``
              apply here

        :return: None
        """
        side = kwargs.get("side", "auto")
        padding = kwargs.get("padding", 2)
        if "width" in kwargs and "height" in kwargs:
            w_width = kwargs.get("width")
            w_height = kwargs.get("height")
        else:
            self.re_calibrate()
            self.update_idletasks()
            w_width = self.winfo_width()
            w_height = self.winfo_height()
        widget.update_idletasks()
        x, y, width, height = widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_width(), widget.winfo_height()
        right = x
        left = x - w_width + width
        top = y - w_height - padding
        bottom = y + height + padding
        if side == "nw":
            return left, top
        if side == "ne":
            return right, top
        if side == "sw":
            return left, bottom
        if side == "se":
            return right, bottom
        # i.e. side == "auto"
        # set the screen size as the boundary
        win_bounds = 0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight()
        offset_b = win_bounds[3] - bottom
        offset_t = y - win_bounds[1]
        offset_l = x - win_bounds[0]
        offset_r = win_bounds[2] - right
        x_pos = left if offset_l >= offset_r or offset_l > w_width else right
        y_pos = bottom if offset_b >= offset_t or offset_b > w_height else top
        return x_pos, y_pos

    def post(self, widget, **kwargs):
        """
        Display a popup window anchored around a widget

        :param widget: A tk widget to be used as an anchor point
        :param kwargs:
            -side: a string value "nw", "ne", "sw", "se", "auto" representing where the
              dialog is to be position relative the anchor widget
            -padding: an integer indicating how much space to allow between the popup and the
              anchor widget
            -width: prospected width of the popup which can be used even before the
              popup is initialized by tkinter. If not provided its obtained
              from the popup hence the popup must have been initialized by tkinter
            -height: prospected height of the popup. Same rules on ``width``
              apply here

        :return: None
        """
        self.set_geometry(self.get_pos(widget, **kwargs))


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
    def event_first(event, widget, class_: type | tuple[type, ...], ignore=None):
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


class DraggableMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allow_drag = False
        self._drag_setup = False

    @property
    def allow_drag(self):
        """
        Determines whether widgets can be dragged in-case of a drag drop event
        """
        return self._allow_drag

    @allow_drag.setter
    def allow_drag(self: Union['tk.Misc', 'DraggableMixin'], flag: bool):
        """
        Call this method to make the widget allow or disallow drag and drop

        :param flag: set to True to allow drag drop and False to disallow
        """
        self._allow_drag = flag
        if self._allow_drag and not self._drag_setup:
            bind_all(self, '<Motion>', self._drag_handler)
            bind_all(self, '<ButtonRelease-1>', self._drag_handler)
            self._drag_setup = True

    @property
    def window(self: tk.Misc):
        window = self.winfo_toplevel()
        if not hasattr(window, 'drag_window'):
            window.drag_window = None
        return window

    def _drag_handler(self, event):
        """
        Handle drag drop events
        :param event: tk event
        """
        if not self.allow_drag:
            return
        if event.type.value == "6":
            # Event is of Motion type
            if event.state & EventMask.MOUSE_BUTTON_1 and self.window.drag_window is None:
                self.window.drag_context = self
                self.window.drag_window = DragWindow(self.window)
                self.render_drag(self.window.drag_window)
                self.window.drag_pos = event.x_root, event.y_root
                self.window.drag_window.set_position(*self.drag_start_pos(event))
                self.on_drag_start(event)
            elif self.window.drag_window is not None:
                x, y = self.window.drag_pos
                delta_x, delta_y = event.x_root - x, event.y_root - y
                self.window.drag_window.move(delta_x, delta_y)
                self.window.drag_pos = event.x_root, event.y_root
                self.on_drag(event)
        elif event.type.value == "5":
            # Event is of Button release type so end drag
            if self.window.drag_window:
                # sometimes the window handle changes when
                # wm_manage/wm_forget is called on the on_drag_end method,
                # so we need to keep a reference to the drag window
                window = self.window
                try:
                    self.on_drag_end(event)
                finally:
                    window.drag_window.destroy()
                    window.drag_window = None
                    # Get the first widget at release position that supports drag manager and pass the context to it
                    event_position = WidgetTree.event_first(event, self, DraggableMixin)
                    if isinstance(event_position, DraggableMixin):
                        event_position.accept_context(window.drag_context)
                    window.drag_context = None

    def accept_context(self, context):
        """
        This method is called when a drag drop operation is completed to allow the dropped object to be handled

        :param context: Object being dropped at the widget
        """
        pass

    def render_drag(self, window):
        """
        Override this method to create and position widgets on the drag shadow window (The object displayed
        as the widget is dragged around). Create your custom widget hierarchy and position
        it in window.

        :param window: The drag window provided by the drag manager that should be used as the widget master
        :return: None
        """
        tk.Label(window, text="Item", bg="#f7f7f7").pack()  # Default render

    def on_drag_start(self, *args):
        """
        Called whe the widget is first dragged
        """
        pass

    def on_drag_end(self, event):
        """
        Called when widget is dropped and dragging ends
        """
        pass

    def on_drag(self, event):
        """
        Called when widget is dragged. This is called on each motion event so
        it's best to keep computation in this function at a minimum
        """
        pass

    def drag_start_pos(self: tk.Misc, event):
        """
        Override and return the preferred drag start position as a tuple (x, y).
        Default is the current widget position
        """
        return event.x_root + 2, event.y_root + 2


class ScrollableInterface:
    """
    Interface that allows widgets to be managed by the _MouseWheelDispatcherMixin which handles mousewheel
    events which may be tricky to handle at the widget level.
    """

    def on_mousewheel(self, event):
        raise NotImplementedError("on_mousewheel method is required")

    def handle_wheel(self, widget, event):
        # perform cross platform mousewheel handling
        delta = 0
        if platform_is(LINUX):
            delta = 1 if event.num == 5 else -1
        elif platform_is(MAC):
            # For mac delta remains unmodified
            delta = -1 * event.delta
        elif platform_is(WINDOWS):
            delta = -1 * (event.delta // 120)

        if event.state & EventMask.CONTROL:
            # scroll horizontally when control is held down
            widget.xview_scroll(delta, "units")
        else:
            widget.yview_scroll(delta, "units")

    def scroll_position(self):
        # Return the scroll position to determine if we have reach the end of scroll so we can
        # pass the scrolling to the next widget under the cursor that can scroll
        raise NotImplementedError("Scroll position required for scroll transfer")

    def scroll_transfer(self) -> bool:
        # Override this method and return true to allow scroll transfers
        return False


class MouseWheelDispatcher:
    """
    Dispatches mousewheel events to the right scrolledFrame. The mousewheel event is bound to the main window
    then the event is processed by this mixin though widget resolution techniques to determine if there is any
    scrolled frame at the scroll position
    """

    @staticmethod
    def _on_mousewheel(widget, event):
        # Resolve the widget under the cursor to determine if there is any scrollable widget (ScrollableInterface)
        # If any pass the event to it
        check = WidgetTree.containing(event.x_root, event.y_root, widget)
        while not isinstance(check, tk.Tk) and check is not None:
            if isinstance(check, ScrollableInterface):
                if check.scroll_transfer() and check.scroll_position()[0] < 1:
                    # Perform scroll transfer by ignoring this widget and checking the next
                    continue
                check.on_mousewheel(event)
                break
            check = check.nametowidget(check.winfo_parent())

    @staticmethod
    def set_up_mousewheel(widget):
        widget.bind_all("<MouseWheel>", lambda e: MouseWheelDispatcher._on_mousewheel(widget, e), '+')
        # linux bindings
        widget.bind_all("<Button-4>", lambda e: MouseWheelDispatcher._on_mousewheel(widget, e), '+')
        widget.bind_all("<Button-5>", lambda e: MouseWheelDispatcher._on_mousewheel(widget, e), '+')
