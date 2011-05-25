import gtk, re

import modes

class Panel(gtk.VBox):
    def __init__(self, toplevel=None, **kwds):
        gtk.VBox.__init__(self, False, 1)
        self.label = gtk.Label('Open..')
        self.toplevel = toplevel

        chooser = gtk.FileChooserWidget(gtk.FILE_CHOOSER_ACTION_OPEN)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("Level formats")
        filter.add_pattern("*.map")
        filter.add_pattern("*.lev")
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.gif")
        chooser.add_filter(filter)

        chooser.connect('update-preview', self.on_update_preview)
        chooser.connect('selection-changed', self.on_selection_changed)
        chooser.connect('file-activated', self.on_file_activated)

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
        self.pack_end(chooser)

        self.show_all()

    def on_cancel(self, *args):
        self.parent.remove(self)

    def activate_ok_button(self, open_fn):
        if self.ok_button.handler_id is not None:
            self.ok_button.disconnect(self.ok_button.handler_id)
        fn = lambda w:self.toplevel.replace_panel(self, open_fn(toplevel=self.toplevel))
        self.ok_button.handler_id = self.ok_button.connect('clicked', fn)
        self.ok_button.set_sensitive(True)

    def on_selection_changed(self, chooser):
        path = chooser.get_filename()
        # use autodetect table to update preview
        mode = modes.autodetect(path) if path else None
        if mode is None:
            chooser.set_preview_widget_active(False)
            self.ok_button.set_sensitive(False)
            return
        (new_fn,open_fn,self.preview_fn) = mode
        self.activate_ok_button(lambda **kwds:open_fn(path=path, **kwds))
        chooser.set_preview_widget_active(True)
        self.on_update_preview(chooser)

    def on_file_activated(self, chooser):
        if self.ok_button.get_sensitive(): self.ok_button.clicked()

    def on_update_preview(self, chooser):
        path = chooser.get_preview_filename()
        if chooser.get_preview_widget_active():
            preview = self.preview_fn(path)
            if preview is not None:
                chooser.set_preview_widget(preview)
                chooser.set_preview_widget_active(True)
