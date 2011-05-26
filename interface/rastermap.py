
class Model():
    def __init__(self, dimensions=(1,1), grid_size=(1,1), **kwds):
        self.is_saved = True
        self.dimensions, self.grid_size = dimensions, grid_size

    # classmethod load unimplemented
    # method save unimplemented

    # map -- array of palette indices
    # palette -- list of objects

    width = property(lambda self: self.dimensions[0]*self.grid_size[0])
    height = property(lambda self: self.dimensions[1]*self.grid_size[1])
