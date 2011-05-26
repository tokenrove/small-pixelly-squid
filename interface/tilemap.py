
import gtk, goocanvas, os, operator, array

# class Model():
#     def __init__(self, **kwds): pass
#     @classmethod
#     def load(cls, path): pass
#     def save(self): pass
#     @property
#     is_saved = lambda self: return True

from interface import rastermap

class GenericModel(rastermap.Model):
    def __init__(self, map=None, slab_path=None, **kwds):
        rastermap.Model.__init__(self, **kwds)
        self.name = '*unnamed*'
        self.slab_path = slab_path
        if self.slab_path is not None:
            self.slab = gtk.gdk.pixbuf_new_from_file(self.slab_path)
        else:
            self.slab = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 256, self.grid_size[1])

        self.map = map
        if self.map is None:
            self.map = array.array('i', [0]*reduce(operator.mul, self.dimensions))

        def extract_tile(n):
            return self.slab.subpixbuf(n*self.grid_size[0], 0, self.grid_size[0], self.grid_size[1])
        zero = extract_tile(0)
        self.palette = [extract_tile(x) for x in range(0,self.slab.get_width()/self.grid_size[0])]

    @classmethod
    def load(cls, path):
        it = cls()
        return it

    def save(self):
        self.is_saved = True
        pass


class Panel(gtk.VBox):
    def __init__(self, toplevel=None, model=None, **kwds):
        gtk.VBox.__init__(self, False, 0)
        self.toplevel = toplevel
        self.model = model
        self.label = gtk.Label(model.name)

        ## example
        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.canvas = goocanvas.Canvas()
        self.canvas.connect('button_press_event', self.on_canvas_click)
        self.canvas.connect('motion_notify_event', self.on_canvas_motion)
        mask = gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK
        self.canvas.set_events(self.canvas.get_events() | mask)
        self.canvas.fill_color = self.style.bg[gtk.STATE_INSENSITIVE]
        root = self.canvas.get_root_item()
        table = goocanvas.Table(parent=root)
        grid = goocanvas.Grid(parent=root,
                              line_width=0.5,
                              line_dash=goocanvas.LineDash([0.0, 2.0, 2.0, 2.0]),
                              width=model.width, height=model.height, x_step=model.grid_size[0], y_step=model.grid_size[1])
        grid.props.visibility = goocanvas.ITEM_HIDDEN
        self.canvas.set_bounds(0,0, model.width, model.height)
        #root.animate(0,0, 16, 0, 0, 5000, 40, goocanvas.ANIMATE_BOUNCE)
        sw.add(self.canvas)
        hpane.pack1(sw, resize=True, shrink=False)

        palette_w = gtk.ScrolledWindow()
        palette_w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        ls = gtk.ListStore(gtk.gdk.Pixbuf)
        for e in model.palette:
            ls.append([e])
        self.palette = palette = gtk.IconView(ls)
        palette.set_size_request(100, 100)
        palette.set_pixbuf_column(0)
        palette.set_spacing(0)
        palette.set_selection_mode(gtk.SELECTION_MULTIPLE)
        palette.set_property('column-spacing', 0)
        palette.set_property('item-padding', 2)
        palette_w.add(palette)
        hpane.pack2(palette_w, resize=True, shrink=True)
        ##

        self.map = []
        for i in range(model.dimensions[1]):
            self.map.insert(i, [])
            for j in range(model.dimensions[0]):
                self.map[i].insert(j, goocanvas.Image(parent=table, pixbuf=model.palette[model.map[i*model.dimensions[0]+j]]))
                table.set_child_properties(self.map[i][j], row=i, column=j)

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

    def apply_current_tool(self, x, y):
        (x,y) = (int(x)/self.model.grid_size[0], int(y)/self.model.grid_size[1])
        if (x < 0 or x >= self.model.dimensions[0] or y < 0 or y >= self.model.dimensions[1]):
            return False

        root = self.canvas.get_root_item()
        (path,_) = self.palette.get_cursor() or (0,None)
        model = self.palette.get_model()
        pix = model.get_value(model.get_iter(path), 0)
        self.model.map[y*self.model.dimensions[0]+x] = path[0]
        self.map[y][x].set_property('pixbuf', pix)
        return True

    def has_unsaved_changes(self): return not self.model.is_saved

