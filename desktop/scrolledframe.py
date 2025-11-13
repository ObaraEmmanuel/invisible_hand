from tkinter import ttk, Frame
import tkinter as tk
import time

from ui_utils import ScrollableInterface


class ScrolledFrame(tk.Frame, ScrollableInterface):

    def __init__(self, master=None, **cnf):
        super().__init__(master, **cnf)
        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._canvas.config(cnf)
        self._canvas.config()
        self._scroll_y = ttk.Scrollbar(self, orient='vertical', command=self._limit_y)  # use frame limiters
        self._scroll_x = ttk.Scrollbar(self, orient='horizontal', command=self._limit_x)
        self._canvas.grid(row=0, column=0, sticky='nswe')
        self.columnconfigure(0, weight=1)  # Ensure the _canvas gets the rest of the left horizontal space
        self.rowconfigure(0, weight=1)  # Ensure the _canvas gets the rest of the left vertical space
        self._canvas.config(yscrollcommand=self._scroll_y.set, xscrollcommand=self._scroll_x.set)  # attach scrollbars
        self.body = Frame(self._canvas, **cnf)
        self._window = self._canvas.create_window(0, 0, anchor='nw', window=self.body)
        self._scrollbar_flag = tk.Y  # Enable vertical scrollbar by default
        # self.after(200, self.on_configure)
        self._limit_var = [0, 0]  # limit var for x and y
        self._max_frame_skip = 3
        self._last_render = time.perf_counter_ns()
        self.fill_x = True  # Set to True to disable the x scrollbar and fit content to width
        self.fill_y = False  # Set to True to disable the y scrollbar and fit content to height
        self._prev_region = (0, 0, 0, 0)
        self._prev_dimension = (0, 0)
        self._detect_change()

    def _show_y_scroll(self, flag):
        if flag and not self._scroll_y.winfo_ismapped():
            self._scroll_y.grid(row=0, column=1, sticky='ns')
        elif not flag:
            self._scroll_y.grid_forget()
        self.update_idletasks()

    def _show_x_scroll(self, flag):
        if flag and not self._scroll_x.winfo_ismapped():
            self._scroll_x.grid(row=1, column=0, sticky='ew')
        elif not flag:
            self._scroll_x.grid_forget()
        self.update_idletasks()

    def _limiter(self, callback, axis, *args):
        # Frame limiting reduces lags while scrolling by skipping a number of scroll events to reduce the burden
        # of performing expensive redrawing by tkinter
        render_time = time.perf_counter_ns()
        render_diff = render_time - self._last_render
        self._last_render = render_time

        # Max human click rate is about 15 CPS = 70ms/click
        # Always render if it's been longer than 70ms since last render
        if self._limit_var[axis] == self._max_frame_skip or render_diff > 7e7:
            callback(*args)
            self._limit_var[axis] = 0
        else:
            self._limit_var[axis] += 1
        self._canvas.update_idletasks()
        self.body.update_idletasks()
        self.update_idletasks()

    def _limit_y(self, *scroll):
        self._limiter(self._canvas.yview, 1, *scroll)

    def _limit_x(self, *scroll):
        self._limiter(self._canvas.xview, 0, *scroll)

    def on_configure(self, *_):
        try:
            self._canvas.update_idletasks()
            self.body.update_idletasks()
            scroll_region = self._canvas.bbox("all")
        except tk.TclError:
            return

        dimension = (self._canvas.winfo_width(), self._canvas.winfo_height())
        if scroll_region == self._prev_region and dimension == self._prev_dimension:
            # Size has not necessarily changed so changes needed, break execution
            return
        self._prev_dimension = dimension
        self._prev_region = scroll_region

        if self.fill_y:
            # No vertical scrollbars needed
            self._canvas.itemconfigure(self._window, height=self._canvas.winfo_height())
        elif scroll_region[3] - scroll_region[1] > self._canvas.winfo_height():
            # Canvas content occupies more height than body's height so vertical scrollbars are needed
            self._show_y_scroll(True)
        else:
            # vertical scrollbars not needed, remove them
            self._show_y_scroll(False)

        if self.fill_x:
            # No horizontal scrollbars needed
            self._canvas.itemconfigure(self._window, width=self._canvas.winfo_width())
        elif scroll_region[2] - scroll_region[0] > self._canvas.winfo_width():
            # Canvas content occupies more width than body's height so horizontal scrollbars are needed
            self._show_x_scroll(True)
        else:
            # Horizontal scrollbars not needed, remove them
            self._show_x_scroll(False)

        # adjust scroll-region of the canvas to cover the contents
        self._canvas.config(scrollregion=scroll_region)

    def clear_children(self):
        # Unmap all children from the frame
        for child in self.body.winfo_children():
            if hasattr(child, "pack_forget"):
                child.pack_forget()

    def _detect_change(self, flag=True):
        # Lets set up the frame to listen to changes in size and update the scrollbars
        if flag:
            self.body.bind('<Configure>', self.on_configure)  # Changes in internal content
            self.bind('<Configure>', self.on_configure)  # Changes in the containing parent frame
        else:
            self.unbind('<Configure>')
            self.body.unbind('<Configure>')

    def on_mousewheel(self, event):
        # Enable the scrollbar to be scrolled using mouse wheel
        # Occasionally throws unpredictable errors so we better wrap it up in a try block
        try:
            if event.state & 0x4 and self._scroll_x.winfo_ismapped():
                self.handle_wheel(self._canvas, event)
            elif self._scroll_y.winfo_ismapped():
                self.handle_wheel(self._canvas, event)
        except tk.TclError:
            pass

    def scroll_position(self):
        return self._scroll_y.get()

    def set_scrollbars(self, flag):
        """
        :param flag: set to tkinter.X to enable horizontal scrollbar, tkinter.Y to enable vertical scrollbar,
          tkinter.BOTH to enable both scrollbars and None to disable all scrollbars. The default is tkinter.Y for
          the vertical scrollbar.
        :return: None
        """
        self._scrollbar_flag = flag

    def content_height(self):
        self._canvas.update_idletasks()
        bbox = self._canvas.bbox('all')
        return bbox[3] - bbox[1] + 3

    def scroll_to_start(self):
        self._canvas.yview_moveto(0.0)
        self._canvas.xview_moveto(0.0)

    def scroll_to(self, widget):
        self._canvas.update_idletasks()
        widget.update_idletasks()
        bbox = self._canvas.bbox('all')

        if self._scroll_x.winfo_ismapped():
            r_x = self._canvas.winfo_rootx()
            w_x = widget.winfo_rootx()
            w = bbox[2] - bbox[0]
            x_off = self._canvas.xview()[0] * w
            x = w_x - r_x + x_off
            self._canvas.xview_moveto(x / w)

        if self._scroll_y.winfo_ismapped():
            r_y = self._canvas.winfo_rooty()
            w_y = widget.winfo_rooty()
            h = bbox[3] - bbox[1]
            y_off = self._canvas.yview()[0] * h
            y = w_y - r_y + y_off
            self._canvas.yview_moveto(y / h)

    def xview_scroll(self, n, what):
        return self._canvas.xview_scroll(n, what)

    def yview_scroll(self, n, what):
        return self._canvas.yview_scroll(n, what)

    def xview_moveto(self, fraction):
        return self._canvas.xview_moveto(fraction)

    def yview_moveto(self, fraction):
        return self._canvas.yview_moveto(fraction)

    def scroll_transfer(self) -> bool:
        # Override this method and return true to allow scroll transfers
        return False
