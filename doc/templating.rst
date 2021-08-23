.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2021 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. AnyBlok documentation master file, created by
   sphinx-quickstart on Mon Feb 24 10:12:33 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. contents::

Templating
==========

FuretUI is a client, the goal of the serveur is to give the template to display the UI
for the model.

The template waiting by FuretUI is complexe and the anyblok_furetui give the helper 
to write easily these template.

Define template in blok
-----------------------

The first step is to load the template file::

   class ABlok(Blok):

      furetui = {
         'i18n': {
            'en': {dict a translation}
         },
         'templates': [
            'path of the template file relative of the blok',
         ],
      }


The extension has no importance, by convention the extension is tmpl for template, and the 
repository is templates at the root of the blok.

The contenant of the template files is a html::

   <templates>
      <template id="key to identify the template">
         <h1>Title</h1>
         <p>
            This is a template
         </p>
      </template>
   </templates>


The base of the template
------------------------

Node : **template**
~~~~~~~~~~~~~~~~~~~

The attribute of the template are

+-------------------------+-------------------------------------------------------------+
| Attribute's name        | Description                                                 |
+=========================+=============================================================+
| id                      | key to identify the template, the key is unique             |
+-------------------------+-------------------------------------------------------------+
| extend                  | Key to identify an existing template.                       |
|                         |                                                             |
|                         | * Alone this attibute allow to modify an existing template  |
|                         | * With attribute id, A new new template identify by id is a |
|                         |   modified copy of the extended template                    |
+-------------------------+-------------------------------------------------------------+
| rewrite                 | The id of a template is unique and can be reuse directly to |
|                         | create another template or rewrite. This attribute allow to |
|                         | replace an existing template by another one                 |
+-------------------------+-------------------------------------------------------------+

Node : **call**
~~~~~~~~~~~~~~~

The node **call** allow to include a template in another template::

   <templates>
      <template id="template2include">
         <p>
             Template to include
         </p>
      </template>
      <template id="The final template">
         <h1>Title</h1>
         <p>
             Foo
         </p>
         <call template="template2include" />
      </template>
   </templates>


the result will be::

   <template id="The final template">
      <h1>Title</h1>
      <p>
          Foo
      </p>
      <p>
          Template to include
      </p>
   </template>

This template can be shared between more than one another template

Node : **xpath**
~~~~~~~~~~~~~~~~

This Node works with the attribute **extend** of the template node. The goal is to modify 
a curent template with modification given by xpath::

   <template extend="key2modify">
      <xpath expression="xpath expression" action="action to do">
         <p>some new node</p>
      </xpath>
   </template>


+----------------------------+---------------------------------------------------------+
| Attribute                  | Description                                             |
+============================+=========================================================+
| expression                 | xpath expression defined by                             |
|                            | `lxml <https://lxml.de/xpathxslt.html#xpath>_`          |
+----------------------------+---------------------------------------------------------+
| action                     | The action to do, see next table                        |
+----------------------------+---------------------------------------------------------+
| mult                       | Boolean (default : False), If True All the node will be |
|                            | modified, else only the first                           |
+----------------------------+---------------------------------------------------------+


+----------------------------+---------------------------------------------------------+
| action                     | Description                                             |
+============================+=========================================================+
| insert                     | Insert the element in the selected node                 |
+----------------------------+---------------------------------------------------------+
| insertBefore               | Insert the element before the selected node             |
+----------------------------+---------------------------------------------------------+
| insertAfter                | Insert the element after the selected node              |
+----------------------------+---------------------------------------------------------+
| replace                    | Insert the element at the location of the seleted node  |
+----------------------------+---------------------------------------------------------+
| remove                     | Remove the seleted node                                 |
+----------------------------+---------------------------------------------------------+
| attributes                 | Replace some attributes of the selected node            |
+----------------------------+---------------------------------------------------------+


Example of xpath attributes::

   <template extend="...">
       <xpath expresion="..." action="attributes">
           <attribute key="value"/>
           <attribute foo="bar"/>
       </xpath>
   </template>

Node : **field**
~~~~~~~~~~~~~~~~

This node is particulare, because it is used by the resource representation, the attribute depend
of the resource type


Template : **List**
-------------------

Example of list resource::

   <template id="...">
      <field name="name" sortable/>
      <field name="date" />
      <field name="state" />
   </template>


**field** attributes
~~~~~~~~~~~~~~~~~~~~

This attributes are used by all the field widgets

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| name                       | Required, name of the field to display                  |
+----------------------------+---------------------------------------------------------+
| sortable                   | The field is sortable, in the case of the relationship  |
|                            | the value can be a string "field name.sub field name"   |
+----------------------------+---------------------------------------------------------+
| label                      | Label to display in column header                       |
+----------------------------+---------------------------------------------------------+
| widget                     | Type of field to display, by default is the type of the |
|                            | field                                                   |
+----------------------------+---------------------------------------------------------+
| tooltip                    | Tooltip for the column                                  |
+----------------------------+---------------------------------------------------------+
| width                      | the column size                                         |
+----------------------------+---------------------------------------------------------+
| hidden                     | Can be evaluate, if True the the column will not be     |
|                            | displaied                                               |
+----------------------------+---------------------------------------------------------+
| column-can-be-hidden       | The column can be hidden, an option is shown at the     |
|                            | top of the list                                         |
+----------------------------+---------------------------------------------------------+
| hidden-column              | works with **column-can-be-hidden**, this attribute     |
|                            | give a default value to hide or display column          |
+----------------------------+---------------------------------------------------------+

slot
~~~~

