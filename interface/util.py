
import gtk

def get_cb_active_text(combobox):
    model = combobox.get_model()
    active = combobox.get_active()
    return model[active][0] if active >= 0 else None

def new_text_combobox(items):
    cb = gtk.combo_box_new_text()
    for i in items: cb.append_text(i)
    return cb

def populate_model_from_dict(m, d, parent=None):
    for (k,v) in d.items():
        i = m.append(parent, [k,None if type(v) is dict else v])
        if type(v) is dict:
            populate_model_from_dict(m, v, i)
