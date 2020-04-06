import pytest
from anyblok.config import Configuration
from anyblok.blok import BlokManager
from os.path import join


@pytest.mark.usefixtures('rollback_registry')
class TestWebClient:

    def test_get_client_file(self, webserver, rollback_registry):
        path = Configuration.get('furetui_client_path', '/furet-ui')
        response = webserver.get(path)
        blok_path = BlokManager.getPath('furetui')
        path = join(blok_path, 'static', 'index.html')
        assert response.status_code == 200
        assert response.content_type == 'text/html'
        with open(path, 'rb') as fp:
            assert fp.read() == response.body
