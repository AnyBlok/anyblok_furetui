import pytest
from ...testing import TmpTemplate


tmpl_test_form_ok = """
    <template id="tmpl_test_form">
        <field name="name" />
    </template>
"""


tmpl_test_form_ko = """
    <template id="tmpl_test_form">
        <button label="test" />
        <field name="name" />
    </template>
"""


tmpl_test_list_ok = """
    <template id="tmpl_test_list">
        <field name="name" />
    </template>
"""


tmpl_test_list_ko = """
    <template id="tmpl_test_list">
        <buttons>
            <button label="test" />
        </buttons>
        <field name="name" />
    </template>
"""


@pytest.mark.usefixtures('rollback_registry')
class TestResourceForm:

    @pytest.fixture(autouse=True)
    def transact(self, request, rollback_registry):
        self.resource_form = rollback_registry.FuretUI.Resource.Form.insert(
            code='test-list-resource', model='Model.System.Model',
            template='tmpl_test_form')
        self.resource_list = rollback_registry.FuretUI.Resource.List.insert(
            code='test-list-resource', title='test-list-resource',
            model='Model.System.Model', template='tmpl_test_list')

    def test_valide_resource_form_ok(self, rollback_registry):
        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str(tmpl_test_form_ok)
            tmpl.compile()
            validate = rollback_registry.FuretUI.validate_form_resources()
            assert len(validate) == 0, ', '.join(validate)

    def test_valide_resource_form_ko(self, rollback_registry):
        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str(tmpl_test_form_ko)
            tmpl.compile()
            validate = rollback_registry.FuretUI.validate_form_resources()
            assert len(validate) == 1, ', '.join(validate)

    def test_valide_resource_list_ok(self, rollback_registry):
        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str(tmpl_test_list_ok)
            tmpl.compile()
            validate = rollback_registry.FuretUI.validate_list_resources()
            assert len(validate) == 0, ', '.join(validate)

    def test_valide_resource_list_ko(self, rollback_registry):
        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str(tmpl_test_list_ko)
            tmpl.compile()
            validate = rollback_registry.FuretUI.validate_list_resources()
            assert len(validate) == 1, ', '.join(validate)

    def test_valide_resources_ko(self, rollback_registry):
        with TmpTemplate(rollback_registry) as tmpl:
            tmpl.load_template_from_str(tmpl_test_form_ko)
            tmpl.load_template_from_str(tmpl_test_list_ko)
            tmpl.compile()
            validate = rollback_registry.FuretUI.validate_resources()
            assert len(validate) == 2, ', '.join(validate)
