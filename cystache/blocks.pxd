from reader cimport Reader
cimport template

cdef class Block:
    cdef template.Template template
    cdef int start
    cdef bint starts_on_newline

cdef class StaticBlock(Block):
    cdef int end

cdef class TaggedBlock(Block):
    cdef public str tag

cdef class ValueBlock(TaggedBlock):
    pass

cdef class UnquotedValueBlock(TaggedBlock):
    pass

cdef class SectionBlock(TaggedBlock):
    cdef public object parent
    cdef public str otag
    cdef public str ctag
    cdef public list blocks
    cdef public int inner_start
    cdef public int inner_end

cdef class InverseSectionBlock(SectionBlock):
    pass

cdef class PartialBlock(TaggedBlock):
    cdef object partial
    cdef str indent
