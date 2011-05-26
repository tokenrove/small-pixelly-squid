import operator, array, os, re
import gtk.gdk as gdk
from editor import rastermap

class GenericModel(rastermap.Model):
    def __init__(self, map=None, slab_path=None, **kwds):
        rastermap.Model.__init__(self, **kwds)
        self.slab_path = slab_path
        if self.slab_path is not None:
            self.slab = gdk.pixbuf_new_from_file(self.slab_path)
        else:
            self.slab = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, 256, self.grid_size[1])

        self.map = map
        if self.map is None:
            self.map = array.array('i', [0]*reduce(operator.mul, self.dimensions))

        def extract_tile(n):
            return self.slab.subpixbuf(n*self.grid_size[0], 0, self.grid_size[0], self.grid_size[1])
        zero = extract_tile(0)
        self.palette = [extract_tile(x) for x in range(0,self.slab.get_width()/self.grid_size[0])]

    @classmethod
    def load(cls, path):
        # XXX wrong, bad, etc
        it = cls()
        return it

    def save(self):
        self.has_unsaved_changes = False
        pass


def autodetect(path):
    return re.match(r'(?i)\.map$', os.path.splitext(path)[1]) is not None

