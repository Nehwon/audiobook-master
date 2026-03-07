from pathlib import Path
from unittest.mock import MagicMock

from integrations.audiobookshelf import AudiobookshelfClient, AudiobookshelfConfig


def test_build_base_url_with_full_host():
    cfg = AudiobookshelfConfig(host='https://abs.example.com')
    client = AudiobookshelfClient(cfg)
    assert client.base_url == 'https://abs.example.com'


def test_authenticate_accepts_token_at_root_key():
    cfg = AudiobookshelfConfig(host='localhost')
    client = AudiobookshelfClient(cfg)
    client.config.username = 'u'
    client.config.password = 'p'

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


def test_auth_upload_and_scan_flow(tmp_path):
    cfg = AudiobookshelfConfig(host='localhost')
    client = AudiobookshelfClient(cfg)
    client.config.username = 'u'
    client.config.password = 'p'

    login_response = MagicMock()
    login_response.status_code = 200
    login_response.json.return_value = {'token': 'tok-flow'}

    upload_response = MagicMock()
    upload_response.status_code = 201

    scan_response = MagicMock()
    scan_response.status_code = 200

    client.session.post = MagicMock(side_effect=[login_response, upload_response, scan_response])

    audiobook = tmp_path / 'book.m4b'
    audiobook.write_bytes(b'm4b')

    assert client.authenticate() is True
    assert client.upload_audiobook(audiobook, 'lib1', {'title': 'Titre', 'author': 'Auteur'}) is True
    assert client.scan_library('lib1') is True

    assert client.session.post.call_args_list[0].args[0].endswith('/api/login')
    assert client.session.post.call_args_list[1].args[0].endswith('/api/libraries/lib1/upload')
    assert client.session.post.call_args_list[2].args[0].endswith('/api/libraries/lib1/scan')
