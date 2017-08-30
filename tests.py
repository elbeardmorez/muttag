
try:
    import pyflakes
except ImportError:
    raise SystemExit("pyflakes missing")

try:
    import pep8
except ImportError:
    raise SystemExit("pep8 missing")

import os
import glob

path = os.path.dirname(os.path.realpath(__file__))
files = glob.glob(os.path.join(path, '*.py'))

cmd = str('pyflakes %s' % ' '.join(files))
print "# running pyflakes:\n%s" % cmd
os.system(cmd)
cmd = str('pep8 %s' % ' '.join(files))
print "# running pep8:\n%s" % cmd
os.system(cmd)
