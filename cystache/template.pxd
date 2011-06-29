from reader cimport Reader
import cython

cdef class Template:
    cdef public str source
    cdef public object loader
    cdef public str filename
    cdef bint compiled
    cdef object section

    @cython.locals(reader = Reader)
    cpdef bint compile(self, str otag=*, str ctag=*)
    #cpdef unicode render(self, object, object)
    #cpdef _render(self, object, object, object)

