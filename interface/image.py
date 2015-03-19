import gtk
import editor.image
from interface import panel, form

class Panel(panel.Panel):
    def __init__(self, toplevel=None, model=None, **kwds):
        panel.Panel.__init__(self)
        self.toplevel = toplevel
        self.model = model
        self.label = gtk.Label(model.name)

        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.area = gtk.DrawingArea()
        self.area.set_size_request(*model.dimensions)

        self.area.connect('expose_event', self.on_expose)
        mask = gtk.gdk.EXPOSURE_MASK
        self.area.set_events(self.area.get_events() | mask)
        sw.add_with_viewport(self.area)
        hpane.pack1(sw, resize=True, shrink=False)
        palette_w = gtk.ScrolledWindow()
        palette_w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.palette = gtk.Label('color palette here...')
        palette_w.add_with_viewport(self.palette)
        hpane.pack2(palette_w, resize=True, shrink=True)

        hpane.show()
        self.add(hpane)
        self.show_all()
        self.status_id = self.toplevel.statusbar.get_context_id('Image' + model.name)
        self.toplevel.statusbar.push(self.status_id, 'I recommend using gfx2 for image editing instead.')

    def on_expose(self, widget, event):
        x,y,w,h = event.area
        w = min(w, self.model.pixbuf.get_width())
        h = min(h, self.model.pixbuf.get_height())
        widget.window.draw_pixbuf(None, self.model.pixbuf, x, y, x, y, w, h)
        return False

    has_unsaved_changes = property(lambda self: self.model.has_unsaved_changes)

def new_options():
    (f,results) = form.make([('Dimensions', (256,256))])
    return (f, lambda **kwds:Panel(model=editor.image.Model(dimensions=results['Dimensions']), **kwds))

def preview_fn(path):
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 128, 128)
        preview = gtk.Image()
        preview.set_from_pixbuf(pixbuf)
        return preview
    except:
        return None

from interface import modes
modes.register(['Image'], new_options, editor.image.autodetect,
               lambda path=None, **kwds: Panel(model=editor.image.Model(path=path), **kwds), preview_fn)
