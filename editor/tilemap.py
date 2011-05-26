import operator, array, os, re, struct
import gtk.gdk as gdk
from editor import rastermap

class GenericModel(rastermap.Model):
    def __init__(self, name=None, path=None, map=None, slab_path=None, **kwds):
        rastermap.Model.__init__(self, **kwds)
        self.path, self.slab_path, self.map, self.name = path, slab_path, map, name
        if self.name is None: self.name = '*unnamed*' if path is None else os.path.basename(path)
        if self.slab_path is not None:
            self.slab = gdk.pixbuf_new_from_file(self.slab_path)
        else:
            self.slab = gdk.Pixbuf(gdk.COLORSPACE_RGB, False, 8, 256, self.grid_size[1])
        if self.map is None:
            self.map = array.array('i', [0]*reduce(operator.mul, self.dimensions))

        def extract_tile(n):
            return self.slab.subpixbuf(n*self.grid_size[0], 0, self.grid_size[0], self.grid_size[1])
        zero = extract_tile(0)
        self.palette = [extract_tile(x) for x in range(0,self.slab.get_width()/self.grid_size[0])]

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            magic = f.read(len(OLD_MAGIC))
            dimensions = (w,h) = struct.unpack('>HH', f.read(4))
            map = array.array('B', f.read(w*h))
        slab_path = os.path.splitext(path)[0] + '.png'
        it = cls(path=path, map=map, slab_path=slab_path, dimensions=dimensions, grid_size=(8,8))
        return it

    def save(self):
        assert self.path is not None
        with open(self.path, 'wb') as f:
            f.write(OLD_MAGIC)
            f.write(struct.pack('>HH', self.dimensions[0], self.dimensions[1]))
            f.write(self.map)
        # XXX should check to make sure slab is there
        self.has_unsaved_changes = False
        pass


def query_dimensions_of_file(path):
    with open(path, 'rb') as f:
        magic = f.read(len(OLD_MAGIC))
        if magic != OLD_MAGIC: return None
        (w,h) = struct.unpack('>HH', f.read(4))
        return (w,h)

OLD_MAGIC = 'animosity-map'

def autodetect(path):
    if re.match(r'(?i)\.map$', os.path.splitext(path)[1]) is None: return False
    if not os.path.isfile(os.path.splitext(path)[0] + '.png'): return False
    with open(path, 'rb') as f:
        return f.read(len(OLD_MAGIC)) == OLD_MAGIC

