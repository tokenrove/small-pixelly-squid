import gtk, goocanvas
import re, cPickle, os

class Panel(gtk.VBox):
    def __init__(self, toplevel=None, path=None, dimensions=(1,1), **kwds):
        gtk.VBox.__init__(self, False, 0)
        self.toplevel = toplevel
        self.dimensions = dimensions
        self.path = path
        self.label = gtk.Label('*unnamed*' if path is None else os.path.basename(path))

        with open(path) as f:
            level = cPickle.load(f)

        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.canvas = goocanvas.Canvas()
        grid = goocanvas.Grid(parent=self.canvas.get_root_item(),
                              line_width=0.5,
                              line_dash=goocanvas.LineDash([4.0, 4.0]),
                              width=800, height=600, x_step=20*16, y_step=13*16)
        sw.add(self.canvas)
        hpane.pack1(sw, resize=True, shrink=False)
        # room list
        vpane = gtk.VPaned()
        hpane.pack2(vpane)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(gtk.Label('List of rooms %s' % len(level['rooms'])))
        vpane.pack1(sw)
        vpane.pack2(gtk.Label('Room editing details and controls'))

        hpane.show()
        self.add(hpane)
        self.show_all()


def autodetect(path):
    if re.search(r'(?i)\.lev$', path) is None: return False
    with open(path) as f:
        try:
            level = cPickle.load(f)
            return level['magic'] == 'Berzerk'
        except: return False

def preview_fn(path):
    with open(path) as f:
        level = cPickle.load(f)
        return gtk.Label('Griefenzerk level with %s rooms' % len(level['rooms']))

import modes
modes.register(['Level', 'Griefenzerk'],
               modes.no_options(Panel), autodetect, Panel, preview_fn)
