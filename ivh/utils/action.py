class Action:
    """
    Action object for use in a undo redo system.
    """

    def __init__(self, undo, redo, **kwargs):
        """
        Initialize the action object with the undo and redo callbacks
        :param undo: The undo callback
        :param redo: The redo callback
        """
        self._undo = undo
        self._redo = redo
        self._data = kwargs.get("data", {})
        self.key = kwargs.get("key", None)

    def undo(self):
        self._undo(self._data)

    def redo(self):
        self._redo(self._data)

    def update_redo(self, redo):
        self._redo = redo

    def update(self, data):
        self._data.update(data)