The display of the field can modified::

   <field name="...">
      <strong>The value is : </strong>{{ value }}
   </field>


We also use another field in the slot::

   <field name="title" hidden />
   <field name="name">
      {{ fields.title }} => {{ value }}
   </field>


.. note::

   {{ fields.name }} is different of {{ value }}, because value is a converted version of the field


Widget : **BarCode**
~~~~~~~~~~~~~~~~~~~~

Works with **vue-barcode** all the options can be used with a prefix **barecode-**

Widget : **Many2One**, **One2One**, **One2Many**, **Many2Many**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is the option for all widget's type relationship 

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| display                    | Defined the field of the relationship to display        |
+----------------------------+---------------------------------------------------------+
| no-link                    | If True, FuretUI will be no link to display a resource  |
+----------------------------+---------------------------------------------------------+
| menu                       | AnyBlok.IO.Mapping key of the menu to select            |
+----------------------------+---------------------------------------------------------+
| resource                   | AnyBlok.IO.Mapping key of the resource to select        |
+----------------------------+---------------------------------------------------------+


.. note::

   the slot get the capability to display relationship fields with key word **relation**::

      <field name="address">
         <p>{{ relation.firstname }} {{ relation.lastname }}</p>
         <p>{{ relation.street }}</p>
         <p>{{ relation.zip }} {{ relation.city }}</p>
      </field>


Widget : **Selection**
~~~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| colors                     | json dict value to defined color for the values         |
+----------------------------+---------------------------------------------------------+


Widget : **StatusBar**
~~~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| done-states                | json list of the state will display as final            |
+----------------------------+---------------------------------------------------------+
| dangerous-states           | json list of the states, they are hidden, but if it is  |
|                            | the current value, the value will be displaied with     |
|                            | danger css class                                        |
+----------------------------+---------------------------------------------------------+

Case of the buttons
~~~~~~~~~~~~~~~~~~~

::

   <buttons>
      <button ..../>
   </buttons>

Added buttons on the top of the list

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| call                       | exposed method name on the model of the resource        |
+----------------------------+---------------------------------------------------------+
| open-resource              | AnyBlok.IO.Mapping key of the resource to select        |
+----------------------------+---------------------------------------------------------+


Template : **Form**, **Thumbnail**
----------------------------------

Example of the form resource::

   <template id="...">
      <h1>Title</h1>
      <p><field name="name" /></p>
      <p><field name="date" /></p>
      <p><field name="state" /></p>
   </template>


**field** attributes
~~~~~~~~~~~~~~~~~~~~

This attributes are used by all the field widgets

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| name                       | Required, name of the field to display                  |
+----------------------------+---------------------------------------------------------+
| label                      | Label to display in column header                       |
+----------------------------+---------------------------------------------------------+
| widget                     | Type of field to display, by default is the type of the |
|                            | field                                                   |
+----------------------------+---------------------------------------------------------+
| tooltip                    | Tooltip for the column                                  |
+----------------------------+---------------------------------------------------------+
| hidden                     | Can be evaluate, if True the the column will not be     |
|                            | displaied                                               |
+----------------------------+---------------------------------------------------------+
| writable                   | Can be evaluate, if True the the column will be         |
|                            | writable                                                |
+----------------------------+---------------------------------------------------------+
| readonly                   | Can be evaluate, if True the the column will be         |
|                            | readonly                                                |
+----------------------------+---------------------------------------------------------+
| required                   | Can be evaluate, if True the the column have to         |
|                            | be filled                                               |
+----------------------------+---------------------------------------------------------+

slot
~~~~

The display of the field can modified::

   <field name="...">
      <strong>The value is : </strong>{{ value }}
   </field>


We also use another field in the slot::

   <field name="title" hidden />
   <field name="name">
      {{ fields.title }} => {{ value }}
   </field>

**header** and **footer**
~~~~~~~~~~~~~~~~~~~~~~~~~

the template can be separated to defined a header and a footer template::

   <template id="...">
      <header>
         <h1>{{ fields.name }}</h1>
      </header>
      <footer>
         <p><field name="name"/><p>
      </footer>
      <p>
         foo bar
      </p>
      <p>
         <field name="..." />
      </p>
   </template>


Widget : **String**
~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| placeholder                | The placeholder of the input                            |
+----------------------------+---------------------------------------------------------+
| icon                       | The icon to display in the field                        |
+----------------------------+---------------------------------------------------------+


Widget : **Sequence**
~~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| placeholder                | The placeholder of the input                            |
+----------------------------+---------------------------------------------------------+
| icon                       | The icon to display in the field                        |
+----------------------------+---------------------------------------------------------+

.. warning::

   The field is always readonly


Widget : **Password**
~~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| placeholder                | The placeholder of the input                            |
+----------------------------+---------------------------------------------------------+
| icon                       | The icon to display in the field                        |
+----------------------------+---------------------------------------------------------+
| reveal                     | boolean, if True (default) the password can be reveal   |
+----------------------------+---------------------------------------------------------+


Widget : **BarCode**
~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| placeholder                | The placeholder of the input                            |
+----------------------------+---------------------------------------------------------+
| icon                       | The icon to display in the field                        |
+----------------------------+---------------------------------------------------------+

Works with **vue-barcode** all the options can be used with a prefix **barecode-**


Widget : **Integer**
~~~~~~~~~~~~~~~~~~~~

+----------------------------+---------------------------------------------------------+
| attribute                  | Description                                             |
+============================+=========================================================+
| min                        | min avalaible value                                     |
+----------------------------+---------------------------------------------------------+
| max                        | max avalaible value                                     |
+----------------------------+---------------------------------------------------------+
