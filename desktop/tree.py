import enum
import tkinter as tk
from tkinter import Frame, Label, PhotoImage

from geometry import absolute_bounds, upscale_bounds, bounds
from highlight import EdgeIndicator
from scrolledframe import ScrolledFrame
from ui_utils import chain, EventMask, DragWindow, WidgetTree


class Tree:
    """
    Tree Abstraction for management of tree_views and similar
    tree-like widgets in hoverset. To use this class, subclass it and
    implement the :py:meth:`Tree.get_body` method to specify the container widget.

    .. note::
        Remember to call :py:meth:`Tree.initialize_tree` in your constructor before
        performing any operations on the tree.
    """

    class Strip(Frame):
        """
        An interface for event binding to tree view items
        """

        def __init__(self, master=None, **config):
            super().__init__(master, **config)
            self.parent_node: TreeView = master

        def select(self):
            self.parent_node.select()

        def deselect(self):
            self.parent_node.deselect()

        def config_all(self, **kw):
            pass

    class Node(Frame):
        # will be loaded later
        EXPANDED_ICON = None
        COLLAPSED_ICON = None
        BLANK = None
        __icons_loaded = False
        PADDING = 1

        def __init__(self, tree, **config):
            super().__init__(tree.get_body())
            self._load_images()
            self.tree = tree
            self._icon = config.get("icon", self.BLANK)
            self._name = config.get("name", "unknown")
            self.strip = f = TreeView.Strip(self, takefocus=True)
            f.pack(side="top", fill="x")
            self._spacer = Frame(f, width=0)
            self._spacer.grid(row=0, column=0)
            self.expander = Label(f, compound=tk.TOP, image=self.BLANK)
            self.expander.grid(row=0, column=1)
            self.expander.bind("<Button-1>", self.toggle)
            self.icon_pad = Label(f, image=self._icon)
            self.icon_pad.grid(row=0, column=2)
            self.name_pad = Label(f, text=self._name)
            self.name_pad.grid(row=0, column=3)
            f.columnconfigure(3, uniform=1)
            self.body = Frame(self)
            self.body.pack(side="top", fill="x")
            self._visible = True
            self._expanded = False
            self._selected = False
            self._depth = 0  # Will be set on addition to a node or tree so this value is just placeholder
            self.parent_node = None
            self.nodes = []

        def _init_binding(self):
            for i in (self.name_pad, self.strip, *self.strip.winfo_children()):
                i.bind("<ButtonRelease-1>", self.select)
                i.bind("<Return>", self.select)

        def _load_images(self):
            if self.__icons_loaded:
                return
            cls = self.__class__
            cls.EXPANDED_ICON = PhotoImage(file="resources/collapse.png")
            cls.COLLAPSED_ICON = PhotoImage(file="resources/expand.png")
            cls.BLANK = PhotoImage(file="resources/blank.png")
            cls.__icons_loaded = True

        @property
        def selected(self):
            return self._selected

        @property
        def depth(self):
            return self._depth

        @depth.setter
        def depth(self, value):
            self._depth = value
            self._spacer["width"] = 30 * (value - 1) + 1  # width cannot be set to completely 0 so add 1 just in case
            # Update depth even for the children
            for node in self.nodes:
                node.depth = self._depth + 1

        @property
        def name(self):
            return self.name_pad["text"]

        def bind_all(self, sequence=None, func=None, add=None):
            # The strip is pretty much the handle for the Node so better bind events here
            self.strip.bind(sequence, func, add)
            for child in self.strip.winfo_children():
                child.bind(sequence, func, add)

        def _set_expander(self, icon):
            if icon:
                self.expander.configure(image=icon)
            else:
                self.expander.configure(image=self.BLANK)

        def is_descendant(self, node):
            if node.depth >= self.depth:
                return False
            parent = self.parent_node
            while parent is not None:
                if parent == node:
                    return True
                parent = parent.parent_node
            return False

        def select(self, event=None, silently=False):
            if event and event.state & EventMask.CONTROL:
                self.tree.toggle_from_selection(self)
                return
            if event:
                self.tree.select(self)
            else:
                self.tree.add_to_selection(self, silently)

            self._selected = True

        def deselect(self, *_):
            self._selected = False

        def index(self):
            return self.parent_node.nodes.index(self)

        def toggle_select(self, event):
            if self._selected:
                self.deselect(event)
            else:
                self.select(event)

        @chain  # This just makes the method returns the object instance to allow method chaining
        def add(self, node):
            if self.is_descendant(node) or node == self:
                # You cannot add a node to its descendant/ child or itself
                return
            self.nodes.append(node)
            node.parent_node = self
            node.depth = self.depth + 1
            node.lift(self.body)
            if self._expanded:
                node.pack(in_=self.body, fill="x", side="top", pady=self.PADDING)
            else:
                self._set_expander(self.COLLAPSED_ICON)

        def insert_after(self, *nodes):
            """
            Insert the nodes immediately after this node in the same parent

            :param nodes: List of nodes to be inserted
            """
            self.parent_node.insert(self.parent_node.nodes.index(self) + 1, *nodes)

        def insert_before(self, *nodes):
            """
            Insert the nodes immediately before this node in the same parent

            :param nodes: List of nodes to be inserted
            """
            self.parent_node.insert(self.index(), *nodes)

        def insert(self, index=None, *nodes):
            """
            Insert all child nodes passed into parent node starting from the given index

            :param index: int representing the index from which to insert
            :param nodes: Child nodes to be inserted
            """
            # If no index is provided we assume we are appending
            index = len(self.nodes) if index is None else index
            for node in nodes:
                if self.is_descendant(node) or node == self:
                    # You cannot add a node to its descendant/ child or itself
                    continue
                node.remove()  # Remove node from whatever parent it belongs to
                self.nodes.insert(index, node)
                index += 1
                node.parent_node = self
                node.depth = self.depth + 1
                node.lift(self.body)
            if self._expanded:
                self.collapse()
                self.expand()
            if len(self.nodes) > 0:
                self._set_expander(self.COLLAPSED_ICON)
                self.expand()

        def add_as_node(self, **options):
            """
            Adds a node to the tree view.

            :param options: Options used in creating the node like name, icon e.t.c. depending on the Node
            :return: The created Node
            """
            # Create an object belonging to the same Node family as self
            # This allows sub-classes of TreeView to implement their own nodes.
            # By default self.__class__ will be equivalent to TreeView.Node but could change with subclasses
            node = self.__class__(self.tree, **options)
            node.parent_node = self
            node.depth = self.depth + 1
            self.add(node)
            return node

        def remove(self, node=None):
            """
            Remove the node from node's child nodes. If node is not provided the the node removes itself from
            its parent

            :param node: Node to be removed (optional)
            :return: None
            """
            if node is None:
                self.parent_node.remove(self)
            elif node in self.nodes:
                # We need a local copy of the expanded flag since calling collapse resets
                was_expanded = self._expanded
                # Collapse parent so that layout changes caused by removal of a node can be applied
                self.collapse()
                self.nodes.remove(node)
                node.pack_forget()
                if was_expanded and len(self.nodes) > 0:
                    # If the parent was expanded when we began removal we expand it again
                    self.expand()
                if not self.nodes:
                    # remove the expansion icon
                    self._set_expander(self.BLANK)

        def expand(self):
            if self._expanded or not self.nodes:
                return
            self.pack_propagate(True)
            for node in filter(lambda n: n._visible, self.nodes):
                node.pack(in_=self.body, fill="x", side="top", pady=self.PADDING)
            self._set_expander(self.EXPANDED_ICON)
            self._expanded = True

        def collapse(self):
            if not self._expanded:
                return
            for node in self.nodes:
                node.pack_forget()
            self.pack_propagate(False)
            self.config(height=self.strip.winfo_height())
            self._set_expander(self.COLLAPSED_ICON)
            self._expanded = False

        def expand_all(self):
            # Expand all nodes recursively
            self.expand()
            for node in self.nodes:
                node.expand_all()

        def collapse_all(self):
            # Collapse all nodes recursively
            self.collapse()
            for node in self.nodes:
                node.collapse_all()

        def toggle(self, *_):
            """
            Toggle between the expanded and collapsed state
            """
            if self._expanded:
                self.collapse()
            else:
                self.expand()

        def clear(self):
            nodes = list(self.nodes)
            for node in nodes:
                self.remove(node)

        def search(self, query):
            match = False
            self.collapse()
            if not query:
                # empty query is used to end search
                # remove all nodes so they can be reconstructed in right order
                for node in self.nodes:
                    node.pack_forget()

            for node in self.nodes:
                if node.search(query):
                    node.pack(in_=self.body, fill="x", side="top", pady=self.PADDING)
                    node._visible = True
                    match = True
                else:
                    node.pack_forget()
                    node._visible = False

            if not match:
                self._set_expander(self.BLANK)
            else:
                self.expand()
            return match or (query.lower() in self.name_pad["text"].lower())

    # =========================== Tree =================================

    def get_body(self):
        """
        Return the tkinter container like a Frame where the nodes are
        packed. This method must be implemented and must return a valid
        container.
        """
        raise NotImplementedError()

    def initialize_tree(self):
        """
        Initialize tree properties. Make sure its called before any
        operations are performed on the tree.
        """
        if getattr(self, "_has_tree_init", False):
            # safety to ensure tree is not initialized twice
            return
        self._selected = []
        self.nodes = []
        self._multi_select = False
        self._on_select = None
        self._depth = 0
        self._parent_node = None  # This value should never be changed
        self._has_tree_init = True
        self._visible = True

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value):
        self._depth = value

    @property
    def parent_node(self) -> None:
        # We prevent anyone from altering the parent_node value
        # The parent node for a tree is always None
        return self._parent_node

    def select(self, n, silently=False):
        """
        Select a node :param n and deselect all other selected nodes

        :param silently: Flag set to true to prevent firing on change event and vice versa. Default is false
        :param n: Node to be selected
        """
        for node in self._selected:
            node.deselect()
        self._selected = [n]
        if not silently:
            self.selection_changed()

    def clear_selection(self):
        """
        Deselect all currently selected nodes
        """
        for node in self._selected:
            node.deselect()
        self._selected = []
        self.selection_changed()

    def get(self):
        """
        Get the currently selected node if multi select is set to False and a list of all selected items if multi
        select is set to True. Returns None if no item is selected.

        :return: Selected widget or None if no widget is selected
        """
        if self._multi_select:
            return self._selected
        if self._selected:
            return self._selected[0]
        return None

    def add_to_selection(self, node, silently=False):
        if not self._multi_select:
            # We are not in multi select mode so select one node at a time
            self.select(node)
        else:
            # Append node without affecting the other selected nodes
            self._selected.append(node)
            if not silently:
                self.selection_changed()

    def toggle_from_selection(self, node):
        if not self._multi_select:
            return
        if node in self._selected:
            self.deselect(node)
            self.selection_changed()
        else:
            node.select()

    def deselect(self, node):
        if node in self._selected:
            self._selected.remove(node)
        node.deselect()

    def add(self, node):
        """
        Add an already created node to the tree view. Use add_as_node instead to avoid tkinter parent
        issues.

        :param node: The child Node to be added to the Node
        """
        self.nodes.append(node)
        node.parent_node = self
        node.depth = self.depth + 1
        node.pack(side="top", fill="x", in_=self.get_body(), pady=self.__class__.Node.PADDING)

    def add_as_node(self, **options) -> Node:
        """
        Adds a base node to the Tree. The node will belong to a subclass' Node definition if any.

        :param options: Options used in creating the node like name, icon e.t.c.
        :return: The created Node
        """
        # Use the Node definition of the object
        node = self.__class__.Node(self, **options)
        self.add(node)
        node.parent_node = self
        node.depth = self.depth + 1
        return node

    def allow_multi_select(self, flag):
        """
        Allow or disallow multiple widgets to be selected

        :param flag: Set to True to allow multiple items to be selected by the tree view and false to disable
          selection of multiple items.
        """
        self._multi_select = flag

    def remove(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            node.pack_forget()

    def clear(self):
        nodes = list(self.nodes)
        for node in nodes:
            self.remove(node)

    def redraw(self):
        for node in self.nodes:
            node.pack_forget()
        for node in filter(lambda n: n._visible, self.nodes):
            node.pack(side="top", fill="x", in_=self.get_body(), pady=self.__class__.Node.PADDING)

    def insert(self, index=None, *nodes):
        if index is None:
            index = len(self.nodes)
        for node in nodes:
            node.remove()  # Remove node from whatever parent it belongs to
            self.nodes.insert(index, node)
            index += 1
            node.parent_node = self
            node.depth = self.depth + 1
        self.redraw()

    def on_select(self, listener, *args, **kwargs):
        self._on_select = lambda: listener(*args, **kwargs)

    def selection_changed(self):
        if self._on_select:
            self._on_select()

    def collapse_all(self):
        """
        Collapse all nodes and sub-nodes so that their sub-node are not displayed
        """
        for node in self.nodes:
            node.collapse_all()

    def expand_all(self):
        """
        Expand all nodes and sub-nodes so that their sub-nodes are displayed
        """
        for node in self.nodes:
            node.expand_all()

    def see(self, node):
        """
        Expand all nodes from the root to the given node so that the node is visible

        :param node: The node to be expanded to
        """
        hierarchy = []
        orig_node = node
        while hasattr(node.parent_node, "parent_node"):
            hierarchy.append(node.parent_node)
            node = node.parent_node

        for node in reversed(hierarchy):
            if hasattr(node, "expand"):
                node.expand()

        scrollframe: ScrolledFrame = WidgetTree.ancestor_first(orig_node, ScrolledFrame)
        if scrollframe:
            scrollframe.scroll_to(orig_node)

    def selected_count(self) -> int:
        """
        Return the total number of items currently selected usually 1 if multi-select is disabled.

        :return: total number of items selected
        """
        return len(self._selected)

    def search(self, query):
        match = False
        if not query:
            # empty query is used to end search
            # remove all nodes so they can be reconstructed in right order
            for node in self.nodes:
                node.pack_forget()

        for node in self.nodes:
            if node.search(query):
                node.pack(
                    in_=self.get_body(), fill="x", side="top",
                    pady=self.__class__.Node.PADDING
                )
                node._visible = True
                match = True
            else:
                node.pack_forget()
                node._visible = False
        return match


class TreeView(Tree, ScrolledFrame):
    """
    Custom tree view implementation that is way more flexible for hoverset applications. Can be easily
    modified and works well with hoverset themes.
    """

    def __init__(self, master=None, **config):
        super().__init__(master, **config)
        self.initialize_tree()

    def get_body(self):
        return self.body


class MalleableTree(Tree):
    """
    Abstract Sub class of Tree that allows rearrangement of Nodes which useful in repositioning components in the
    various studio features. For any tree that allows rearrangement, subclass MalleableTree.
    """
    drag_components = []  # All objects that were selected when dragging began
    drag_active = False  # Flag showing whether we are currently dragging stuff
    drag_popup = None  # The almost transparent window that shows what is being dragged
    drag_highlight = None  # The widget that currently contains the rectangular highlight
    drag_select = None  # The node where all events go when button is released ending drag
    drag_display_limit = 3  # The maximum number of items the drag popup can display
    drag_instance = None  # The current tree that is performing a drag

    class Node(Tree.Node):
        PADDING = 0

        class InsertType(enum.IntEnum):

            INSERT_BEFORE = 0
            INSERT_INTO = 1
            INSERT_AFTER = 2

        def __init__(self, tree, **config):
            # Master is always a TreeView object unless you tamper with the add_as_node method
            super().__init__(tree, **config)
            # If set tp False the node accepts children and vice versa
            self._is_terminal = config.get("terminal", True)
            # use add='+' to avoid overriding the default event which selects nodes
            # self.strip.bind_all("<ButtonRelease-1>", self.end_drag)
            # self.strip.config(**self.style.highlight)  # The highlight on a normal day
            self._on_structure_change = None
            # if true allows node to be dragged and repositioned
            self.editable = False
            # if true prevents node from being dragged to another tree
            self.strict_mode = False
            self.configuration = config

        def _bind_widgets(self):
            return self.name_pad, self.strip

        def _init_binding(self):
            ws = self._bind_widgets()
            for i in ws:
                i.bind("<ButtonRelease-1>", self.end_drag)
                i.bind("<Return>", self.select)
                i.bind("<Motion>", self.drag)
                i.bind("<Motion>", self.begin_drag, add='+')

        def on_structure_change(self, callback, *args, **kwargs):
            self._on_structure_change = lambda: callback(*args, **kwargs)

        def _change_structure(self):
            if self._on_structure_change:
                self._on_structure_change()
            self.tree._structure_changed()

        def _edge_scroll(self, event):
            scrolled_parent = WidgetTree.ancestor_first(self, ScrolledFrame)
            if scrolled_parent:
                x1, y1, x2, y2 = absolute_bounds(scrolled_parent)
                overshoot_top, overshoot_bottom = y1 - event.y_root, event.y_root - y2
                if scrolled_parent.scroll_position() != (0, 1):
                    # use -2 to allow a edge margin of about 2
                    if overshoot_top > -2:
                        scrolled_parent.yview_scroll(-1, 'units')
                    elif overshoot_bottom > -2:
                        scrolled_parent.yview_scroll(1, 'units')

        def begin_drag(self, event):
            if not self.editable or not self.tree.selected_count() or not event.state & EventMask.MOUSE_BUTTON_1:
                return
            MalleableTree.drag_active = True

        # noinspection PyProtectedMember
        def drag(self, event):
            if not self.editable or not MalleableTree.drag_active:
                return
            # only initialize if not initialized
            if not MalleableTree.drag_popup:
                MalleableTree.drag_popup = DragWindow(self.winfo_toplevel()).set_position(event.x_root,
                                                                                          event.y_root + 20)
                MalleableTree.drag_components = self.tree._selected
                MalleableTree.drag_instance = self.tree
                count = 0
                for component in MalleableTree.drag_components:
                    # Display all items upto the drag_display_limit
                    if count == MalleableTree.drag_display_limit:
                        overflow = len(MalleableTree.drag_components) - count
                        # Display the overflow information
                        Label(MalleableTree.drag_popup,
                              text=f"and {overflow} other{'' if overflow == 1 else 's'}...", anchor='w',
                              ).pack(side="top", fill="x")
                        break
                    Label(
                        MalleableTree.drag_popup,
                        text=component.name, anchor='w').pack(side="top", fill="x")
                    count += 1
            self._edge_scroll(event)
            widget = WidgetTree.containing(event.x_root, event.y_root, self)
            # The widget can be a child to Node but not necessarily a node but we need a node so
            # Resolve the node that is immediately under the cursor position by iteratively getting widget's parent
            # For the sake of performance not more than 4 iterations
            limit = 4
            while not isinstance(widget, self.__class__):
                if widget is None:
                    # This happens when someone hovers outside the current top level window
                    break
                widget = self.nametowidget(widget.winfo_parent())
                limit -= 1
                if not limit:
                    break
            tree = WidgetTree.event_first(event, self.tree, MalleableTree)

            if isinstance(widget, self.__class__) and (not self.strict_mode or widget.tree == self.tree):
                # We can only react if we have resolved the widget to a compatible Node object
                widget.react(event)
                # Store the currently reacting widget so we can apply actions to it on ButtonRelease/ drag_end
                MalleableTree.drag_select = widget
            elif isinstance(tree, self.tree.__class__) and (not self.strict_mode or tree == self.tree):
                # if the tree found is compatible to the current tree i.e belongs to same class or is subclass of
                # disallow incompatible trees from interacting as this may cause errors
                tree.react(event)
                MalleableTree.drag_select = tree
            else:
                # No viable node found on resolution so clear all highlights and indicators
                if MalleableTree.drag_select:
                    MalleableTree.drag_select.clear_indicators()
                MalleableTree.drag_select = None

            MalleableTree.drag_popup.set_position(event.x_root, event.y_root + 20)

        def end_drag(self, event):
            # Dragging is complete so we make the necessary insertions and repositions
            node = MalleableTree.drag_select
            if MalleableTree.drag_active:
                if MalleableTree.drag_select is not None:
                    action = node.react(event)
                    if action == self.InsertType.INSERT_BEFORE:
                        node.insert_before(*MalleableTree.drag_components)
                    elif action == self.InsertType.INSERT_INTO:
                        node.insert(None, *MalleableTree.drag_components)
                    elif action == self.InsertType.INSERT_AFTER:
                        node.insert_after(*MalleableTree.drag_components)
                    # else there is no viable action to take.
                    if action in [i.value for i in self.InsertType]:
                        # These actions means tree structure changed
                        self._change_structure()
                # Reset all drag related attributes
                if MalleableTree.drag_popup is not None:
                    if MalleableTree.drag_select is not None:
                        MalleableTree.drag_select.clear_indicators()
                    MalleableTree.drag_popup.destroy()  # remove the drag popup window
                    MalleableTree.drag_popup = None
                    MalleableTree.drag_components = []
                    MalleableTree.drag_instance = None
                    self.clear_indicators()
                    MalleableTree.drag_highlight = None
                MalleableTree.drag_active = False
            else:
                self.select(event)

        def highlight(self):
            MalleableTree.drag_highlight = self
            # TODO self.strip.config(**self.style.bright_highlight)

        def react(self, event) -> int:
            # Checks, based on the cursor position whether we can insert before, into or after the node
            # Returns 0, 1 or 2 respectively
            # It is mostly with respect to the nodes head element known as the strip except for --- case * --- below
            self.clear_indicators()
            # The cursor is at the top edge of the node so we can attempt to insert before it
            if event.y_root < self.strip.winfo_rooty() + 5:
                self.tree.edge_indicator.top(upscale_bounds(bounds(self.strip), self))
                return self.InsertType.INSERT_BEFORE
            # The cursor is at the center of the node so we can attempt a direct insert into the node
            if self.strip.winfo_rooty() + 5 < event.y_root < self.strip.winfo_rooty() + self.strip.winfo_reqheight() - 5:
                if not self._is_terminal:
                    # If node is terminal then id does not support children and consequently insertion
                    self.highlight()
                    return self.InsertType.INSERT_INTO
            # The cursor is at the bottom edge of the node so we attempt to insert immediately after the node
            elif self._expanded:  # --- Case * ---
                # If the node is expanded we would want to edge indicate at the very bottom after its last child
                if event.y_root > self.winfo_rooty() + self.winfo_reqheight() - 5:
                    self.tree.edge_indicator.bottom(bounds(self))
                    return self.InsertType.INSERT_AFTER
            else:
                self.tree.edge_indicator.bottom(upscale_bounds(bounds(self.strip), self))
                return self.InsertType.INSERT_AFTER

        def clear_highlight(self):
            # Remove the rectangular highlight around the node
            # TODO self.strip.configure(**self.style.highlight)
            pass

        def clear_indicators(self):
            # Remove any remaining node highlights and edge indicators
            if MalleableTree.drag_highlight is not None:
                MalleableTree.drag_highlight.clear_highlight()
            self.tree.edge_indicator.clear()

        @property
        def is_terminal(self):
            return self._is_terminal

        @is_terminal.setter
        def is_terminal(self, value):
            self._is_terminal = value

        def insert(self, index=None, *nodes):
            # if dragging to new tree copy to new location
            # only do this during drags, i.e drag_active is True
            if MalleableTree.drag_active and MalleableTree.drag_instance != self.tree:
                # clone to new parent tree
                # the node will still be retained in the former tree
                nodes = [node.clone(self.tree) for node in nodes]
                self.clear_indicators()
            super().insert(index, *nodes)
            return nodes

        def clone(self, parent):
            #  Generic cloning that replicates node using config provided on creation
            #  Override to define attributes that may have changed
            node = self.__class__(parent, **self.configuration)
            node.parent_node = self.parent_node
            for sub_node in self.nodes:
                sub_node_clone = sub_node.clone(parent)
                node.insert(None, sub_node_clone)
            return node

    def initialize_tree(self):
        super(MalleableTree, self).initialize_tree()
        self._on_structure_change = None
        self.is_terminal = False
        self.edge_indicator = EdgeIndicator(self.get_body())  # A line that shows where an insertion can occur

    def on_structure_change(self, callback, *args, **kwargs):
        self._on_structure_change = lambda: callback(*args, **kwargs)

    def _structure_changed(self):
        if self._on_structure_change:
            self._on_structure_change()

    def insert(self, index=None, *nodes):
        # if dragging to new tree clone nodes to new location
        # only do this during drags, i.e drag_active is True
        if MalleableTree.drag_active and MalleableTree.drag_instance != self:
            # clone to new parent tree
            # the node will still be retained in the former tree
            nodes = [node.clone(self) for node in nodes]
            self.edge_indicator.clear()
        super().insert(index, *nodes)
        # Return the nodes just in case they have been cloned and new references are required
        return nodes

    def react(self, *_):
        self.clear_indicators()
        self.highlight()
        # always perform a direct insert hence return 1
        return 1

    def highlight(self):
        MalleableTree.drag_highlight = self
        # TODO add style

    def clear_highlight(self):
        # Remove the rectangular highlight around the node
        # TODO add style
        pass

    def clear_indicators(self):
        # Remove any remaining node highlights and edge indicators
        if MalleableTree.drag_highlight is not None:
            MalleableTree.drag_highlight.clear_highlight()
            self.edge_indicator.clear()


class MalleableTreeView(MalleableTree, ScrolledFrame):
    """
    Malleable TreeView that allows rearrangement of Nodes which useful in
    repositioning components in the various studio features.
    For any tree view that allows rearrangement, subclass MalleableTreeView.
    """

    def __init__(self, master=None, **config):
        super().__init__(master, **config)
        self.initialize_tree()

    def get_body(self):
        return self.body
