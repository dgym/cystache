from cStringIO import StringIO

from context import Context
from render_state import RenderState
from reader import Reader
from blocks import *

class Template:
    def __init__(self, source, loader = None, filename = None, compile = True):
        self.source = unicode(source)
        self.loader = loader
        self.filename = unicode(filename)
        self.compiled = False

    def compile(self, otag = u'{{', ctag = u'}}'):
        return self._compile(unicode(otag), unicode(ctag))

    def _compile(self, otag, ctag):
        if self.compiled:
            return True

        reader = Reader(self.source)
        self.section = SectionBlock(self, reader, u'', None, u'{{', u'}}')
        section = self.section

        while True:
            last_idx = reader.get_start_idx()

            # first find the next opening tag
            if not reader.find_opening_tag(otag):
                # end of file
                if last_idx < reader.end:
                    section.blocks.append(StaticBlock(self, reader))
                if section != self.section:
                    unclosed = []
                    while section != self.section:
                        unclosed.append(section.tag)
                        section = section.parent
                    raise SyntaxError('Unclosed sections : %s' % ' '.join(unclosed))
                self.compiled = True
                return True

            # examine the control character as it affects the end tag
            if reader.tag_inner_start >= reader.end:
                raise SyntaxError('Premature end of script')

            control = reader.source[reader.tag_inner_start]
            if control == u'{':
                reader.skip_over(u'}')
            elif control == u'=':
                reader.skip_over(u'=')

            # now find the closing tag
            if not reader.find_closing_tag(ctag):
                raise SyntaxError('Premature end of script')

            # untagged content can change depending on whether the tag
            # is standalone, so just store the information to write it
            add_static_to = section.blocks
            static_idx = len(section.blocks)

            tag = reader.source[reader.tag_inner_start:reader.tag_inner_end]

            if control == u'#':
                new_section = SectionBlock(self, reader, tag[1:], section, otag, ctag)
                section.blocks.append(new_section)
                section = new_section
            elif control == u'^':
                new_section = InverseSectionBlock(self, reader, tag[1:], section)
                section.blocks.append(new_section)
                section = new_section
            elif control == u'/':
                if not section.parent:
                    raise SyntaxError('Unmatched closing tag %s at top level' % repr(tag))
                tag = tag[1:].strip()
                if tag != section.tag:
                    raise SyntaxError('Unmatched closing tag %s, expecting %s' % (repr(tag), repr(section.tag)))
                section.inner_end = reader.tag_start
                section = section.parent
            elif control == u'=':
                otag, ctag = tag[1:-1].split()
            elif control == u'{':
                reader.never_standalone()
                section.blocks.append(UnquotedValueBlock(self, reader, tag[1:-1]))
            elif control == u'&':
                reader.never_standalone()
                section.blocks.append(UnquotedValueBlock(self, reader, tag[1:]))
            elif control == u'!':
                # comment
                pass
            elif control == u'>':
                # partial
                partial = PartialBlock(self, reader, tag[1:],
                    self.loader.load(tag[1:].strip(), self.filename))
                section.blocks.append(partial)
            else:
                reader.never_standalone()
                section.blocks.append(ValueBlock(self, reader, tag))

            # now insert the static content
            add_static_to.insert(static_idx, StaticBlock(self, reader))

    def render(self, context_or_dict, output = None):
        if not self.compiled:
            self.compile()

        if isinstance(context_or_dict, Context):
            context = context_or_dict
        else:
            context = Context(context_or_dict)

        output = StringIO()
        rs = RenderState()

        self._render(context, output, rs)

        return unicode(output.getvalue())

    def _render(self, context, output, rs):
        for block in self.section.blocks:
            block.render(context, output, rs)
