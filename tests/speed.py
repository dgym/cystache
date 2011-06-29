from cystache import Template, Loader

class FileLoader(Loader):
    def load(self, tag, source_filename = None):
        if tag in self.templates:
            template = self.templates[tag]
        else:
            filename = 'tests/templates/%s.mustache' % tag
            f = open(filename, 'r')
            try:
                template = Template(f.read(), self, filename = '<internal>')
            finally:
                f.close()
        return template

context = {}
context['vgs_intro'] = '''
Hello, and welcome to the <b>virtual goods store</b>.
All orders come with free packaging and postage.'''
context['emotions'] = [ {'name': 'emotion %i' % i} for i in range(50) ]
context['colours'] = [ {'name': 'colour %i' % i, 'price': i} for i in range(50) ]
context['previous_order'] = {
        'items': [ {'name': 'item %i' % i, 'price': i, 'quantity': i + 10} for i in range(50) ],
}


loader = FileLoader()
# preload
def run():
    return loader.load('speed').render(context)
print run()

def report(proc, count):
    import timeit
    seconds = timeit.timeit(proc, number=count)
    print '%i runs in %f seconds - %f runs per second' % (count, seconds, count / seconds)
report(run, 50)
