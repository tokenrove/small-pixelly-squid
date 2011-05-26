import os, re
import gtk.gdk as gdk
from editor import model

class Model(model.Model):
    def __init__(self, name=None, path=None, dimensions=(1,1), **kwds):
        model.Model.__init__(self, **kwds)
        self.path = path
        self.dimensions = dimensions
        self.name = name
        if self.name is None: self.name = '*unnamed*' if path is None else os.path.basename(path)
        if path is not None:
            self.pixbuf = gdk.pixbuf_new_from_file(path)
            self.dimensions = (self.pixbuf.get_width(), self.pixbuf.get_height())
        else:
            self.pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, dimensions[0], dimensions[1])

import re
def autodetect(path):
    return re.match(r'(?i)\.png$', os.path.splitext(path)[1]) is not None
