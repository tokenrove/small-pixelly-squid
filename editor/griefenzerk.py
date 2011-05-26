import re, cPickle, os
from editor import model, tilemap

class LevelModel(model.Model):
    def __init__(self, name=None, path=None, rooms=None, **kwds):
        model.Model.__init__(self, **kwds)
        self.path, self.name, self.rooms = path, name, rooms
        if self.name is None: self.name = '*unnamed*' if path is None else os.path.basename(path)
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
            with open(self.path, "w") as f:
                cPickle.dump({'magic':'Berzerk', 'rooms':self.rooms}, f)
            self.has_unsaved_changes = False
        except IOError: return

class RoomModel(tilemap.GenericModel):
    def __init__(self, parent=None, id=None, **kwds):
        tilemap.GenericModel.__init__(self, **kwds)
        self.parent = parent
        self.id = id

    @classmethod
    def from_room(cls, parent, id):
        room = parent.rooms[id]
        name = '%s [%d]' % (parent.name,id)
        return cls(name=name, parent=parent, id=id,
                   dimensions=room['dim'], grid_size=(16,16), map=room['map'],
                   slab_path=os.path.join(os.path.dirname(parent.path), room['slab']))

    def save(self): self.parent.save()

    def _propagate_unsaved_changes(self, v):
        if v is False: self.parent.has_unsaved_changes = v
    has_unsaved_changes = property(lambda self:self.parent.has_unsaved_changes,
                                   _propagate_unsaved_changes)


def autodetect(path):
    if re.match(r'(?i)\.lev$', os.path.splitext(path)[1]) is None: return False
    with open(path) as f:
        try:
            level = cPickle.load(f)
            return level['magic'] == 'Berzerk'
        except: return False

