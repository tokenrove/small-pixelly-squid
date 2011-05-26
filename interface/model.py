
class Model():
    def __init__(self, name=None, **kwds):
        self.name = '*unnamed*' if name is None else name
        self.has_unsaved_changes = False

    @classmethod
    def load(cls, path):
        """
        """
        pass

    def save(self):
        """
        """
        pass

