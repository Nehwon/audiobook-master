import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from web import app as web_app


class TestWebRenameApi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.media_dir = Path(self.tmp.name) / "_media"
        self.output_dir = Path(self.tmp.name) / "_output"
        self.temp_dir = Path(self.tmp.name) / "_tmp"
        self.old_media_dir = web_app.MEDIA_DIR
        self.old_output_dir = web_app.OUTPUT_DIR
        self.old_temp_dir = web_app.TEMP_DIR
        self.old_config_path = web_app.CONFIG_PATH
        web_app.MEDIA_DIR = self.media_dir
        web_app.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        web_app.OUTPUT_DIR = self.output_dir
        web_app.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        web_app.TEMP_DIR = self.temp_dir
        web_app.CONFIG_PATH = web_app.TEMP_DIR / "web_config.json"
        with web_app.jobs_lock:
            web_app.jobs.clear()
            web_app.job_events.clear()
        self.client = web_app.app.test_client()

    def tearDown(self):
        web_app.MEDIA_DIR = self.old_media_dir
        web_app.OUTPUT_DIR = self.old_output_dir
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

    def test_rename_rejects_non_dict_overrides(self):
        resp = self.client.post('/api/rename', json={'folders': ['a'], 'overrides': []})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertIn('overrides', payload['error'])

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

    def test_rename_uses_manual_override_title(self):
        src = self.media_dir / 'Author_Book'
        src.mkdir()

        resp = self.client.post(
            '/api/rename',
            json={'folders': ['Author_Book'], 'overrides': {'Author_Book': 'Mon Titre 2024'}},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['renamed'], [{'old': 'Author_Book', 'new': 'Mon Titre 2024'}])
        self.assertTrue((self.media_dir / 'Mon Titre 2024').exists())

    def test_rename_rejects_invalid_manual_override_title(self):
        src = self.media_dir / 'Author_Book'
        src.mkdir()

        resp = self.client.post(
            '/api/rename',
            json={'folders': ['Author_Book'], 'overrides': {'Author_Book': '   '}},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['renamed'], [])
        self.assertEqual(payload['skipped'][0]['reason'], 'titre manuel vide')

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

    def test_library_hides_source_folder_when_matching_output_exists(self):
        folder = self.media_dir / 'Mon Livre Source'
        folder.mkdir()
        (folder / 'track1.mp3').write_text('x')

        output_name = 'Auteur - Mon Super Livre.m4b'
        (web_app.OUTPUT_DIR / output_name).write_text('m4b')
        web_app._save_m4b_candidate('Mon Livre Source', output_name)

        listing = self.client.get('/api/library').get_json()
        names = [entry['name'] for entry in listing['folders']]
        self.assertNotIn('Mon Livre Source', names)

    def test_save_config_encrypts_audiobookshelf_secrets_at_rest(self):
        cfg = web_app._default_config()
        cfg['audiobookshelf_password'] = 'MotDePasseUltraSecret'
        cfg['audiobookshelf_api_key'] = 'api_key_123456'

        web_app._save_config(cfg)

        raw = web_app.CONFIG_PATH.read_text(encoding='utf-8')
        self.assertNotIn('MotDePasseUltraSecret', raw)
        self.assertNotIn('api_key_123456', raw)

        loaded = web_app._load_config()
        self.assertEqual(loaded['audiobookshelf_password'], 'MotDePasseUltraSecret')
        self.assertEqual(loaded['audiobookshelf_api_key'], 'api_key_123456')

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




    def test_library_includes_active_job_status_for_folder(self):
        folder = self.media_dir / 'Livre En Cours'
        folder.mkdir()
        (folder / 'track.mp3').write_text('x')

        with web_app.jobs_lock:
            web_app.jobs.clear()
            web_app.jobs['job-42'] = web_app.Job(
                id='job-42',
                folder='Livre En Cours',
                status='running',
                progress=47,
                stage='Conversion',
            )

        resp = self.client.get('/api/library')
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        entry = next(item for item in payload['folders'] if item['name'] == 'Livre En Cours')
        self.assertIsNotNone(entry['job'])
        self.assertEqual(entry['job']['status'], 'running')
        self.assertEqual(entry['job']['progress'], 47)

    def test_push_job_event_persists_details_payload(self):
        with web_app.jobs_lock:
            web_app.job_events.clear()

        web_app._push_job_event('job-99', 'Livre', 'Conversion', 'FFmpeg en cours', details={'eta': '00h12mn'})

        with web_app.jobs_lock:
            last_event = web_app.job_events[-1]

        self.assertIn('details', last_event)
        self.assertEqual(last_event['details']['eta'], '00h12mn')

    def test_jobs_payload_contains_events(self):
        folder = self.media_dir / 'Livre'
        folder.mkdir()
        (folder / 'a.mp3').write_text('x')

        enqueue = self.client.post('/api/jobs/enqueue', json={'folders': ['Livre']})
        self.assertEqual(enqueue.status_code, 200)

        jobs = self.client.get('/api/jobs')
        self.assertEqual(jobs.status_code, 200)
        payload = jobs.get_json()
        self.assertIn('events', payload)
        self.assertIsInstance(payload['events'], list)

    def test_push_job_event_does_not_deadlock_when_lock_is_held(self):
        done = threading.Event()

        def _call_event_push():
            with web_app.jobs_lock:
                web_app._push_job_event('job-1', 'Livre', 'Préparation', 'Test event')
            done.set()

        worker = threading.Thread(target=_call_event_push)
        worker.start()
        worker.join(timeout=1)

        self.assertTrue(done.is_set(), 'Deadlock détecté lors de _push_job_event')


    def test_dom_changes_reports_no_change_with_same_signatures(self):
        first = self.client.get('/api/dom/changes')
        self.assertEqual(first.status_code, 200)
        payload = first.get_json()

        signatures = payload['signatures']
        second = self.client.get(
            '/api/dom/changes',
            query_string={
                'source_sig': signatures['source_sig'],
                'output_sig': signatures['output_sig'],
                'jobs_sig': signatures['jobs_sig'],
            },
        )
        self.assertEqual(second.status_code, 200)
        payload2 = second.get_json()
        self.assertFalse(payload2['changes']['library'])
        self.assertFalse(payload2['changes']['outputs'])
        self.assertFalse(payload2['changes']['jobs'])

    def test_dom_changes_detects_source_and_output_and_jobs_updates(self):
        initial = self.client.get('/api/dom/changes').get_json()

        folder = self.media_dir / 'Nouveau Livre'
        folder.mkdir()
        (folder / 'track.mp3').write_text('x')
        (self.output_dir / 'Sortie.m4b').write_text('m4b')

        with web_app.jobs_lock:
            web_app.jobs['job-100'] = web_app.Job(id='job-100', folder='Nouveau Livre', status='running', progress=5)

        changed = self.client.get(
            '/api/dom/changes',
            query_string={
                'source_sig': initial['signatures']['source_sig'],
                'output_sig': initial['signatures']['output_sig'],
                'jobs_sig': initial['signatures']['jobs_sig'],
            },
        )
        self.assertEqual(changed.status_code, 200)
        payload = changed.get_json()
        self.assertTrue(payload['changes']['library'])
        self.assertTrue(payload['changes']['outputs'])
        self.assertTrue(payload['changes']['jobs'])

    def test_logs_endpoint_returns_json(self):
        resp = self.client.get('/api/logs?lines=20')
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertIn('lines', payload)
        self.assertIn('path', payload)

if __name__ == '__main__':
    unittest.main()
