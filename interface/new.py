
import gtk

from interface import tilemap, modes

def populate_model_from_dict(m, d, parent=None):
    for (k,v) in d.items():
        i = m.append(parent, [k,None if type(v) is dict else v])
        if type(v) is dict:
            populate_model_from_dict(m, v, i)

class Panel(gtk.VBox):
    def __init__(self, toplevel = None, **kwds):
        gtk.VBox.__init__(self, False, 1)
        self.label = gtk.Label('New..')
        self.toplevel = toplevel

        hbox = gtk.HBox(False, 1)
        hbox.pack_start(gtk.Label('Select project type:'), expand=False)
        model = gtk.TreeStore(str, object)
        populate_model_from_dict(model, modes.table)
        self.type_select = gtk.ComboBox(model)
        cell = gtk.CellRendererText()
        self.type_select.pack_start(cell, True)
        self.type_select.add_attribute(cell, 'text', 0)
        self.type_select.connect('changed', self.on_type_select)
        hbox.pack_start(self.type_select, expand=False)
        self.pack_start(hbox, expand=False)

        self.options_form = gtk.ScrolledWindow()
        self.options_form.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.pack_start(self.options_form)
        buttons = gtk.HButtonBox()
        buttons.set_layout(gtk.BUTTONBOX_END)
        cancel_button = gtk.Button('Cancel', gtk.STOCK_CANCEL)
        cancel_button.connect('clicked', self.on_cancel)
        buttons.add(cancel_button)
        self.ok_button = gtk.Button('OK', gtk.STOCK_OK)
        self.ok_button.handler_id = None
        self.ok_button.set_sensitive(False)
        buttons.add(self.ok_button)
        self.pack_end(buttons, expand=False)

        self.show_all()

    def on_cancel(self, *args): self.parent.remove(self)

    def activate_ok_button(self, on_ok):
        if self.ok_button.handler_id is not None:
            self.ok_button.disconnect(self.ok_button.handler_id)
        fn = lambda w:self.toplevel.replace_panel(self, on_ok(toplevel=self.toplevel))
        self.ok_button.handler_id = self.ok_button.connect('clicked', fn)
        self.ok_button.set_sensitive(True)

    def on_type_select(self, cb, *args):
        model, active = cb.get_model(), cb.get_active_iter()
        widget, on_ok = model.get_value(active, 1)[0]()
        for c in self.options_form.get_children(): self.options_form.remove(c)
        self.options_form.add_with_viewport(widget)
        self.activate_ok_button(on_ok)
        self.show_all()

    def has_unsaved_changes(self): return False

