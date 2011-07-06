import unittest
from cystache import Template, Loader

class TestSimple(unittest.TestCase):
    def assertRender(self, template, output, **context):
        self.assertEqual(Template(template).render(context), output)

    def test_conditional(self):
        self.assertEqual(
                Template('({{#name}}{{name}}{{/name}}{{^name}}{{alt}}{{/name}})').render({'name': 'a name'}),
                '(a name)')
        self.assertEqual(
                Template('({{#name}}{{{.}}}{{/name}}{{^name}}{{alt}}{{/name}})').render({'alt': 'another name'}),
                '(another name)')

    def test_single_item_list(self):
        l = Loader({
            'outer': 'A colour: {{#colours}}{{>speed_colour_row}}{{/colours}}.',
            'speed_colour_row': '<li>{{name}} - {{#price}}${{price}}{{/price}}{{^price}}free!{{/price}}</li>',
            })
        self.assertEqual(
                l.load('outer', '').render({'colours': [{'name': 'colour 42', 'price': 52}]}),
                'A colour: <li>colour 42 - $52</li>.')

    def test_zero(self):
        self.assertRender('{{v}}', '0', v='0')

    def test_lambda_list(self):
        self.assertRender('{{#l}}{{.}},{{/l}}', '1,2,3,', l=lambda x:[1,2,3])

if __name__ == '__main__':
    unittest.main()

