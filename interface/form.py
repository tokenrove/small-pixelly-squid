"""
Convenience shorthand for making all these cursed forms.
"""
import math
import gtk

class Result:
    def __getitem__(self, key):
        return self.__dict__[key]() if callable(self.__dict__[key]) else self.__dict__[key]

def make(items):
    result = Result()
    vbox = gtk.VBox()
    for (label,value) in items:
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(label), expand=False)
        result.__dict__[label] = make_field(hbox, value)
        vbox.pack_start(hbox, expand=False)
    return (vbox, result)

def about_this_long(n):
    return 1 + n + int(3.5*round(math.log(n,10)))

def make_field(hbox, value):
    if type(value) is str:
        field = gtk.Entry()
        field.set_width_chars(about_this_long(len(value)))
        field.set_text(value)
        hbox.pack_end(field, expand=False)
        return lambda:field.get_text()
    if type(value) is int:
        field = gtk.Entry()
        field.set_width_chars(about_this_long(len(str(value))))
        field.set_text(str(value))
        hbox.pack_end(field, expand=False)
        return lambda:int(field.get_text())
    if type(value) is tuple and len(value) == 2 and all(map(lambda v:type(v) is int, value)):
        # special case
        fn2 = make_field(hbox, value[1])
        hbox.pack_end(gtk.Label('x'), expand=False)
        fn1 = make_field(hbox, value[0])
        return lambda:(fn1(), fn2())
    if type(value) is tuple:
        fns = map(lambda v:make_field(hbox,v), reversed(value))
        return lambda:[fn() for fn in fns]
    if isinstance(value, gtk.Widget):
        hbox.pack_end(value, expand=False)
        return lambda:value
    assert False

#### TEST CODE

def _main():
    w = gtk.Window()
    w.set_position(gtk.WIN_POS_CENTER)
    w.connect('destroy', lambda w:gtk.main_quit())
    vbox = gtk.VBox()
    w.add(vbox)
    fr = gtk.Frame('the form')
    vbox.pack_start(fr)
    (form,result) = make([('Test', 'foo'),
                          ('Another test', (42,66)),
                          ('More stuff', (42,'foo','baz',109)),
                          ('Choose a file', gtk.FileChooserButton('foo')),
                          ])

    fr.add(form)
    button = gtk.Button(stock=gtk.STOCK_OK)
    def on_click(w):
        for v in result.__dict__: print result[v]
    button.connect('clicked', on_click)
    vbox.pack_start(button, expand=False)
    w.show_all()
    gtk.main()

if __name__ == "__main__": _main()
