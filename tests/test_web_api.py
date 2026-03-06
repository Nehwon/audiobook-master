import tempfile
import unittest
from pathlib import Path
from unittest import mock

from web import app as web_app


class TestWebRenameApi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.media_dir = Path(self.tmp.name)
        self.old_media_dir = web_app.MEDIA_DIR
        self.old_temp_dir = web_app.TEMP_DIR
        self.old_config_path = web_app.CONFIG_PATH
        web_app.MEDIA_DIR = self.media_dir
        web_app.TEMP_DIR = self.media_dir / "tmp"
        web_app.CONFIG_PATH = web_app.TEMP_DIR / "web_config.json"
        self.client = web_app.app.test_client()

    def tearDown(self):
        web_app.MEDIA_DIR = self.old_media_dir
        web_app.TEMP_DIR = self.old_temp_dir
        web_app.CONFIG_PATH = self.old_config_path
        self.tmp.cleanup()

    def test_rename_skips_invalid_folder_type(self):
        resp = self.client.post('/api/rename', json={'folders': [None, '', 12]})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['renamed'], [])
        self.assertEqual(len(payload['skipped']), 3)

    def test_rename_rejects_non_list_payload(self):
        resp = self.client.post('/api/rename', json={'folders': 'abc'})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertIn('folders', payload['error'])

    def test_rename_handles_destination_conflict(self):
        src = self.media_dir / 'Author_Book'
        src.mkdir()
        conflict = self.media_dir / 'Author Book'
        conflict.mkdir()

        resp = self.client.post('/api/rename', json={'folders': ['Author_Book']})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['renamed'], [])
        self.assertEqual(payload['skipped'][0]['reason'], 'destination existante')

    def test_ignore_folder_hides_it_from_library(self):
        (self.media_dir / 'A_Garder').mkdir()
        (self.media_dir / 'A_Garder' / 'a.mp3').write_text('x')
        (self.media_dir / 'A_Ignorer').mkdir()
        (self.media_dir / 'A_Ignorer' / 'a.mp3').write_text('x')

        resp = self.client.post('/api/ignore', json={'folder': 'A_Ignorer'})
        self.assertEqual(resp.status_code, 200)

        listing = self.client.get('/api/library').get_json()
        names = [entry['name'] for entry in listing['folders']]
        self.assertIn('A_Garder', names)
        self.assertNotIn('A_Ignorer', names)

    def test_library_flags_suspicious_folder(self):
        folder = self.media_dir / 'Star Wars - La Tentation de la Force.part3'
        folder.mkdir()
        (folder / 'broken.part3').write_text('x')

        listing = self.client.get('/api/library').get_json()
        self.assertEqual(len(listing['folders']), 1)
        info = listing['folders'][0]
        self.assertTrue(info['issues'])
        self.assertTrue(info['suggest_delete'])
        self.assertTrue(info['can_ignore'])

    def test_library_hides_ignore_for_normal_folder(self):
        folder = self.media_dir / 'Dossier Normal'
        folder.mkdir()
        (folder / 'track1.mp3').write_bytes(b'a' * (60 * 1024 * 1024))
        (folder / 'track2.mp3').write_bytes(b'b' * (60 * 1024 * 1024))

        listing = self.client.get('/api/library').get_json()
        info = next(f for f in listing['folders'] if f['name'] == 'Dossier Normal')
        self.assertFalse(info['suggest_delete'])
        self.assertFalse(info['can_ignore'])

    def test_delete_suspect_folder(self):
        folder = self.media_dir / 'Suspect.part2'
        folder.mkdir()
        (folder / 'broken.part2').write_text('x')

        resp = self.client.post('/api/folder/delete', json={'folder': 'Suspect.part2'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(folder.exists())

    def test_delete_rejects_non_suspect_folder(self):
        folder = self.media_dir / 'Sain'
        folder.mkdir()
        (folder / 'track1.mp3').write_bytes(b'a' * (60 * 1024 * 1024))
        (folder / 'track2.mp3').write_bytes(b'b' * (60 * 1024 * 1024))

        resp = self.client.post('/api/folder/delete', json={'folder': 'Sain'})
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(folder.exists())

    @mock.patch('web.app._run_ollama_metadata_search')
    def test_ollama_search_allowed_even_when_disabled(self, mocked_search):
        web_app._save_config({**web_app._default_config(), 'ollama_enabled': False})
        mocked_search.return_value = {'folder': 'Book', 'title': 'Titre'}

        resp = self.client.post('/api/ollama/search', json={'folders': ['Book']})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['results'], [{'folder': 'Book', 'title': 'Titre'}])

    @mock.patch('web.app._ollama_pull_model')
    def test_ollama_pull_returns_503_on_backend_error(self, mocked_pull):
        mocked_pull.side_effect = RuntimeError('Ollama indisponible')

        resp = self.client.post('/api/ollama/pull', json={'model': 'qwen2.5:7b'})
        self.assertEqual(resp.status_code, 503)
        payload = resp.get_json()
        self.assertIn('Ollama indisponible', payload['error'])


if __name__ == '__main__':
    unittest.main()
