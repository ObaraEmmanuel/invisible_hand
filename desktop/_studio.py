from studio import WidgetMeta

from catalogue import CatalogueList
from commands import ComponentTree
from scrolledframe import ScrolledFrame
from tree import TreeView


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


class ComponentTreeMeta(ComponentTree, metaclass=WidgetMeta):
    display_name = 'ComponentTree'
    # impl is not necessary and can be inferred from the inheritance list
    impl = ComponentTree
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100


class CatalogueListMeta(CatalogueList, metaclass=WidgetMeta):
    display_name = 'CatalogueList'
    # impl is not necessary and can be inferred from the inheritance list
    impl = CatalogueList
    icon = "listbox"
    is_container = False
    initial_dimensions = 100, 100
