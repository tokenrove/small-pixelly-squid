import gtk, goocanvas, os

class Panel(gtk.VBox):
    def __init__(self, toplevel=None, path=None, dimensions=(1,1), **kwds):
        gtk.VBox.__init__(self, False, 0)
        self.toplevel = toplevel
        self.dimensions = dimensions
        self.path = path
        self.label = gtk.Label('*unnamed*' if path is None else os.path.basename(path))

        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.area = gtk.DrawingArea()
        self.area.set_size_request(*dimensions)
        if path is not None:
            self.pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        else:
            self.pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, dimensions[0], dimensions[1])

        self.area.connect('expose_event', self.on_expose)
        mask = gtk.gdk.EXPOSURE_MASK
        self.area.set_events(self.area.get_events() | mask)
        sw.add_with_viewport(self.area)
        hpane.pack1(sw, resize=True, shrink=False)
        palette_w = gtk.ScrolledWindow()
        palette_w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.palette = goocanvas.Canvas()
        grid = goocanvas.Grid(parent=self.palette.get_root_item(),
                              line_width=0.5,
                              line_dash=goocanvas.LineDash([4.0, 4.0]),
                              width=128, height=256, x_step=16, y_step=16)
        palette_w.add(self.palette)
        hpane.pack2(palette_w, resize=True, shrink=True)

        hpane.show()
        self.add(hpane)
        self.show_all()

    def on_expose(self, widget, event):
        x,y,w,h = event.area
        w = min(w, self.pixbuf.get_width())
        h = min(h, self.pixbuf.get_height())
        widget.window.draw_pixbuf(None, self.pixbuf, x, y, x, y, w, h)
        return False

import re
def autodetect(path):
    return re.search(r'(?i)\.png$', path) is not None


def new_options():
    vbox = gtk.VBox()

    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Dimensions'), expand=False)
    h = gtk.Entry(max=5)
    h.set_width_chars(4)
    h.set_text('256')
    hbox.pack_end(h, expand=False)
    hbox.pack_end(gtk.Label('x'), expand=False)
    w = gtk.Entry(max=5)
    w.set_width_chars(4)
    w.set_text('256')
    hbox.pack_end(w, expand=False)
    vbox.pack_start(hbox, expand=False)

    return (vbox, lambda **kwds:Panel(dimensions=(int(w.get_text()), int(h.get_text())), **kwds))



def preview_fn(path):
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 128, 128)
        preview = gtk.Image()
        preview.set_from_pixbuf(pixbuf)
        return preview
    except:
        return None

import modes
modes.register(['Image'],
               new_options, autodetect, Panel, preview_fn)
