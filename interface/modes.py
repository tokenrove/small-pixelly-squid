
import gtk
import util

def no_options(constructor):
    return lambda: (gtk.Label('This mode has no pre-creation options.'), constructor)

table = { }

autodetect_list = [ ]

def autodetect(path):
    t = table
    for (pred, mode) in autodetect_list:
        if pred(path):
            for e in mode: t = t[e]
            return t
    return None

def register(path, new_options_fn, autodetect_fn, open_fn, preview_fn=None):
    t = table
    for e in path[0:-1]:
        if not t.has_key(e): t[e] = {}
        assert type(t[e]) is dict
        t = t[e]
    assert not t.has_key(path[-1])
    t[path[-1]] = (new_options_fn, open_fn, preview_fn)
    # XXX wishlist: hints on how expensive this predicate is
    autodetect_list.append((autodetect_fn, path))
