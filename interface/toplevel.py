
import gtk

from interface import pie, splash, modes
import interface.open, interface.new

class TopLevel(gtk.Window):
    """Main application window that hosts panels."""

    def new_file(self, action):
        #self.content_box = gtk.VBox(False, 1)
        pass

    def quit_request(self, *args):
        # XXX Check if we have unsaved projects
        if any(p.has_unsaved_changes for p in self.notebook.get_children()):
            print 'Quitting with unsaved changes!'
            for p in self.notebook.get_children():
                if p.has_unsaved_changes: print p
        gtk.main_quit()

    def __init__(self, argv = None, **kwds):
        gtk.Window.__init__(self, **kwds)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title('Small Pixelly Squid')
        # XXX or full screen?
        self.set_size_request(800,600)
        self.connect("destroy", self.quit_request)
        self.connect('key_press_event', self.on_key_press)

        main_vbox = gtk.VBox(False, 1)
        ev_box = gtk.EventBox()
        ev_box.add(main_vbox)
        self.add(ev_box)
        main_vbox.show()
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        self.notebook.reorderable = True
        self.notebook.connect('page-removed', self.on_page_remove)
        main_vbox.pack_start(self.notebook)
        self.statusbar = gtk.Statusbar()
        self.status_id = self.statusbar.get_context_id('Toplevel')
        self.statusbar.push(self.status_id, 'Hit F for the File Menu.')
        main_vbox.pack_end(self.statusbar, expand=False)
        self.show_all()

        for f in argv[1:]: self.commandline_open(f)
        if self.notebook.get_n_pages() == 0: self.append_panel(splash.Panel)
        self.show_all()

    def commandline_open(self, path):
        mode = modes.autodetect(path)
        if mode is None: return
        self.append_panel(lambda **kwds:mode[1](path=path, **kwds))

    def append_panel(self, panel_or_ctor):
        panel = panel_or_ctor(toplevel=self) if callable(panel_or_ctor) else panel_or_ctor
        nidx = self.notebook.append_page(panel, panel.label)
        self.notebook.set_current_page(nidx)
        self.notebook.show_all()
        self.show_all()
        return True

    def switch_to(self, panel):
        self.notebook.set_current_page(self.notebook.page_num(panel))
        self.notebook.show_all()
        self.show_all()

    def replace_panel(self, old_panel, new_panel):
        idx = self.notebook.page_num(old_panel)
        nidx = self.notebook.append_page(new_panel, new_panel.label)
        self.notebook.remove_page(idx)
        self.notebook.set_current_page(nidx)
        self.notebook.show_all()
        return True

    def on_key_press(self, widget, event):
        ## Handle root menu
        if event.keyval != ord('f'): return False
        menu = pie.Menu([('New',lambda:self.append_panel(interface.new.Panel)),
                         ('Open',lambda:self.append_panel(interface.open.Panel)),
                         ('Quit',self.quit_request)])
        (x,y,_) = widget.window.get_pointer()
        menu.popup(x,y)
        return True

    def on_page_remove(self, nb, child, page_num):
        if nb.get_n_pages() == 0:
            panel = splash.Panel(toplevel=self)
            nb.append_page(panel, panel.label)
            self.show_all()
