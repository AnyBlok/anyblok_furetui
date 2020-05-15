# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations
from anyblok.config import Configuration
from ipaddress import ip_address, ip_network
from logging import getLogger


logger = getLogger(__name__)


@Declarations.register(Declarations.Model)
class FuretUI:

    @classmethod
    def define_authorized_ips(cls):
        cls.IPS = []
        for network in Configuration.get(
            'furetui_authorized_networks', ''
        ).split(','):
            network = network.strip()
            logger.info('Add network %r in authorized IPs', network)
            if network:
                if network[-3:] == '/32':
                    cls.IPS.append(ip_address(network[:-3]))
                else:
                    cls.IPS.extend(list(ip_network(network).hosts()))

    @classmethod
    def check_security(cls, request):
        res = super(FuretUI, cls).check_security(request)
        if not res:
            return False

        if request.client_addr:  # cause of unittest
            addr = ip_address(request.client_addr)
            logger.debug('Check ip: %r', addr)
            if cls.IPS and addr not in cls.IPS:
                logger.info('%r is not an allowed ip', addr)
                return False

        return True