def generic_tilemap_new_panel_options():
    vbox = gtk.VBox()

    outer_hbox = gtk.HBox(False, 5)
    tabula_rasa_btn = gtk.RadioButton()
    outer_hbox.pack_start(tabula_rasa_btn, expand=False)

    tabula_frame = gtk.Frame('Tabula Rasa')
    inner_vbox = gtk.VBox()
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Room dimensions'), expand=False)
    h = gtk.Entry(max=4)
    h.set_width_chars(2)
    h.set_text('13')
    hbox.pack_end(h, expand=False)
    hbox.pack_end(gtk.Label('x'), expand=False)
    w = gtk.Entry(max=4)
    w.set_width_chars(2)
    w.set_text('20')
    hbox.pack_end(w, expand=False)
    inner_vbox.pack_start(hbox, expand=False)

    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Tile size'), expand=False)
    th = gtk.Entry(3)
    th.set_width_chars(2)
    th.set_text('16')
    hbox.pack_end(th, expand=False)
    hbox.pack_end(gtk.Label('x'), expand=False)
    tw = gtk.Entry(3)
    tw.set_width_chars(2)
    tw.set_text('16')
    hbox.pack_end(tw, expand=False)
    inner_vbox.pack_start(hbox, expand=False)
    tabula_frame.add(inner_vbox)
    outer_hbox.pack_start(tabula_frame)
    vbox.pack_start(outer_hbox, expand=False)
    tabula_rasa_btn.connect('toggled', lambda w:tabula_frame.set_sensitive(w.get_active()))

    outer_hbox = gtk.HBox(False, 5)
    mortimer_btn = gtk.RadioButton(tabula_rasa_btn)
    outer_hbox.pack_start(mortimer_btn, expand=False)

    # (frame "Mortimer" (vbox (hbox (label "Tile size") (entry "16" :width-chars 2) (label "x") (entry "16" :width-chars 2)) (hbox (label "Source image") (file-chooser-button "Select an image to mortimer"))))
    mortimer_frame = gtk.Frame('Mortimer')
    inner_vbox = gtk.VBox()
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Tile size'), expand=False)
    th = gtk.Entry(3)
    th.set_width_chars(2)
    th.set_text('16')
    hbox.pack_end(th, expand=False)
    hbox.pack_end(gtk.Label('x'), expand=False)
    tw = gtk.Entry(3)
    tw.set_width_chars(2)
    tw.set_text('16')
    hbox.pack_end(tw, expand=False)
    inner_vbox.pack_start(hbox, expand=False)
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label('Source image'), expand=False)
    chooser_btn = gtk.FileChooserButton('Select an image to mortimer')
    hbox.pack_end(chooser_btn, expand=False)
    inner_vbox.pack_start(hbox, expand=False)
    mortimer_frame.add(inner_vbox)
    outer_hbox.pack_start(mortimer_frame)
    vbox.pack_start(outer_hbox, expand=False)
    mortimer_btn.connect('toggled', lambda w:mortimer_frame.set_sensitive(w.get_active()))
    mortimer_frame.set_sensitive(False)

    def ctor(**kwds):
        if tabula_rasa_btn.get_active():
            model = GenericModel(dimensions=(int(w.get_text()), int(h.get_text())), grid_size=(int(tw.get_text()), int(th.get_text())), slab_path='slab.png')
        else:
            print 'mortimer not ready.'
            assert False
        return Panel(model=model, **kwds)
    return (vbox, ctor)

import re
def autodetect(path):
    return re.match(r'(?i)\.map$', os.path.splitext(path)[1]) is not None

from interface import modes
modes.register(['Tilemap'], generic_tilemap_new_panel_options, autodetect,
               lambda path=None,**kwds:Panel(model=Model.load(path),**kwds), None)
