from lxml import html, etree
from copy import deepcopy
from logging import getLogger

logger = getLogger(__name__)


class TemplateException(Exception):
    pass


class Template:
    """ html templating framework, the need is to manipulate web template.

    ::

        tmpl = Template()
        tmpl.load_file(file_pointer_1)
        tmpl.load_file(file_pointer_2)
        tmpl.load_file(file_pointer_3)
        tmpl.load_file(file_pointer_N)
        tmpl.compîle()
        tmpl.get_all_template()

    """

    def __init__(self, *args, **kwargs):
        if 'forclient' in kwargs:
            self.forclient = kwargs.pop('forclient')
        else:
            self.forclient = False

        super(Template, self).__init__(*args, **kwargs)
        self.clean()

    def clean(self):
        """ Erase all the known templates """
        self.compiled = {}
        self.known = {}

    def get_all_template(self):
        """ Return all the template in string format """
        res = []
        for tmpl in self.compiled.keys():
            res.append(self.get_template(tmpl))

        res = ''.join(res)
        return res.strip()

    def get_template(self, name, tostring=True, first_children=False):
        """return a specific template

        :param name: name of the template
        :rtype: str
        """
        tmpl = deepcopy(self.compiled[name])
        if self.forclient:
            tmpl.tag = 'script'
            if tmpl.attrib.get('type') is None:
                tmpl.set('type', 'text/html')
        elif first_children:
            tmpl = tmpl.getchildren()[0]

        if tostring:
            res = html.tostring(tmpl)
            return self.decode(res.decode("utf-8"))

        return tmpl

    def decode(self, element):
        """ Decode some element need for the web template

        :param element: string representation of the element
        :rtype: str
        """
        return element

    def encode(self, element):
        """ Encode the templating commande

        :param element: string representation of the element
        :rtype: str
        """
        return element

    def load_file(self, openedfile):
        """ Load a file

        File format ::

            <templates>
                <template id="...">
                    ...
                </template>
            </templates>

        :param openedfile: file descriptor
        :exception: TemplateException
        """
        try:
            el = openedfile.read()
            # the operator ?= are cut, then I replace them before
            # to save the operator in get_template
            element = html.fromstring(self.encode(el))
        except Exception:
            logger.error('error durring load of %r' % openedfile)
            raise

        if element.tag.lower() == 'template':
            self.load_template(element)
        elif element.tag.lower() == 'templates':
            for _element in element.getchildren():
                if _element.tag is etree.Comment:
                    continue
                elif _element.tag is html.HtmlComment:
                    continue
                elif _element.tag.lower() == 'template':
                    self.load_template(_element)
                else:
                    raise TemplateException(
                        "Only 'template' can be loaded not %r in file %r" % (
                            _element.tag, openedfile))

        else:
            raise TemplateException(
                "Only 'template' or 'templates' can be loaded not %r in %r"
                % (element.tag, openedfile))

    def load_template(self, element):
        """ Load one specific template

        :param element: html.Element
        :exception: TemplateException
        """
        name = element.attrib.get('id')
        extend = element.attrib.get('extend')
        rewrite = bool(eval(element.attrib.get('rewrite', "False")))

        if name:
            if self.known.get(name) and not rewrite:
                raise TemplateException("Alredy existing template %r" % name)

            self.known[name] = {'tmpl': []}

        if extend:
            if name:
                self.known[name]['extend'] = extend
            else:
                if extend not in self.known:
                    raise TemplateException(
                        "Extend an unexisting template %r" %
                        html.tostring(element))
                name = extend

        if not name:
            raise TemplateException(
                "No template id or extend attrinute found %r" % (
                    html.tostring(element)))

        els = [element] + element.findall('*')
        for el in els:
            if el.text:
                el.text = el.text.strip()

        self.known[name]['tmpl'].append(element)

    def load_template_from_str(self, template):
        el = html.fromstring(template)
        self.load_template(el)

    def get_xpath(self, element):
        """ Find and return the xpath found in the template

        :param element: html.Element
        :rtype: list of dict
        """
        res = []
        for el in element.findall('xpath'):
            res.append(dict(
                expression=el.attrib.get('expression', '/'),
                mult=bool(eval(el.attrib.get('mult', 'False'))),
                action=el.attrib.get('action', 'insert'),
                elements=el.getchildren()))

        return res

    def xpath(self, name, expression, mult):
        """ Apply the xpath """
        tmpl = self.compiled[name]
        if mult:
            return tmpl.findall(expression)
        else:
            return [tmpl.find(expression)]

    def xpath_insert(self, name, expression, mult, elements):
        """ Apply a xpath insert::

            <template id="..." extend="other template">
                <xpath expresion="..." action="insert">
                    ...
                </xpath>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        :elements: children of the xpath to insert
        """
        els = self.xpath(name, expression, mult)
        for el in els:
            nbchildren = len(el.getchildren())
            for i, subel in enumerate(elements):
                el.insert(i + nbchildren, subel)

    def xpath_insertBefore(self, name, expression, mult, elements):
        """ Apply a xpath insert::

            <template id="..." extend="other template">
                <xpath expresion="..." action="insertBefore">
                    ...
                </xpath>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        :elements: children of the xpath to insert
        """
        els = self.xpath(name, expression, mult)
        parent_els = self.xpath(name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    for j, subel in enumerate(elements):
                        parent.insert(i + j, subel)

    def xpath_insertAfter(self, name, expression, mult, elements):
        """ Apply a xpath insert::

            <template id="..." extend="other template">
                <xpath expresion="..." action="insertAfter">
                    ...
                </xpath>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        :elements: children of the xpath to insert
        """
        els = self.xpath(name, expression, mult)
        parent_els = self.xpath(name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    for j, subel in enumerate(elements):
                        parent.insert(i + j + 1, subel)

    def xpath_remove(self, name, expression, mult):
        """ Apply a xpath remove::

            <template id="..." extend="other template">
                <xpath expresion="..." action="remove"/>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        """
        els = self.xpath(name, expression, mult)
        parent_els = self.xpath(name, expression + '/..', mult)
        for parent in parent_els:
            for cel in parent.getchildren():
                if cel in els:
                    parent.remove(cel)

    def xpath_replace(self, name, expression, mult, elements):
        """ Apply a xpath replace::

            <template id="..." extend="other template">
                <xpath expresion="..." action="replace">
                    ...
                </xpath>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        :elements: children of the xpath to replace
        """
        els = self.xpath(name, expression, mult)
        parent_els = self.xpath(name, expression + '/..', mult)
        for parent in parent_els:
            for i, cel in enumerate(parent.getchildren()):
                if cel in els:
                    parent.remove(cel)
                    for j, subel in enumerate(elements):
                        parent.insert(i + j, subel)

    def xpath_attributes(self, name, expression, mult, attributes):
        """ Apply a xpath attributes::

            <template id="..." extend="other template">
                <xpath expresion="..." action="attributes">
                    <attribute key="value"/>
                    <attribute foo="bar"/>
                </xpath>
            </template>

        :param name: name of the template
        :param expresion: xpath regex to find the good node
        :param mult: If true, xpath can apply on all the element found
        :attributes: attributes to apply
        """
        els = self.xpath(name, expression, mult)
        for el in els:
            for k, v in attributes.items():
                el.set(k, v)

    def get_xpath_attributes(self, elements):
        """ Find and return the attibute """
        res = []
        for el in elements:
            if el.tag != 'attribute':
                logger.warning(
                    "get %r node, waiting 'attribute' node" % el.tag)
                continue

            res.append(dict(el.items()))

        return res

    def get_elements(self, name):
        elements = [deepcopy(x) for x in self.known[name]['tmpl']]
        for el in elements:
            for el_call in el.findall('.//call'):
                parent = el_call.getparent()
                index = parent.index(el_call)
                tmpl = self.compile_template(el_call.attrib['template'])
                for child in tmpl.getchildren():
                    parent.insert(index, deepcopy(child))
                    index += 1

                parent.remove(el_call)

        return elements

    def apply_xpath(self, val, name):
        action = val['action']
        expression = val['expression']
        mult = val['mult']
        els = val['elements']
        if action == 'insert':
            self.xpath_insert(name, expression, mult, els)
        elif action == 'insertBefore':
            self.xpath_insertBefore(name, expression, mult, els)
        elif action == 'insertAfter':
            self.xpath_insertAfter(name, expression, mult, els)
        elif action == 'replace':
            self.xpath_replace(name, expression, mult, els)
        elif action == 'remove':
            self.xpath_remove(name, expression, mult)
        elif action == 'attributes':
            for attributes in self.get_xpath_attributes(els):
                self.xpath_attributes(
                    name, expression, mult, attributes)
        else:
            raise TemplateException("Unknown action %r" % action)

    def compile_template(self, name):
        """ compile a specific template

        :param name: id str of the template
        """
        if name in self.compiled:
            return self.compiled[name]

        extend = self.known[name].get('extend')
        elements = self.get_elements(name)

        if extend:
            tmpl = deepcopy(self.compile_template(extend))
            tmpl.set('id', name)
        else:
            tmpl = elements[0]
            elements = elements[1:]

        self.compiled[name] = tmpl

        for el in elements:
            for val in self.get_xpath(el):
                self.apply_xpath(val, name)

        return self.compiled[name]

    def compile(self):
        """ compile all the templates """
        for tmpl in self.known.keys():
            self.compile_template(tmpl)

    def copy(self):
        """ copy all the templates """
        self_copy = Template(forclient=self.forclient)
        for tmpl_name in self.known.keys():
            self_copy.known[tmpl_name] = {
                'tmpl': [x for x in self.known[tmpl_name]['tmpl']],
            }
            if self.known[tmpl_name]['extend']:
                self_copy.known[tmpl_name]['extend'] = self.known[tmpl_name][
                    'extend']

        return self_copy
