import cython

cdef class ContextManager:
    cdef object context
    cdef object template
    cdef object thread_storage

    cdef _set_current_context(self, object context)
    cdef _set_current_template(self, object template)
