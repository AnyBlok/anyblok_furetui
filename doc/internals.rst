.. This file is a part of the AnyBlok project
..
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

Import data of the UI
=====================

In AnyBlok / Furet UI, we made the choices to separate "what we display" and "How we display".

The "how" is the template the what is the data saved in DB. We did some Model to define menu and resource to display

The best way to define the data in a **Blok** is to use the **XML importer**


::

   from anyblok.blok import Blok
   from anyblok_io.blok import BlokImporter

   class MyBlok(Blok, BlokImporter):

      def update(self, latest):
         self.import_file_xml(Model, path, of, the, xml, file)


.. note::

   the path is relative of the blok root

Space menu
----------

It is the main menu of the header, Each space represent a set of resource

The model to use in import_file_xml is **Model.FuretUI.Space**

::

   <records>
      <record external_id="my-space">
         <field name="code">MySpace</field>
         <field name="Label">My Space</field>
         <field name="description">This is a short description of what I will found in my space</field>
      </record>
   </records>
