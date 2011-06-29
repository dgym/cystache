#!/usr/bin/env python

from distutils.core import setup

kwargs = {
    'name': 'cystache',
    'version': '0.1',
    'description': 'Cython implementation of the Mustache templating language.',
    'author': 'Jim Bailey',
    'author_email': 'dgym.bailey@gmail.com',
    'url': 'http://github.com/dgym/cystache',
    'packages': [
        'cystache'
    ],
}

try:
    from Cython.Distutils import build_ext
    from Cython.Distutils.extension import Extension

    kwargs['cmdclass'] = {'build_ext': build_ext}
    kwargs['ext_modules'] = [
        Extension('cystache.reader',['cystache/reader.py']),
        Extension('cystache.blocks',['cystache/blocks.py']),
        Extension('cystache.context',['cystache/context.py']),
        Extension('cystache.render_state',['cystache/render_state.py']),
        Extension('cystache.template',['cystache/template.py']),
        Extension('cystache.loader',['cystache/loader.py']),
    ]
    kwargs['py_modules'] = [
        'cystache.__init__'
    ]
    del kwargs['packages']
except:
    print 'PERFORMANCE WARNING - cython not found, pure python modules being used instead'

setup(**kwargs)
