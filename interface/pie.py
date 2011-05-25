"""Simple GTk pie menus for Small Pixelly Squid.

Distilled by Julian Squires from the much more complex implementation
by Don Hopkins. (http://www.donhopkins.com/drupal/taxonomy_menu/4/49/14/18)
"""

import gtk, gobject, cairo, pango, math
from gtk import gdk

two_pi = 2*math.pi

def mouse_arc(x,y,r): return math.atan2(y/r, x/r) % two_pi

class Menu(gtk.Window):
    desired_width, desired_height = 250,250

    def __init__(self, items, **kwds):
        gtk.Window.__init__(self, type=gtk.WINDOW_POPUP)
        self.set_default_size(self.desired_width, self.desired_height)
        self.set_has_frame(False)
        self.set_decorated(False)
        self.set_opacity(0.5)
        self._pango_context = self.create_pango_context()
        self._pango_layout = pango.Layout(self._pango_context)
        self._area = gtk.DrawingArea()
        self.add(self._area)
        mask = 0
        self.connect("show", self.draw)
        for (ev,fn,m) in (('expose_event',self.draw,gdk.EXPOSURE_MASK),
                         ('motion_notify_event',self.on_motion,gdk.POINTER_MOTION_HINT_MASK),
                         ('button_press_event',self.on_button_press,gdk.BUTTON_PRESS_MASK),
                         ('button_release_event',self.on_button_release,gdk.BUTTON_RELEASE_MASK)):
            self.connect(ev, fn)
            self._area.connect(ev, fn)
            mask |= m
        self.set_events(self.get_events()|m)
        self._area.set_events(self._area.get_events()|m)
        self.valid = False
        self.items = items
        self.button_active = False
        self.active_action = None

    def invalidate(self): self.valid = False

    def do_size_allocate(self, allocation):
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_size_request(self, requisition):
        requisition.width, requisition.height = self.desired_width, self.desired_height

    def popup(self, x, y):
        self.move(int(x-self.desired_width/2),int(y-self.desired_height/2))
        self.active_action = None
        self.queue_draw()
        self.show_all()
        if self.allocation:
            _,_,w,h = self.allocation
            self.move(int(x-w/2),int(y-h/2))
        self._area.grab_add()
        self._area.grab_focus()
        gtk.gdk.pointer_grab(
            self._area.window,
            True,
            gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.ENTER_NOTIFY_MASK |
            gtk.gdk.LEAVE_NOTIFY_MASK |
            gtk.gdk.POINTER_MOTION_MASK)

    def popdown(self):
        self._area.grab_remove()
        gtk.gdk.pointer_ungrab()
        self.hide()

    def draw(self, widget, event=None, *args):
        x,y,w,h = self.allocation
        cr = widget.window.cairo_create()

        (mx,my,_) = widget.window.get_pointer()
        mx -= x+w/2
        my -= y+h/2

        if event is not None:
            cr.rectangle(event.area)
            cr.clip()

        r = w/2-10
        cr.arc(w/2, h/2, r, 0, two_pi)
        cr.set_source_color(self.style.bg[gtk.STATE_INSENSITIVE])
        cr.fill()
        #cr.set_source_color(self.style.fg[gtk.STATE_NORMAL])
        #cr.stroke()

        inactive_radius = 15
        step = two_pi/len(self.items)
        mtheta = math.atan2(my/r, mx/r) % two_pi
        outside_center_p = mx**2+my**2 >= inactive_radius**2
        for (i,(label,action)) in enumerate(self.items):
            selected = mtheta >= i*step and mtheta <= (i+1)*step and outside_center_p
            if selected: self.active_action = action
            state = gtk.STATE_PRELIGHT if selected else gtk.STATE_NORMAL if outside_center_p else gtk.STATE_INSENSITIVE
            if state == gtk.STATE_PRELIGHT and self.button_active: state = gtk.STATE_ACTIVE
            cr.move_to(w/2,h/2)
            cr.arc(w/2, h/2, r, i*step, (i+1)*step)
            cr.close_path()
            cr.set_source_color(self.style.bg[state])
            cr.fill_preserve()
            cr.set_source_color(self.style.dark[state])
            cr.stroke()
            self._pango_layout.set_markup(label)
            (lw,lh) = self._pango_layout.get_pixel_size()
            ltheta = i*step+step/2
            cr.move_to(w/2+(r/2)*math.cos(ltheta)-lw/2, h/2+(r/2)*math.sin(ltheta)-lh/2)
            cr.set_source_color(self.style.fg[state])
            cr.show_layout(self._pango_layout)

        # draw the inactive center area
        cr.new_path()
        cr.arc(w/2, h/2, inactive_radius, 0, two_pi)
        if not outside_center_p: self.active_action = None
        state = gtk.STATE_INSENSITIVE if outside_center_p else gtk.STATE_PRELIGHT
        if state == gtk.STATE_PRELIGHT and self.button_active: state = gtk.STATE_ACTIVE
        cr.set_source_color(self.style.bg[state])
        cr.fill_preserve()
        cr.set_source_color(self.style.fg[state])
        cr.stroke()

        return True

    def on_motion(self, widget, event):
        # update selected item
        # if selection has changed,
        self.queue_draw()
        return False

    def on_button_press(self, *args):
        self.button_active = True
        self.queue_draw()
        return False

    def on_button_release(self, *args):
        self.button_active = False
        self.popdown()
        if self.active_action is not None: self.active_action()
        return True


#### TEST CODE

_menu_pop_position = (0,0)
def _on_key_press(widget, event):
    print 'got %s' % event.keyval
    if event.keyval != ord('f'): return False
    menu = Menu([('New',None), ('Open',None), ('Quit',gtk.main_quit)])
    menu.popup(*_menu_pop_position)
    return True

def _on_motion_notify(widget, event):
    global _menu_pop_position
    _menu_pop_position = event.get_root_coords()
    return False

def _main():
    w = gtk.Window()
    w.set_position(gtk.WIN_POS_CENTER)
    w.connect('destroy', lambda w:gtk.main_quit())
    w.connect('key_press_event', _on_key_press)
    w.connect('motion_notify_event', _on_motion_notify)
    w.set_events(w.get_events()|gdk.POINTER_MOTION_MASK)
    fr = gtk.Frame()
    w.add(fr)
    fr.add(gtk.Label('Nothing here.'))
    w.show_all()
    gtk.main()

if __name__ == "__main__": _main()
