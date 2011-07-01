import cython

cdef class Context:
    cdef public object data
    cdef public bint is_dict
    cdef public Context parent

    @cython.locals(parts = list)
    cpdef object get(Context self, unicode key)
