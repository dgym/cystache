from reader cimport Reader
import cython

cdef class Template:
    cdef public unicode source
    cdef public object loader
    cdef public unicode filename
    cdef bint compiled
    cdef object section

    @cython.locals(reader = Reader)
    cdef bint _compile(self, unicode otag, unicode ctag) except *
    #cpdef unicode render(self, object, object)
    #cpdef _render(self, object, object, object)

