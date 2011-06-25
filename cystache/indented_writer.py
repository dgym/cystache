from cStringIO import StringIO

class IndentedWriter:
    '''IndentedWriter

    A StringIO like class with a reconfigurable indent
    that is written at the start of every line.
    '''

    def __init__(self, indent = ''):
        self.output = StringIO()
        self.indent = indent
        self.on_new_line = True
    
    def write(self, content):
        if not self.indent or not content:
            return self.output.write(content)

        if self.on_new_line:
            self.output.write(self.indent)

        self.on_new_line = content[-1] == '\n'
        if self.on_new_line:
            self.output.write(content[:-1].replace('\n', '\n' + self.indent) + '\n')
        else:
            self.output.write(content.replace('\n', '\n' + self.indent))

    def getvalue(self):
        return self.output.getvalue()
