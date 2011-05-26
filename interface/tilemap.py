import gtk, goocanvas
import editor.tilemap
from interface import panel, form

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
        (path,_) = self.palette.get_cursor() or ((0,),None)
        model = self.palette.get_model()
        pix = model.get_value(model.get_iter(path), 0)
        self.model.map[y*self.model.dimensions[0]+x] = path[0]
        self.model.has_unsaved_changes = True
        self.map[y][x].set_property('pixbuf', pix)
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

from interface import modes
modes.register(['Tilemap'], generic_tilemap_new_panel_options, editor.tilemap.autodetect,
               lambda path=None,**kwds:Panel(model=editor.tilemap.GenericModel.load(path),**kwds), None)
