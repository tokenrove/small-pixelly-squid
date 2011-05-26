
import gtk, sys

from interface import modes
# base modes
from interface import tilemap, image
# project-specific modes
from interface import griefenzerk, animosity

from interface import toplevel
def main():
    toplevel.TopLevel(argv = sys.argv)
    gtk.main()
