import gtk, goocanvas
import editor.griefenzerk
from interface import panel, tilemap

class Panel(panel.Panel):
    def __init__(self, toplevel=None, model=None, **kwds):
        panel.Panel.__init__(self)
        self.toplevel = toplevel
        self.model = model
        self.label = gtk.Label(model.name)
        self.subpanels = []

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
        for i,r in enumerate(model.rooms): room_model.append([i,r])
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
        for r in self.subpanels:
            print r.model.id

        for panel in self.subpanels:
            if isinstance(panel.model, editor.griefenzerk.RoomModel) and panel.model.id == id:
                self.toplevel.switch_to(panel)
                return

        model = editor.griefenzerk.RoomModel.from_room(parent=self.model, id=id)
        self.subpanels.append(tilemap.Panel(model=model, toplevel=self.toplevel))
        self.toplevel.append_panel(self.subpanels[-1])

    def on_room_cursor_changed(self, widget):
        (path,column) = widget.get_cursor()
        for b in self.item_buttons:
            b.set_sensitive(path is not None)

    def save(self):
        self.model.save()

    @property
    def has_unsaved_changes(self):
        return self.model.has_unsaved_changes or any(x.has_unsaved_changes for x in self.subpanels)


import cPickle
def preview_fn(path):
    with open(path) as f:
        level = cPickle.load(f)
        return gtk.Label('Griefenzerk level with %s rooms' % len(level['rooms']))

from interface import modes
modes.register(['Level', 'Griefenzerk'],
               modes.no_options(lambda **kwds:Panel(model=editor.griefenzerk.LevelModel(), **kwds)),
               editor.griefenzerk.autodetect,
               lambda path=None,**kwds:Panel(model=editor.griefenzerk.LevelModel.load(path), **kwds),
               preview_fn)
