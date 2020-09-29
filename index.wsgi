#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Assuming index.wsgi (this file) is placed at the top product directory 
#sys.path.insert(0,"/var/www/impassport/")
im_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,im_dir)


def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

# execute the file
activate_this = '/home/vee/impenv/bin/activate_this.py'
execfile(activate_this)
#  format changed in python3 execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read())

from im_pass import app as application
