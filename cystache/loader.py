from template import Template

class Loader:
    '''Loader

    Loads templates, including partials.
    
    This base classes loads templates from a supplied dictionary.'''

    def __init__(self, templates = None):
        self.templates = templates or {}

    def load(self, tag, source_filename):
        template = self.templates[tag]
        if not isinstance(template, Template):
            template = Template(template, self, filename = '<internal>', compile = False)
            self.templates[tag] = template
        return template
