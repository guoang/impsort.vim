from __future__ import print_function, unicode_literals

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jedi'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'parso'))

import jedi
from jedi import settings

# Setting a cache for impsort.  It appears that the caches aren't compatible
# across different versions.
venv = os.getenv('VIRTUAL_ENV', '')
if venv:
    venv = os.path.basename(venv)

cache_dir = os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
cache_dir = os.path.join(cache_dir, 'jedi', 'impsort', venv +
                         '.'.join(str(x) for x in sys.version_info[:3]))

settings.cache_directory = cache_dir


def get_names(filename, source):
    # Workaround for forcing an empty function scope on Jedi
    source += '\n\ndef __impsort_fake__():\n    pass\n'
    script = jedi.Script(source, line=len(source.split('\n')), column=0, path=filename)

    for c in script.completions():
        if c.name == '__impsort_fake__' or c.is_keyword \
                or c.in_builtin_module():
            continue
        if c.type != 'module':
            print('%s,%s' % (c.name, c.type))
        elif c.get_line_code().find('from ') != -1:
            print('%s,%s' % (c.name, c.type))

    for i in script._get_module_node().iter_imports():
        if i.type == 'import_name':
            for full, alias in i._dotted_as_names():
                if alias:
                    print('%s,%s' % (alias.value, 'module'))
                else:
                    print('%s,%s' % ('.'.join([n.value for n in full]), 'module'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    source = sys.stdin.read()
    if not source:
        with open(sys.argv[1], 'rt') as fp:
            source = fp.read()

    get_names(sys.argv[1], source)
