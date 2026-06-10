import abc
from typing import Union

from ivh.ui.tree import Tree, InsertType


class GlueInterface(abc.ABC):
    _instance: Union['GlueInterface', None] = None

    @abc.abstractmethod
    def add_node(self, target: Tree.Node, node: Tree.Node, method: InsertType, silent: bool = True):
        pass

    @abc.abstractmethod
    def delete_nodes(self, nodes: list[Tree.Node], silent: bool = True):
        pass

    @abc.abstractmethod
    def on_nodes_moved(self, nodes: list[Tree.Node], old_parents: list[Tree.Node], old_indices: list[int]):
        pass

    @abc.abstractmethod
    def restore_nodes(self, nodes: list[Tree.Node], old_parents: list[Tree.Node], old_indices: list[int]):
        pass

    @abc.abstractmethod
    def close_connections(self):
        pass

    @classmethod
    def instance(cls) -> 'GlueInterface':
        return cls._instance

    @classmethod
    def set_instance(cls, instance):
        cls._instance = instance

    @classmethod
    def _compact(cls, nodes: list[Tree.Node]) -> list[Tree.Node]:
        reduced_nodes = set()
        for node in sorted(set(nodes), key=lambda n: n.depth):
            parent = node.parent_node
            while parent:
                if parent in reduced_nodes:
                    break
                parent = parent.parent_node
            else:
                reduced_nodes.add(node)
        return list(reduced_nodes)

    @classmethod
    def _compact_ancestors(cls, nodes: list[Tree.Node]) -> list[Tree.Node]:
        reduced_nodes = set()
        for node in nodes:
            if node.is_terminal:
                reduced_nodes.add(node.parent_node)
            else:
                reduced_nodes.add(node)
        return list(reduced_nodes)
