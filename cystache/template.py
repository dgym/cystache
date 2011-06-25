from indented_writer import IndentedWriter
from context import Context
from blocks import *

class Template:
    def __init__(self, source, loader = None, filename = None, compile = True):
        self.source = source
        self.loader = loader
        self.filename = filename
        self.section = SectionBlock(self, 0, len(source), '', None, '{{', '}}')
        self.compiled = False

    def compile(self, otag = '{{', ctag = '}}'):
        if self.compiled:
            return True

        source = self.source
        start = 0
        end = len(source)
        l_otag = len(otag)
        l_ctag = len(ctag)
        section = self.section
        source_start = start

        while True:
            idx = source.find(otag, start, end)
            if idx == -1:
                # end of file
                if start < end:
                    section.blocks.append(StaticBlock(self, start, end))
                if section != self.section:
                    unclosed = []
                    while section != self.section:
                        unclosed.append(section.tag)
                        section = section.parent
                    raise SyntaxError('Unclosed sections : %s' % ' '.join(unclosed))
                self.compiled = True
                return True

            # write untagged content, remembering the last_static
            # as it may need to be trimmed on standalone tag lines
            if start < idx:
                last_static = StaticBlock(self, start, idx)
                section.blocks.append(last_static)
            else:
                last_static = None
            tag_start = idx
            start = idx + l_otag

            # examine the control character
            if start >= end:
                raise SyntaxError('Premature end of script')

            control = source[start]
            if control == '{':
                idx = source.find('}', start, end) + 1
            elif control == '=':
                idx = source.find('=', start, end) + 1
            else:
                idx = start

            if idx == -1:
                raise SyntaxError('Premature end of script')

            # scan for ctag
            idx = source.find(ctag, idx, end)
            if idx == -1:
                raise SyntaxError('Premature end of script')

            tag = source[start:idx]

            # strip out the line 
            tag_end = idx + l_ctag
            strip_line = False

            if control == '#':
                new_section = SectionBlock(self, start, idx, tag[1:], section, otag, ctag)
                new_section.inner_start = tag_end
                section.blocks.append(new_section)
                section = new_section
                strip_line = True
            elif control == '^':
                new_section = InverseSectionBlock(self, start, idx, tag[1:], section)
                section.blocks.append(new_section)
                section = new_section
                strip_line = True
            elif control == '/':
                if not section.parent:
                    raise SyntaxError('Unmatched closing tag %s at top level' % repr(tag))
                tag = tag[1:].strip()
                if tag != section.tag:
                    raise SyntaxError('Unmatched closing tag %s, expecting %s' % (repr(tag), repr(section.tag)))
                if isinstance(section, SectionBlock):
                    section.inner_end = tag_start
                section = section.parent
                strip_line = True
            elif control == '=':
                otag, ctag = tag[1:-1].split()
                l_otag = len(otag)
                l_ctag = len(ctag)
                strip_line = True
            elif control == '{':
                section.blocks.append(UnquotedValueBlock(self, start, idx, tag[1:-1]))
            elif control == '&':
                section.blocks.append(UnquotedValueBlock(self, start, idx, tag[1:]))
            elif control == '!':
                # comment
                strip_line = True
            elif control == '>':
                # partial
                section.blocks.append(PartialBlock(self, start, idx, tag[1:],
                    self.loader.load(tag[1:].strip(), self.filename)))
                strip_line = True
            else:
                section.blocks.append(ValueBlock(self, start, idx, tag))

            if strip_line:
                # strip standalone tags
                standalone_before = source_start
                for i in range(tag_start-1, source_start-1, -1):
                    c = source[i] 
                    if c == '\r' or c == '\n':
                        standalone_before = i + 1
                        break
                    elif c == ' ' or c == '\t':
                        continue
                    standalone_before = -1
                    strip_line = False
                    break

            if strip_line:
                standalone_after = end
                for i in range(tag_end, end):
                    c = source[i] 
                    if c == '\r':
                        i += 1
                        if i < end and source[i] == '\n':
                            standalone_after = i + 1
                        else:
                            standalone_after = i
                        break
                    elif c == '\n':
                        standalone_after = i + 1
                        break
                    elif c == ' ' or c == '\t':
                        continue
                    strip_line = False
                    standalone_after = -1
                    break

            if strip_line:
                if control == '>':
                    section.blocks[-1].indent = source[standalone_before:tag_start]
                if last_static:
                    last_static.end = standalone_before
                start = standalone_after
            else:
                start = tag_end

    def render(self, context_or_dict, output = None):
        if not self.compiled:
            self.compile()

        if isinstance(context_or_dict, Context):
            context = context_or_dict
        else:
            context = Context(context_or_dict)

        output = IndentedWriter()

        self._render(context, output)

        return unicode(output.getvalue())

    def _render(self, context, output):
        for block in self.section.blocks:
            block.render(context, output)
