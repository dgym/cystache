cdef class Reader:
    cdef public str source
    cdef int start
    cdef public int end
    cdef int idx
    cdef public int tag_start
    cdef public int tag_end
    cdef public int tag_inner_start, tag_inner_end
    cdef bint _is_standalone
    cdef bint _standalone_scanned
    cdef int _indent_length
    cdef int _trailing_whitespace_length
    cdef public int static_start
    cdef public bint static_on_newline

    cpdef int get_start_idx(self)
    cpdef int find_opening_tag(self, str)
    cpdef int skip_over(self, str)
    cpdef int find_closing_tag(self, str)
    cpdef never_standalone(self)
    cpdef bint is_standalone(self)
    cpdef int get_indent_length(self)
    cpdef str get_indent(self)
    cpdef int get_trailing_whitespace_length(self)
