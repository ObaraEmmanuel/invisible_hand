from studio import WidgetMeta

from commands import ComponentTree
from scrolledframe import ScrolledFrame
from tree import TreeView, MalleableTreeView


class ScrolledFrameMeta(ScrolledFrame, metaclass=WidgetMeta):
    display_name = 'ScrolledFrame'
    # impl is not necessary and can be inferred from the inheritance list
    impl = ScrolledFrame
    icon = "frame"
    is_container = False
    initial_dimensions = 100, 100


class TreeViewMeta(TreeView, metaclass=WidgetMeta):
    display_name = 'TreeView'
    # impl is not necessary and can be inferred from the inheritance list
    impl = TreeView
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100


class MalleableTreeViewMeta(MalleableTreeView, metaclass=WidgetMeta):
    display_name = 'MalleableTreeView'
    # impl is not necessary and can be inferred from the inheritance list
    impl = MalleableTreeView
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100


class ComponentTreeMeta(ComponentTree, metaclass=WidgetMeta):
    display_name = 'MalleableTreeView'
    # impl is not necessary and can be inferred from the inheritance list
    impl = ComponentTree
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100
