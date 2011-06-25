from cgi import escape

from context import Context

class Block:
    def __init__(self, template, start, end):
        self.template = template
        self.start = start
        self.end = end

    def render(self, context, output):
        pass

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
    def render(self, context, output):
        output.write(self.template.source[self.start:self.end])

class TaggedBlock(Block):
    def __init__(self, template, start, end, tag):
        Block.__init__(self, template, start, end)
        self.tag = tag.strip()

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.tag)

class ValueBlock(TaggedBlock):
    def render(self, context, output):
        value = self.resolve_value(context)
        output.write(escape(unicode(value)).replace('"', '&quot;'))

class UnquotedValueBlock(TaggedBlock):
    def render(self, context, output):
        value = self.resolve_value(context)
        output.write(unicode(value))

class SectionBlock(TaggedBlock):
    def __init__(self, template, start, end, tag, parent, otag = '{{', ctag = '}}'):
        TaggedBlock.__init__(self, '', start, end, tag)
        self.template = template
        self.parent = parent
        self.otag = otag
        self.ctag = ctag
        self.blocks = []
        self.inner_start = 0
        self.inner_end = -1

    def render(self, context, output):
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
                        block.render(inner_context, output)
            else:
                inner_context = Context(value, context)
                for block in self.blocks:
                    block.render(inner_context, output)

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.tag, self.blocks)

class InverseSectionBlock(SectionBlock):
    def render(self, context, output):
        value = context.get(self.tag)
        if callable(value):
            # Call the function as it is expected
            value = value(self.template.source[self.inner_start:self.inner_end])
            # But there is nothing to do, the output is only rendered
            # if it doesn't exist
        elif not value:
            for block in self.blocks:
                block.render(Context(value, context), output)


class PartialBlock(TaggedBlock):
    def __init__(self, template, start, end, tag, partial):
        TaggedBlock.__init__(self, template, start, end, tag)
        self.partial = partial
        self.indent = ''

    def render(self, context, output):
        indent = output.indent
        output.indent = self.indent
        try:
            self.partial.compile()
            self.partial._render(context, output)
        finally:
            output.indent = indent
