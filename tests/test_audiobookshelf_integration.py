from pathlib import Path
from unittest.mock import MagicMock

from integrations.audiobookshelf import AudiobookshelfClient, AudiobookshelfConfig


def test_build_base_url_with_full_host():
    cfg = AudiobookshelfConfig(host='https://abs.example.com')
    client = AudiobookshelfClient(cfg)
    assert client.base_url == 'https://abs.example.com'


def test_authenticate_accepts_token_at_root_key():
    cfg = AudiobookshelfConfig(host='localhost', username='u', password='p')
    client = AudiobookshelfClient(cfg)

    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'token': 'abc', 'user': {'username': 'u'}}
    client.session.post = MagicMock(return_value=response)

    assert client.authenticate() is True
    assert client.token == 'abc'
    assert client.session.headers['Authorization'] == 'Bearer abc'


def test_get_libraries_supports_list_payload():
    cfg = AudiobookshelfConfig(host='localhost')
    client = AudiobookshelfClient(cfg)

    response = MagicMock()
    response.status_code = 200
    response.json.return_value = [{'id': 'lib1'}]
    client.session.get = MagicMock(return_value=response)

    assert client.get_libraries() == [{'id': 'lib1'}]
