
import gtk, sys

import modes
# base modes
import tilemap, image
# project-specific modes
import griefenzerk, animosity

import toplevel
def main():
    toplevel.TopLevel(argv = sys.argv)
    gtk.main()
