# cython: profile=False

import cython
from reader cimport Reader
from render_state cimport RenderState
cimport template

cdef unicode escape(unicode s)

cdef class Block:
    cdef template.Template template
    cdef int start
    cdef bint starts_on_newline

    cpdef render(self, object context, object output, RenderState rs)
    cdef _render(self, object context, object output, RenderState rs)

cdef class StaticBlock(Block):
    cdef int end

cdef class TaggedBlock(Block):
    cdef public unicode tag

cdef class ValueBlock(TaggedBlock):
    pass

cdef class UnquotedValueBlock(TaggedBlock):
    pass

cdef class SectionBlock(TaggedBlock):
    cdef public object parent
    cdef public unicode otag
    cdef public unicode ctag
    cdef public list blocks
    cdef public int inner_start
    cdef public int inner_end

cdef class InverseSectionBlock(SectionBlock):
    pass

cdef class PartialBlock(TaggedBlock):
    cdef object partial
    cdef unicode indent
