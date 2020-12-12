import pytest


@pytest.mark.usefixtures('rollback_registry')
class TestUser:

    def test_is_active(self, rollback_registry):
        user = rollback_registry.Pyramid.User.insert(login='test')
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        assert user.active is True

    def test_is_unactive(self, rollback_registry):
        user = rollback_registry.Pyramid.User.insert(login='test')
        assert user.active is False

    def test_query(self, rollback_registry):
        User = rollback_registry.Pyramid.User
        User.insert(login='test')
        assert User.query().filter(User.active.is_(True)).count() == 0
        rollback_registry.Pyramid.CredentialStore.insert(
            login='test', password='test')
        assert User.query().filter(User.active.is_(True)).count() == 1
