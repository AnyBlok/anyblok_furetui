import pytest
from anyblok.testing import tmp_configuration


class MockRequest:

    def __init__(self, addr):
        self.client_addr = addr


@pytest.mark.usefixtures('rollback_registry')
class TestIp:

    def test_define_authorized_ips_with_mask(self, rollback_registry):
        with tmp_configuration(furetui_authorized_networks='192.168.1.1/32'):
            rollback_registry.FuretUI.define_authorized_ips()

    def test_define_authorized_ips_without_mask(self, rollback_registry):
        with tmp_configuration(furetui_authorized_networks='192.168.1.1'):
            rollback_registry.FuretUI.define_authorized_ips()

    def test_check_security_ok(self, rollback_registry):
        request = MockRequest('192.168.1.1')
        with tmp_configuration(furetui_authorized_networks='192.168.1.1/32'):
            rollback_registry.FuretUI.define_authorized_ips()
            acl = rollback_registry.FuretUI.check_security(request)
            assert acl is True

    def test_check_security_ko(self, rollback_registry):
        request = MockRequest('192.68.1.1')
        with tmp_configuration(furetui_authorized_networks='192.168.1.1/32'):
            rollback_registry.FuretUI.define_authorized_ips()
            acl = rollback_registry.FuretUI.check_security(request)
            assert acl is False
