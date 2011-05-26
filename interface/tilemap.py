import gtk
import editor.tilemap
from interface import panel, form

class Presentation():
    UPDATE = 1
    def __init__(self, model=None, **kwds):
        self.model = model
        self.hooks = {self.UPDATE:[]}
        self.pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, model.width, model.height)
        self.redraw((0, 0, model.width, model.height))

    def as_pixbuf(self): return self.pixbuf
    ### XXX note these values are in tiles, not pixels
    def smirch(self, r):
        self.redraw(r)
        
    def redraw(self, r):
        (x,y,w,h) = r
        (mw,mh) = self.model.dimensions
        (tw,th) = self.model.grid_size
        for ty in xrange(max(0,y), min(y+h, mh)):
            for tx in xrange(max(0,x), min(x+w, mw)):
                idx = self.model.map[ty*mw+tx]
                self.model.palette[idx].copy_area(0,0,tw,th, self.pixbuf, tx*tw, ty*th)

        for fn in self.hooks[self.UPDATE]: fn(self, (x*tw,y*th,w*tw,h*th))

    def hook(self, routine, callback):
        if self.hooks.get(routine) is None: self.hooks[routine] = []
        self.hooks[routine].append(callback)

class TilePalette(gtk.IconView):
    def __init__(self, source):
        ls = gtk.ListStore(gtk.gdk.Pixbuf)
        gtk.IconView.__init__(self, ls)
        for e in source:
            ls.append([e])
        self.set_size_request(100, 100)
        self.set_pixbuf_column(0)
        self.set_spacing(0)
        self.set_selection_mode(gtk.SELECTION_MULTIPLE)
        self.set_property('column-spacing', 0)
        self.set_property('item-padding', 2)

class Panel(panel.Panel):
    def __init__(self, toplevel=None, model=None, **kwds):
        panel.Panel.__init__(self)
        self.toplevel = toplevel
        self.model = model
        self.label = gtk.Label(model.name)

        ## example
        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.canvas = gtk.DrawingArea()
        self.canvas.connect('expose_event', self.on_canvas_expose)
        self.canvas.connect('button_press_event', self.on_canvas_click)
        self.canvas.connect('motion_notify_event', self.on_canvas_motion)
        mask = gtk.gdk.EXPOSURE_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK
        self.canvas.set_events(self.canvas.get_events() | mask)
        self.canvas.set_size_request(model.width, model.height)
        sw.add_with_viewport(self.canvas)
        hpane.pack1(sw, resize=True, shrink=False)

        self.map = Presentation(model)
        def changed(p,r): self.canvas.queue_draw_area(*r)
        self.map.hook(Presentation.UPDATE, changed)

        palette_w = gtk.ScrolledWindow()
        palette_w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.palette = TilePalette(model.palette)
        palette_w.add(self.palette)
        hpane.pack2(palette_w, resize=True, shrink=True)
        ##

        hpane.show()
        self.add(hpane)
        self.show_all()

    def on_canvas_motion(self, canvas, event):
        x,y,state = event.window.get_pointer() if event.is_hint else (event.x,event.y,event.state)
        if state & gtk.gdk.BUTTON1_MASK:
            return self.apply_current_tool(x, y)

    def on_canvas_click(self, canvas, event):
        if event.button != 1: return False
        return self.apply_current_tool(event.x, event.y)

    def on_canvas_expose(self, canvas, event):
        (x,y,w,h) = event.area
        pixbuf = self.map.as_pixbuf()
        w = min(w, pixbuf.get_width())
        h = min(h, pixbuf.get_height())
        canvas.window.draw_pixbuf(None, pixbuf, x,y, x,y,w,h)
        # XXX show grid here, etc

    def apply_current_tool(self, x, y):
        (x,y) = (int(x)/self.model.grid_size[0], int(y)/self.model.grid_size[1])
        if (x < 0 or x >= self.model.dimensions[0] or y < 0 or y >= self.model.dimensions[1]):
            return False

        (path,_) = self.palette.get_cursor() or ((0,),None)
        model = self.palette.get_model()
        pix = model.get_value(model.get_iter(path), 0)
        
        self.model.map[y*self.model.dimensions[0]+x] = path[0]
        self.model.has_unsaved_changes = True
        self.map.smirch((x,y,1,1))
        return True

    has_unsaved_changes = property(lambda self: self.model.has_unsaved_changes)

def generic_tilemap_new_panel_options():
    vbox = gtk.VBox()

    outer_hbox = gtk.HBox(False, 5)
    tabula_rasa_btn = gtk.RadioButton()
    outer_hbox.pack_start(tabula_rasa_btn, expand=False)
    tabula_frame = gtk.Frame('Tabula Rasa')
    (f,tabula) = form.make([('Room dimensions', (20,13)),
                            ('Tile size', (16,16))])
    tabula_frame.add(f)
    outer_hbox.pack_start(tabula_frame)
    vbox.pack_start(outer_hbox, expand=False)
    tabula_rasa_btn.connect('toggled', lambda w:tabula_frame.set_sensitive(w.get_active()))

    outer_hbox = gtk.HBox(False, 5)
    mortimer_btn = gtk.RadioButton(tabula_rasa_btn)
    outer_hbox.pack_start(mortimer_btn, expand=False)
    mortimer_frame = gtk.Frame('Mortimer')
    (f,mortimer) = form.make([('Tile size', (16,16)),
                              ('Source image', gtk.FileChooserButton('Select image to mortimer'))])
    mortimer_frame.add(f)
    outer_hbox.pack_start(mortimer_frame)
    vbox.pack_start(outer_hbox, expand=False)
    mortimer_btn.connect('toggled', lambda w:mortimer_frame.set_sensitive(w.get_active()))
    mortimer_frame.set_sensitive(False)

    def ctor(**kwds):
        if tabula_rasa_btn.get_active():
            model = editor.tilemap.GenericModel(dimensions=tabula['Room dimensions'], grid_size=tabula['Tile size'])
        else:
            print 'gonna mortimer: %s at %s' % (mortimer['Source image'].get_filename(), mortimer['Tile size'])
            print 'mortimer not ready.'
            assert False
        return Panel(model=model, **kwds)
    return (vbox, ctor)

def preview_fn(path):
    return gtk.Label(str(editor.tilemap.query_dimensions_of_file(path)))

from interface import modes
modes.register(['Tilemap'], generic_tilemap_new_panel_options, editor.tilemap.autodetect,
               lambda path=None,**kwds:Panel(model=editor.tilemap.GenericModel.load(path),**kwds),
               preview_fn)
