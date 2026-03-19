from studio import WidgetMeta

from catalogue import CatalogueList
from commands import ComponentTree
from device_select import DeviceSelector
from macro import MacroList
from ui.scrolledframe import ScrolledFrame
from ui.tree import TreeView


class ScrolledFrameMeta(ScrolledFrame, metaclass=WidgetMeta):
    display_name = 'ScrolledFrame'
    impl = ScrolledFrame
    icon = "frame"
    is_container = False
    initial_dimensions = 100, 100


class TreeViewMeta(TreeView, metaclass=WidgetMeta):
    display_name = 'TreeView'
    impl = TreeView
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100


class ComponentTreeMeta(ComponentTree, metaclass=WidgetMeta):
    display_name = 'ComponentTree'
    impl = ComponentTree
    icon = "treeview"
    is_container = False
    initial_dimensions = 100, 100


class CatalogueListMeta(CatalogueList, metaclass=WidgetMeta):
    display_name = 'CatalogueList'
    impl = CatalogueList
    icon = "listbox"
    is_container = False
    initial_dimensions = 100, 100


class MacroListMeta(MacroList, metaclass=WidgetMeta):
    display_name = 'MacroList'
    impl = MacroList
    icon = "listbox"
    is_container = False
    initial_dimensions = 100, 100


class DeviceSelectorMeta(DeviceSelector, metaclass=WidgetMeta):
    display_name = 'DeviceSelector'
    impl = DeviceSelector
    icon = "menubutton"
    is_container = False
    initial_dimensions = 100, 100
