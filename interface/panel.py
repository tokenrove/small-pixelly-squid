
import gtk

class Panel(gtk.VBox):
    __gtype_name__ = 'Panel'
    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
