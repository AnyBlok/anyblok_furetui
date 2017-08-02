from unittest import TestCase
from ..template import Template, TemplateException
from io import StringIO
from lxml import html


class TestWebTemplate(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestWebTemplate, cls).setUpClass()
        cls.Template = Template()
        cls.compiled = cls.Template.compiled.copy()
        cls.known = cls.Template.known.copy()

    def tearDown(self):
        self.Template.compiled = self.compiled.copy()
        self.Template.known = self.known.copy()

    def format_element(self, element):
        return html.tostring(element).decode("utf-8")

    def test_load_file(self):
        f = StringIO()
        t1 = """<template id='test'><a><b1/><b2/></a></template>"""
        f.write(t1)
        f.seek(0)
        self.Template.load_file(f)
        self.assertEqual(
            self.format_element(self.Template.known['test']['tmpl'][0]),
            '<template id="test"><a><b1></b1><b2></b2></a></template>')

    def test_load_template(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        self.assertEqual(
            self.format_element(self.Template.known['test']['tmpl'][0]),
            '<template id="test"><a><b1></b1><b2></b2></a></template>')

    def test_load_template_for_extend(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression="//b2" action="insertAfter">
                    <b3/>
                </xpath>
            </template>""")
        self.Template.load_template(et)
        self.assertEqual(len(self.Template.known['test']['tmpl']), 2)

    def test_load_template_for_extend_unexisting_template(self):
        et = html.fromstring("""
            <template extend="test">
                <xpath expression="//b2" action="insertAfter">
                    <b3/>
                </xpath>
            </template>""")
        with self.assertRaises(TemplateException):
            self.Template.load_template(et)

    def test_load_template_for_replace_existing_template_ko(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring(
            '<template id="test"><a><c1/><c2/></a></template>')
        with self.assertRaises(TemplateException):
            self.Template.load_template(et)

    def test_load_template_for_replace_existing_template_ok(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring(
            '<template id="test" rewrite="1"><a><c1/><c2/></a></template>')
        self.Template.load_template(et)
        self.assertEqual(
            self.format_element(self.Template.known['test']['tmpl'][0]),
            '<template id="test" rewrite="1">%s</template>' %
            '<a><c1></c1><c2></c2></a>')

    def test_get_xpath(self):
        et = html.fromstring("""
            <template>
                <xpath expression="//a1" action="replace"><b/></xpath>
                <xpath expression="//a2" action="insertBefore"><c/></xpath>
                <xpath expression="//a3" action="insertAfter"><d/></xpath>
            </template>""")
        xpaths = self.Template.get_xpath(et)
        self.assertEqual(len(xpaths), 3)

        def check_xpath(xpath, result):
            self.assertEqual(xpath['expression'], result['expression'])
            self.assertEqual(xpath['action'], result['action'])
            els = [html.tostring(el) for el in xpath['elements']]
            self.assertEqual(els, result['elements'])

        check_xpath(xpaths[0], {'expression': '//a1',
                                'action': 'replace',
                                'elements': [b'<b></b>']})
        check_xpath(xpaths[1], {'expression': '//a2',
                                'action': 'insertBefore',
                                'elements': [b'<c></c>']})
        check_xpath(xpaths[2], {'expression': '//a3',
                                'action': 'insertAfter',
                                'elements': [b'<d></d>']})

    def test_xpath_insertBefore(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insertBefore(
            'test', './/b1', True, [html.fromstring('<b0/>')])
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test">%s</template>' %
            '<a><b0></b0><b1></b1><b2></b2></a>')

    def test_xpath_insertAfter(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insertAfter(
            'test', './/b2', True, [html.fromstring('<b3/>')])
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test">%s</template>' %
            '<a><b1></b1><b2></b2><b3></b3></a>')

    def test_xpath_insert(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_insert(
            'test', './/b2', True, [html.fromstring('<c/>')])
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test">%s</template>' %
            '<a><b1></b1><b2><c></c></b2></a>')

    def test_xpath_replace(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_replace(
            'test', './/b2', True, [html.fromstring('<c/>')])
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test">%s</template>' %
            '<a><b1></b1><c></c></a>')

    def test_xpath_remove(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_remove('test', './/b2', True)
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test"><a><b1></b1></a></template>')

    def test_get_xpath_attributes(self):
        ets = [
            html.fromstring("""<attribute name="test" test="name"/>"""),
            html.fromstring("""<attribute a="b" c="d"/>"""),
        ]
        attributes = self.Template.get_xpath_attributes(ets)
        self.assertEqual(len(attributes), 2)

        self.assertEqual(attributes[0], {'name': 'test', 'test': 'name'})
        self.assertEqual(attributes[1], {'a': 'b', 'c': 'd'})

    def test_xpath_attributes(self):
        self.Template.compiled['test'] = html.fromstring(
            '<template name="test"><a><b1/><b2/></a></template>')
        self.Template.xpath_attributes(
            'test', './/b2', True, {'name': "test"})
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template name="test">%s</template>' %
            '<a><b1></b1><b2 name="test"></b2></a>')

    def test_get_template(self):
        template = '<a><b1></b1><b2></b2></a>'
        self.Template.compiled['test'] = html.fromstring(template)
        self.assertEqual(self.Template.get_template('test'), template)

    def test_get_all_template(self):
        template = '<template name="%s"><a><b1></b1><b2></b2></a></template>'
        self.Template.compiled = {
            'test': html.fromstring(template % 'test'),
            'test2': html.fromstring(template % 'test2'),
        }
        res = ''.join(self.format_element(v)
                      for _, v in self.Template.compiled.items())
        self.assertEqual(self.Template.get_all_template(), res)

    def test_compile_the_same_template(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression='.//b1' action="insert"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template id="test">%s</template>' %
            '<a><b1><c></c></b1><b2></b2></a>')

    def test_compile_with_extend_another_template(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test" id="test2">
                <xpath expression='.//b1' action="insert"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template id="test">%s</template>' %
            '<a><b1></b1><b2></b2></a>')
        self.assertEqual(
            self.format_element(self.Template.compiled['test2']),
            '<template id="test2">%s</template>' %
            '<a><b1><c></c></b1><b2></b2></a>')

    def test_compile_the_same_template_and_extend_it(self):
        et = html.fromstring(
            '<template id="test"><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test" id="test2">
                <xpath expression='.//b1' action="insert"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        et = html.fromstring("""
            <template extend="test">
                <xpath expression='.//b2' action="insert"><c/></xpath>
            </template>""")
        self.Template.load_template(et)
        self.Template.compile()
        self.assertEqual(
            self.format_element(self.Template.compiled['test']),
            '<template id="test">%s</template>' %
            '<a><b1></b1><b2><c></c></b2></a>')
        self.assertEqual(
            self.format_element(self.Template.compiled['test2']),
            '<template id="test2">%s</template>' %
            '<a><b1><c></c></b1><b2><c></c></b2></a>')

    def test_html_attribute(self):
        et = html.fromstring(
            '<template id="test" test><a><b1/><b2/></a></template>')
        self.Template.load_template(et)
        self.assertEqual(
            self.format_element(self.Template.known['test']['tmpl'][0]),
            '<template id="test" test><a><b1></b1><b2></b2></a></template>')

    def test_html_no_ending_tag(self):
        et = html.fromstring(
            '<template id="test"><a><b1></a></template>')
        self.Template.load_template(et)
        self.assertEqual(
            self.format_element(self.Template.known['test']['tmpl'][0]),
            '<template id="test"><a><b1></b1></a></template>')
