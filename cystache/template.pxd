# cython: profile=False

import cython
from reader cimport Reader

cdef class Template:
    cdef public unicode source
    cdef public object loader
    cdef public object filename
    cdef bint compiled
    cdef object section

    @cython.locals(reader = Reader)
    cdef bint _compile(Template self, unicode otag, unicode ctag) except *
    #cpdef unicode render(self, object, object)
    #cpdef _render(self, object, object, object)
