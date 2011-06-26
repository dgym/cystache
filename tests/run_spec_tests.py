import json
import traceback
import sys
import bdb
from cystache import Template, Loader

def make_lambdas(d):
    for k, v, in d.items():
        if isinstance(v, dict) and v.get('__tag__') == 'code':
            d[k] = eval(v['python'])
    return d

class Stats:
    def __init__(self):
        self.passed = 0
        self.failed = 0

def run_tests(filename, stats):
    f = open(filename, 'r')
    try:
        data = json.load(f)
    finally:
        f.close()

    for test in data['tests']:
        try:
            template = Template(test['template'], Loader(test.get('partials', {})))
            output = template.render(make_lambdas(test['data']))
            if output != test['expected']:
                raise Exception('%s != %s' % (repr(output), repr(test['expected'])))
            sys.stdout.write('.')
            stats.passed += 1
        except bdb.BdbQuit, e:
            break
        except:
            print
            print '==== FAILED ===='
            print '%s - %s' % (test['name'], test['desc'])
            traceback.print_exc()
            print
            stats.failed += 1
    print

if __name__ == '__main__':        
    stats = Stats()
    for filename in sys.argv[1:]:
        run_tests(filename, stats)
    print 'Passed %i failed %i - %i total tests' % (stats.passed, stats.failed, stats.passed + stats.failed)
