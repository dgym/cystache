from cgi import escape

from context import Context

class Block:
    def __init__(self, template, reader):
        self.template = template
        self.start = reader.tag_start
        self.starts_on_newline = False

    def render(self, context, output, rs):
        if self.starts_on_newline and rs.indent:
            output.write(rs.indent)
        self._render(context, output, rs)

    def resolve_value(self, context, getarg = None):
        value = context.get(self.tag)
        if callable(value):
            if getarg:
                args = getarg(),
            else:
                args = ()
            value = value(*args)
            if isinstance(value, basestring):
                template =  self.template.__class__(value, self.template.loader)
                value = template.render(context)
        return value

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

class StaticBlock(Block):
    def __init__(self, template, reader):
        Block.__init__(self, template, reader)
        self.template = template
        self.start = reader.static_start
        if reader.is_standalone():
            self.end = reader.tag_start - reader.get_indent_length()
        else:
            self.end = reader.tag_start
        self.starts_on_newline = reader.static_on_newline

    def _render(self, context, output, rs):
        if rs.indent:
            content = self.template.source[self.start:self.end-1].replace('\n', '\n' + rs.indent)
            output.write(content + self.template.source[self.end-1:self.end])
        else:
            output.write(self.template.source[self.start:self.end])

class TaggedBlock(Block):
    def __init__(self, template, reader, tag):
        Block.__init__(self, template, reader)
        self.tag = tag.strip()
        self.starts_on_newline = (not reader.is_standalone()) and reader.get_indent_length() >= 0

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.tag)

class ValueBlock(TaggedBlock):
    def _render(self, context, output, rs):
        value = self.resolve_value(context)
        output.write(escape(unicode(value)).replace('"', '&quot;'))

class UnquotedValueBlock(TaggedBlock):
    def _render(self, context, output, rs):
        value = self.resolve_value(context)
        output.write(unicode(value))

class SectionBlock(TaggedBlock):
    def __init__(self, template, reader, tag, parent, otag = '{{', ctag = '}}'):
        TaggedBlock.__init__(self, template, reader, tag)
        self.template = template
        self.parent = parent
        self.otag = otag
        self.ctag = ctag
        self.blocks = []
        self.inner_start = reader.tag_end
        self.inner_end = -1

    def _render(self, context, output, rs):
        value = context.get(self.tag)
        if callable(value):
            value = value(self.template.source[self.inner_start:self.inner_end])
            if isinstance(value, basestring):
                template =  self.template.__class__(value, self.template.loader)
                template.compile(self.otag, self.ctag)
                value = template.render(context)
            output.write(value)
        elif value:
            if hasattr(value, '__iter__') and not isinstance(value, dict):
                for v in value:
                    inner_context = Context(v, context)
                    for block in self.blocks:
                        block.render(inner_context, output, rs)
            else:
                inner_context = Context(value, context)
                for block in self.blocks:
                    block.render(inner_context, output, rs)

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.tag, self.blocks)

class InverseSectionBlock(SectionBlock):
    def _render(self, context, output, rs):
        value = context.get(self.tag)
        if callable(value):
            # Call the function as it is expected
            value = value(self.template.source[self.inner_start:self.inner_end])
            # But there is nothing to do, the output is only rendered
            # if it doesn't exist
        elif not value:
            for block in self.blocks:
                block.render(Context(value, context), output, rs)


class PartialBlock(TaggedBlock):
    def __init__(self, template, reader, tag, partial):
        TaggedBlock.__init__(self, template, reader, tag)
        self.partial = partial
        self.indent = reader.get_indent()

    def _render(self, context, output, rs):
        indent = rs.indent
        rs.indent += self.indent
        try:
            self.partial.compile()
            self.partial._render(context, output, rs)
        finally:
            rs.indent = indent
