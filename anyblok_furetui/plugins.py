# This file is a part of the AnyBlok / Pyramid project
#
#    Copyright (C) 2020 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.model.plugins import ModelPluginBase


class ExposedMethod(ModelPluginBase):
    """An AnyBlok plugin that helps to add exposed methods by models
    """

    def __init__(self, registry):
        if not hasattr(registry, "exposed_methods"):
            registry.exposed_methods = {}

        super().__init__(registry)

    def transform_base_attribute(
        self, attr, method, namespace, base, transformation_properties,
        new_type_properties,
    ):
        """Find exposed methods in the base to save the
        namespace and the method in the registry
        :param attr: attribute name
        :param method: method pointer of the attribute
        :param namespace: the namespace of the model
        :param base: One of the base of the model
        :param transformation_properties: the properties of the model
        :param new_type_properties: param to add in a new base if need
        """
        if getattr(method, "is_an_exposed_method", False) is True:
            model = self.registry.exposed_methods.setdefault(namespace, {})
            model.update({method.__name__: method.exposure_description})

    def after_model_construction(self, base, namespace,
                                 transformation_properties):
        """Do some action with the constructed Model

        :param base: the Model class
        :param namespace: the namespace of the model
        :param transformation_properties: the properties of the model
        """
        # Need for the polymorphism get from main model
        for depend in base.__depends__:
            for k, v in self.registry.exposed_methods.get(depend, {}).items():
                model = self.registry.exposed_methods.setdefault(namespace, {})
                model.setdefault(k, v)
