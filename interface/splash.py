
import gtk

import new, open, util

class Panel(gtk.VBox):
    label = gtk.Label('Splash Screen')
    splash_text = '''<b>Small Pixelly Squid</b> v0

Julian Squires &lt;julian@cipht.net&gt; / 2011

Not much to see here yet...'''

    def __init__(self, toplevel=None, **kwds):
        self.toplevel = toplevel
        gtk.VBox.__init__(self, False, 5)
        label = gtk.Label(Panel.splash_text)
        label.set_use_markup(True)
        self.pack_start(label)

        frame = gtk.Frame('Recent projects:')
        frame.set_label_align(0.9, 0.5)
        hbox = gtk.HBox(False, 5)
        widget = gtk.RecentChooserWidget()
        widget.set_size_request(400, 80)
        hbox.add(widget)
        self.recent_ok = gtk.Button('Open', gtk.STOCK_OK)
        self.recent_ok.set_sensitive(False)
        buttons = gtk.HButtonBox()
        buttons.add(self.recent_ok)
        hbox.pack_start(buttons, expand=False)
        frame.add(hbox)
        self.pack_end(frame, expand=False, padding=5)

        frame = gtk.Frame('Next action:')
        frame.set_label_align(0.9, 0.5)
        buttons = gtk.HButtonBox()
        buttons.set_layout(gtk.BUTTONBOX_END)
        for (l,s,fn) in (('New..', gtk.STOCK_NEW, self.on_new),
                        ('Open..', gtk.STOCK_OPEN, self.on_open),
                        ('Quit', gtk.STOCK_QUIT, self.on_quit)):
            b = gtk.Button(l, s)
            b.connect('clicked', fn)
            buttons.pack_end(b, padding=2)
        buttons.show()
        frame.add(buttons)
        self.pack_end(frame, expand=False, padding=5)

        self.show_all()

    def on_new(self, *args):
        self.toplevel.replace_panel(self, new.Panel(toplevel=self.toplevel))

    def on_open(self, *args):
        self.toplevel.replace_panel(self, open.Panel(toplevel=self.toplevel))

    def on_quit(self, *args):
        self.toplevel.quit_request()
