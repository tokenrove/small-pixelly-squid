import gtk, goocanvas
import re, cPickle, os

class LevelModel():
    def __init__(self, path=None, rooms=None, **kwds):
        self.is_saved = True
        self.name = '*unnamed*' if path is None else os.path.basename(path)
        self.rooms = rooms
        if self.rooms == None: self.rooms = []

    @classmethod
    def load(cls, path):
        with open(path) as f:
            level = cPickle.load(f)
        if level['magic'] != 'Berzerk': return None
        return LevelModel(path=path, rooms = level['rooms'])

    def save(self):
        if not self.path:
            print 'no path! implement save-as...'
            return
        try:
            with open(path, "w") as f:
                cPickle.dump({'magic':'Berzerk', 'rooms':self.rooms}, f)
            self.is_saved = True
        except IOError: return


class Panel(gtk.VBox):
    def __init__(self, toplevel=None, model=None, **kwds):
        gtk.VBox.__init__(self, False, 0)
        self.toplevel = toplevel
        self.model = model
        self.label = gtk.Label(model.name)

        hpane = gtk.HPaned()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.canvas = goocanvas.Canvas()
        grid = goocanvas.Grid(parent=self.canvas.get_root_item(),
                              line_width=0.5,
                              line_dash=goocanvas.LineDash([4.0, 4.0]),
                              width=1500, height=1500, x_step=20*16, y_step=13*16)
        sw.add(self.canvas)
        hpane.pack1(sw, resize=True, shrink=False)
        # room list
        vpane = gtk.VPaned()
        hpane.pack2(vpane)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        room_model = gtk.ListStore(int, object)
        for i,r in enumerate(model.rooms):
            room_model.append([i,r])
        self.room_list = gtk.TreeView(room_model)
        def fn(column, cell, model, iter):
            cell.set_property('text', str(model.get_value(iter, 0)))
        cell = gtk.CellRendererText()
        id_column = gtk.TreeViewColumn('ID', cell)
        self.room_list.append_column(id_column)
        self.room_list.connect('cursor-changed', self.on_room_cursor_changed)
        id_column.set_cell_data_func(cell, fn)
        sw.add_with_viewport(self.room_list)
        vpane.pack1(sw)

        hbox = gtk.HBox(False, 5)
        frame = gtk.Frame('Room Properties')
        inner_vbox = gtk.VBox()
        inner_hbox = gtk.HBox()
        inner_hbox.pack_start(gtk.Label('Connected to:'))
        inner_hbox.pack_start(gtk.ComboBox())
        inner_vbox.pack_start(inner_hbox)
        frame.add(inner_vbox)
        hbox.pack_start(frame)

        buttons = gtk.VButtonBox()
        buttons.set_layout(gtk.BUTTONBOX_START)
        self.item_buttons = []
        for (l,s,fn) in [('Up', gtk.STOCK_GO_UP, lambda *args:False),
                        ('Down', gtk.STOCK_GO_DOWN, lambda *args:False),
                        ('Duplicate', gtk.STOCK_COPY, lambda *args:False),
                        ('Edit', gtk.STOCK_EDIT, self.on_edit_room),
                        ('Delete', gtk.STOCK_DELETE, lambda *args:False)]:
            b = gtk.Button(l,s)
            b.connect('clicked', fn)
            self.item_buttons.append(b)
            buttons.pack_start(b)
            b.set_sensitive(False)
        buttons.pack_end(gtk.Button('Add', gtk.STOCK_ADD))
        hbox.pack_end(buttons, expand=False)
        vpane.pack2(hbox)

        hpane.show()
        self.add(hpane)
        self.show_all()

    def on_edit_room(self, button):
        (path,_) = self.room_list.get_cursor()
        model = self.room_list.get_model()
        (id,room) = model.get(model.get_iter(path), 0, 1)
        print 'going to edit room %s' % room
        ## here's where buffer management would come in handy...
        buf = self.toplevel.find_buffer([self.path, 'room %d' % id])
        if buf is None:
            self.toplevel.append_panel(tilemap.Panel(map=room))

    def on_room_cursor_changed(self, widget):
        (path,column) = widget.get_cursor()
        for b in self.item_buttons:
            b.set_sensitive(path is not None)

    def has_unsaved_changes(self): return not self.model.is_saved


def autodetect(path):
    if re.match(r'(?i)\.lev$', os.path.splitext(path)[1]) is None: return False
    with open(path) as f:
        try:
            level = cPickle.load(f)
            return level['magic'] == 'Berzerk'
        except: return False

def preview_fn(path):
    with open(path) as f:
        level = cPickle.load(f)
        return gtk.Label('Griefenzerk level with %s rooms' % len(level['rooms']))

from interface import modes
modes.register(['Level', 'Griefenzerk'],
               modes.no_options(lambda **kwds:Panel(model=LevelModel(), **kwds)),
               autodetect, lambda path=None,**kwds:Panel(model=LevelModel.load(path), **kwds),
               preview_fn)
