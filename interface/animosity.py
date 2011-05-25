import re
def autodetect(path):
    return re.search(r'(?i)\.level$', path) is not None

import modes
modes.register(['Level', 'Animosity'], None, autodetect, None, None)
