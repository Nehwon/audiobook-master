import json
import sqlite3
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
        self.assertEqual(payload['code'], 'invalid_folders')

    def test_rename_rejects_non_dict_overrides(self):
        resp = self.client.post('/api/rename', json={'folders': ['a'], 'overrides': []})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertIn('overrides', payload['error'])
        self.assertEqual(payload['code'], 'invalid_overrides')

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

    def test_ignore_rejects_path_traversal(self):
        resp = self.client.post('/api/ignore', json={'folder': '../secret'})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload['code'], 'invalid_folder_name')

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
        hidden = next(entry for entry in listing['hidden_processed_folders'] if entry['name'] == 'Mon Livre Source')
        self.assertIn(output_name, hidden['output_files'])

    def test_delete_processed_folder_with_override_flag(self):
        folder = self.media_dir / 'Traite'
        folder.mkdir()
        (folder / 'track1.mp3').write_text('x')
        output_name = 'Auteur - Traite.m4b'
        (web_app.OUTPUT_DIR / output_name).write_text('m4b')
        web_app._save_m4b_candidate('Traite', output_name)

        resp = self.client.post('/api/folder/delete', json={'folder': 'Traite', 'allow_hidden_processed': True})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(folder.exists())

    def test_delete_output_file_endpoint(self):
        output_name = 'Auteur - Roman.m4b'
        out = web_app.OUTPUT_DIR / output_name
        out.write_text('m4b')

        resp = self.client.post('/api/output/delete', json={'filename': output_name})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(out.exists())

    def test_delete_both_processed_folder_and_output(self):
        folder = self.media_dir / 'Traite Deux'
        folder.mkdir()
        (folder / 'track1.mp3').write_text('x')
        output_name = 'Auteur - Traite Deux.m4b'
        out = web_app.OUTPUT_DIR / output_name
        out.write_text('m4b')
        web_app._save_m4b_candidate('Traite Deux', output_name)

        resp_folder = self.client.post('/api/folder/delete', json={'folder': 'Traite Deux', 'allow_hidden_processed': True})
        self.assertEqual(resp_folder.status_code, 200)
        resp_out = self.client.post('/api/output/delete', json={'filename': output_name})
        self.assertEqual(resp_out.status_code, 200)

        self.assertFalse(out.exists())
        self.assertFalse(folder.exists())

    def test_save_config_encrypts_audiobookshelf_secrets_at_rest(self):
        cfg = web_app._default_config()
        cfg['audiobookshelf_password'] = 'MotDePasseUltraSecret'
        cfg['audiobookshelf_api_key'] = 'api_key_123456'

        web_app._save_config(cfg)

        with sqlite3.connect(web_app._state_db_path()) as conn:
            row = conn.execute(
                "SELECT config_payload FROM app_config WHERE config_key = ?",
                ('web',),
            ).fetchone()
        self.assertIsNotNone(row)
        raw = row[0]
        self.assertNotIn('MotDePasseUltraSecret', raw)
        self.assertNotIn('api_key_123456', raw)

        loaded = web_app._load_config()
        self.assertEqual(loaded['audiobookshelf_password'], 'MotDePasseUltraSecret')
        self.assertEqual(loaded['audiobookshelf_api_key'], 'api_key_123456')

    def test_save_config_persists_to_sqlite(self):
        cfg = web_app._default_config()
        cfg['audiobookshelf_server_url'] = 'https://abs.example'
        web_app._save_config(cfg)

        db_path = web_app._state_db_path()
        self.assertTrue(db_path.exists())

        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT config_payload FROM app_config WHERE config_key = ?",
                ('web',),
            ).fetchone()
        self.assertIsNotNone(row)
        stored = json.loads(row[0])
        self.assertEqual(stored['audiobookshelf_server_url'], 'https://abs.example')

        loaded = web_app._load_config()
        self.assertEqual(loaded['audiobookshelf_server_url'], 'https://abs.example')


    def test_load_config_migrates_legacy_json_file_to_sqlite(self):
        legacy = web_app._default_config()
        legacy['audiobookshelf_server_url'] = 'https://legacy.example'
        web_app.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        web_app.CONFIG_PATH.write_text(json.dumps(legacy), encoding='utf-8')

        loaded = web_app._load_config()
        self.assertEqual(loaded['audiobookshelf_server_url'], 'https://legacy.example')

        with sqlite3.connect(web_app._state_db_path()) as conn:
            row = conn.execute(
                "SELECT config_payload FROM app_config WHERE config_key = ?",
                ('web',),
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertIn('legacy.example', row[0])

    def test_api_config_preserves_audiobookshelf_and_plugin_settings(self):
        payload = {
            'audiobookshelf_server_url': 'https://abs.example',
            'audiobookshelf_username': 'admin',
            'audiobookshelf_password': 'secret',
            'audiobookshelf_api_key': 'key123',
            'audiobookshelf_library_id': 'lib-main',
            'scraping_sources': ['google_books', 'babelio'],
            'cover_sources': ['existing_file'],
            'export_plugins': ['audiobookshelf'],
        }

        resp = self.client.post('/api/config', json=payload)
        self.assertEqual(resp.status_code, 200)

        loaded = self.client.get('/api/config').get_json()
        self.assertEqual(loaded['audiobookshelf_library_id'], 'lib-main')
        self.assertEqual(loaded['audiobookshelf_server_url'], 'https://abs.example')
        self.assertEqual(loaded['scraping_sources'], ['google_books', 'babelio'])
        self.assertEqual(loaded['cover_sources'], ['existing_file'])
        self.assertEqual(loaded['export_plugins'], ['audiobookshelf'])

    def test_api_config_export_and_import(self):
        payload = {
            'audiobookshelf_server_url': 'https://abs-export.example',
            'audiobookshelf_username': 'export-user',
            'audiobookshelf_password': 'export-secret',
            'scraping_sources': ['google_books'],
        }
        saved = self.client.post('/api/config', json=payload)
        self.assertEqual(saved.status_code, 200)

        exported_resp = self.client.get('/api/config/export')
        self.assertEqual(exported_resp.status_code, 200)
        exported = exported_resp.get_json()
        self.assertTrue(exported['ok'])
        self.assertEqual(exported['config']['audiobookshelf_server_url'], 'https://abs-export.example')
        self.assertIn('version', exported['config'])

        self.client.post('/api/config', json={'audiobookshelf_server_url': 'https://changed.example'})
        imported_resp = self.client.post('/api/config/import', json=exported)
        self.assertEqual(imported_resp.status_code, 200)
        imported_payload = imported_resp.get_json()
        self.assertTrue(imported_payload['ok'])
        self.assertEqual(imported_payload['config']['audiobookshelf_server_url'], 'https://abs-export.example')

    @mock.patch('urllib.request.urlopen')
    def test_audiobookshelf_test_connection_with_api_key(self, mocked_urlopen):
        response = mock.MagicMock()
        response.status = 200
        response.read.return_value = b'{"user": {"username": "fabrice"}}'
        mocked_urlopen.return_value.__enter__.return_value = response

        resp = self.client.post(
            '/api/audiobookshelf/test-connection',
            json={
                'audiobookshelf_server_url': 'https://abs.example.com',
                'audiobookshelf_api_key': 'secret-api-key',
            },
        )

        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['auth_method'], 'api_key')
        self.assertEqual(payload['username'], 'fabrice')

    @mock.patch('urllib.request.urlopen')
    def test_audiobookshelf_test_connection_with_login_password(self, mocked_urlopen):
        response = mock.MagicMock()
        response.status = 200
        response.read.return_value = b'{"token": "abc-token"}'
        mocked_urlopen.return_value.__enter__.return_value = response

        resp = self.client.post(
            '/api/audiobookshelf/test-connection',
            json={
                'audiobookshelf_server_url': 'https://abs.example.com',
                'audiobookshelf_username': 'admin',
                'audiobookshelf_password': 'password',
            },
        )

        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['auth_method'], 'password')
        self.assertEqual(payload['username'], 'admin')

    def test_audiobookshelf_test_connection_rejects_missing_credentials(self):
        resp = self.client.post(
            '/api/audiobookshelf/test-connection',
            json={
                'audiobookshelf_server_url': 'https://abs.example.com',
            },
        )

        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload['code'], 'missing_credentials')

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


    def test_enqueue_rejects_duplicate_active_folder(self):
        folder = self.media_dir / 'Livre Unique'
        folder.mkdir()
        (folder / 'a.mp3').write_text('x')

        first = self.client.post('/api/jobs/enqueue', json={'folders': ['Livre Unique']})
        self.assertEqual(first.status_code, 200)
        payload1 = first.get_json()
        self.assertEqual(len(payload1['queued']), 1)

        second = self.client.post('/api/jobs/enqueue', json={'folders': ['Livre Unique']})
        self.assertEqual(second.status_code, 200)
        payload2 = second.get_json()
        self.assertEqual(len(payload2['queued']), 0)
        self.assertEqual(len(payload2['skipped']), 1)
        self.assertEqual(payload2['skipped'][0]['reason'], 'déjà en attente/en cours')

    @mock.patch('web.app._persist_job_created')
    def test_enqueue_persists_created_jobs(self, mocked_persist):
        folder = self.media_dir / 'Livre Persisté'
        folder.mkdir()
        (folder / 'a.mp3').write_text('x')

        resp = self.client.post('/api/jobs/enqueue', json={'folders': ['Livre Persisté']})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mocked_persist.call_count, 1)

    @mock.patch('web.app._persist_job_created')
    def test_reprocess_persists_created_job(self, mocked_persist):
        folder = self.media_dir / 'Livre Reprocess'
        folder.mkdir()
        (folder / 'a.mp3').write_text('x')

        resp = self.client.post('/api/jobs/reprocess', json={'folder': 'Livre Reprocess'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mocked_persist.call_count, 1)

    @mock.patch('web.app._persist_job_transition')
    def test_cancel_job_marks_pending_job_as_cancelled(self, mocked_transition):
        folder = self.media_dir / 'Livre Cancel'
        folder.mkdir()
        (folder / 'a.mp3').write_text('x')

        enqueue = self.client.post('/api/jobs/enqueue', json={'folders': ['Livre Cancel']})
        self.assertEqual(enqueue.status_code, 200)
        job_id = enqueue.get_json()['queued'][0]['id']

        resp = self.client.post('/api/jobs/cancel', json={'job_id': job_id})
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['cancelled']['status'], 'cancelled')
        self.assertEqual(mocked_transition.call_count, 1)

    def test_cancel_job_rejects_unknown_job(self):
        resp = self.client.post('/api/jobs/cancel', json={'job_id': 'job-missing'})
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload['code'], 'job_not_found')

    def test_cancel_job_requires_job_id(self):
        resp = self.client.post('/api/jobs/cancel', json={})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertEqual(payload['code'], 'missing_job_id')

    def test_enqueue_rejects_non_list_payload(self):
        resp = self.client.post('/api/jobs/enqueue', json={'folders': 'not-a-list'})
        self.assertEqual(resp.status_code, 400)
        payload = resp.get_json()
        self.assertIn('folders', payload['error'])

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

    def test_jobs_payload_includes_cancelled_in_done(self):
        with web_app.jobs_lock:
            web_app.jobs.clear()
            web_app.jobs['job-cancel'] = web_app.Job(id='job-cancel', folder='Livre', status='cancelled', progress=100)

        jobs = self.client.get('/api/jobs')
        self.assertEqual(jobs.status_code, 200)
        payload = jobs.get_json()
        done_statuses = [entry['status'] for entry in payload['done']]
        self.assertIn('cancelled', done_statuses)

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



    def test_monitor_endpoint_detects_no_change_with_same_signatures(self):
        first = self.client.get('/api/monitor')
        self.assertEqual(first.status_code, 200)
        first_payload = first.get_json()

        signatures = first_payload['signatures']
        second = self.client.get('/api/monitor', query_string={
            'source_sig': signatures['source_sig'],
            'output_sig': signatures['output_sig'],
            'jobs_sig': signatures['jobs_sig'],
        })
        self.assertEqual(second.status_code, 200)
        payload = second.get_json()
        self.assertFalse(payload['changes']['library'])
        self.assertFalse(payload['changes']['outputs'])
        self.assertFalse(payload['changes']['jobs'])

    def test_monitor_endpoint_detects_source_output_and_job_changes(self):
        baseline = self.client.get('/api/monitor').get_json()

        folder = self.media_dir / 'Live Change'
        folder.mkdir()
        (folder / 'track.mp3').write_text('x')
        (self.output_dir / 'Live Change.m4b').write_text('m4b')

        with web_app.jobs_lock:
            web_app.jobs['job-live'] = web_app.Job(id='job-live', folder='Live Change', status='running', progress=12)

        changed = self.client.get('/api/monitor', query_string={
            'source_sig': baseline['signatures']['source_sig'],
            'output_sig': baseline['signatures']['output_sig'],
            'jobs_sig': baseline['signatures']['jobs_sig'],
        })
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

    def test_download_rejects_path_escape(self):
        resp = self.client.get('/api/download/../../etc/passwd')
        self.assertEqual(resp.status_code, 404)
        payload = resp.get_json()
        self.assertEqual(payload['code'], 'file_not_found')

    @mock.patch('web.app._ensure_worker')
    def test_pipeline_archive_extract_rename_enqueue(self, mocked_worker):
        import zipfile

        archive = self.media_dir / 'Auteur_Livre.zip'
        with zipfile.ZipFile(archive, 'w') as zf:
            zf.writestr('01-track.mp3', b'audio-bytes')

        extract_resp = self.client.post('/api/extract', json={'archives': ['Auteur_Livre.zip']})
        self.assertEqual(extract_resp.status_code, 200)
        extract_payload = extract_resp.get_json()
        self.assertEqual(extract_payload['errors'], [])
        extracted_folder = extract_payload['results'][0]['folder']

        rename_resp = self.client.post(
            '/api/rename',
            json={'folders': [extracted_folder], 'overrides': {extracted_folder: 'Auteur - Livre'}},
        )
        self.assertEqual(rename_resp.status_code, 200)
        rename_payload = rename_resp.get_json()
        self.assertEqual(rename_payload['renamed'][0]['new'], 'Auteur - Livre')

        enqueue_resp = self.client.post('/api/jobs/enqueue', json={'folders': ['Auteur - Livre']})
        self.assertEqual(enqueue_resp.status_code, 200)
        enqueue_payload = enqueue_resp.get_json()
        self.assertEqual(len(enqueue_payload['queued']), 1)
        self.assertEqual(enqueue_payload['queued'][0]['folder'], 'Auteur - Livre')
        mocked_worker.assert_called()


class TestSprint2PacketsApi(unittest.TestCase):
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
        with web_app.packets_lock:
            web_app.upload_packets.clear()
            web_app.packet_schedule_jobs.clear()
        self.client = web_app.app.test_client()

    def tearDown(self):
        web_app.MEDIA_DIR = self.old_media_dir
        web_app.OUTPUT_DIR = self.old_output_dir
        web_app.TEMP_DIR = self.old_temp_dir
        web_app.CONFIG_PATH = self.old_config_path
        with web_app.packets_lock:
            web_app.upload_packets.clear()
            web_app.packet_schedule_jobs.clear()
        self.tmp.cleanup()

    def test_packets_list_and_detail(self):
        (self.output_dir / "Livre-A.m4b").write_bytes(b"a")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-A.m4b']})
        response = self.client.get('/api/integrations/audiobookshelf/packets')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['packets'])
        packet_id = payload['packets'][0]['id']

        detail = self.client.get(f'/api/integrations/audiobookshelf/packets/{packet_id}')
        self.assertEqual(detail.status_code, 200)
        detail_payload = detail.get_json()
        self.assertIn('payload_preview', detail_payload)

    def test_packets_metadata_update_marks_packet_ready(self):
        (self.output_dir / "Livre-B.m4b").write_bytes(b"b")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-B.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']

        response = self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata',
            json={'filename': 'Livre-B.m4b', 'metadata': {'title': 'Titre', 'author': 'Auteur', 'synopsis': 'Résumé'}}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['packet']['validation']['ok'])
        self.assertEqual(payload['packet']['status'], 'pret')

    def test_packets_submit_without_channels_has_no_delivery(self):
        (self.output_dir / "Livre-Canal.m4b").write_bytes(b"x")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-Canal.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']
        self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata',
            json={'filename': 'Livre-Canal.m4b', 'metadata': {'title': 'Titre', 'author': 'Auteur', 'synopsis': 'Résumé'}}
        )

        response = self.client.post(f'/api/integrations/audiobookshelf/packets/{packet_id}/submit', json={'channels': []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['deliveries'], [])

    def test_packets_submit_requires_complete_metadata(self):
        (self.output_dir / "Livre-C.m4b").write_bytes(b"c")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-C.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']

        invalid_submit = self.client.post(f'/api/integrations/audiobookshelf/packets/{packet_id}/submit')
        self.assertEqual(invalid_submit.status_code, 400)
        self.assertEqual(invalid_submit.get_json()['code'], 'metadata_incomplete')

        self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata',
            json={'filename': 'Livre-C.m4b', 'metadata': {'title': 'Titre', 'author': 'Auteur', 'synopsis': 'Résumé'}}
        )
        valid_submit = self.client.post(f'/api/integrations/audiobookshelf/packets/{packet_id}/submit')
        self.assertEqual(valid_submit.status_code, 200)
        self.assertTrue(valid_submit.get_json()['ok'])

    def test_packets_create_from_outputs(self):
        out = self.output_dir / 'Mon-Livre.m4b'
        out.write_bytes(b'12345')

        response = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['Mon-Livre.m4b'], 'name': 'Paquet Output'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['packet']['name'], 'Paquet Output')
        self.assertEqual(payload['packet']['file_count'], 1)

    def test_packets_are_not_auto_bootstrapped(self):
        response = self.client.get('/api/integrations/audiobookshelf/packets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['packets'], [])

    def test_packets_remove_file(self):
        out = self.output_dir / 'A.m4b'
        out.write_bytes(b'aaa')
        packet = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['A.m4b'], 'name': 'Paquet A'}
        ).get_json()['packet']

        response = self.client.delete(
            f"/api/integrations/audiobookshelf/packets/{packet['id']}/files",
            json={'filename': 'A.m4b'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['packet']['file_count'], 0)


    def test_packets_create_prefills_metadata_from_filename(self):
        (self.output_dir / "Auteur X - Saga Y - Vol 2 - Livre Z.m4b").write_bytes(b"x")
        response = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['Auteur X - Saga Y - Vol 2 - Livre Z.m4b']}
        )
        self.assertEqual(response.status_code, 200)
        packet = response.get_json()['packet']
        md = packet['file_metadata']['Auteur X - Saga Y - Vol 2 - Livre Z.m4b']
        self.assertEqual(md['author'], 'Auteur X')
        self.assertEqual(md['series'], 'Saga Y')
        self.assertEqual(md['volume'], '2')
        self.assertEqual(md['title'], 'Livre Z')

    def test_packets_require_volume_when_series_is_set(self):
        (self.output_dir / "Livre-Serie.m4b").write_bytes(b"x")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-Serie.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']

        response = self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata',
            json={'filename': 'Livre-Serie.m4b', 'metadata': {'title': 'Titre', 'author': 'Auteur', 'series': 'Saga', 'synopsis': 'Résumé'}}
        )
        self.assertEqual(response.status_code, 200)
        missing = response.get_json()['packet']['validation']['missing']
        self.assertIn('Livre-Serie.m4b:volume', missing)

    @mock.patch('web.app._summarize_synopsis_no_spoiler', return_value='Résumé court sans spoiler')
    @mock.patch('web.app.BookScraper')
    def test_packets_metadata_scrape_endpoint(self, mocked_scraper_cls, _mock_summary):
        (self.output_dir / "Auteur - Livre.m4b").write_bytes(b"x")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Auteur - Livre.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']

        scraper = mocked_scraper_cls.return_value
        scraper.search_book.return_value = mock.Mock(
            title='Livre Officiel',
            author='Auteur Officiel',
            series='Saga Officielle',
            series_number='4',
            narrator='Narrateur',
            description='Texte long de synopsis source',
        )

        response = self.client.post(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata/scrape',
            json={'filename': 'Auteur - Livre.m4b'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        md = payload['packet']['file_metadata']['Auteur - Livre.m4b']
        self.assertEqual(md['title'], 'Livre Officiel')
        self.assertEqual(md['author'], 'Auteur Officiel')
        self.assertEqual(md['series'], 'Saga Officielle')
        self.assertEqual(md['volume'], '4')
        self.assertEqual(md['synopsis'], 'Résumé court sans spoiler')

    def test_packets_changelog_draft_includes_each_title_and_single_line_synopsis(self):
        (self.output_dir / "Livre-1.m4b").write_bytes(b"1")
        (self.output_dir / "Livre-2.m4b").write_bytes(b"2")
        packet = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['Livre-1.m4b', 'Livre-2.m4b'], 'name': 'Paquet Multi'}
        ).get_json()['packet']

        self.client.put(
            f"/api/integrations/audiobookshelf/packets/{packet['id']}/metadata",
            json={'filename': 'Livre-1.m4b', 'metadata': {'title': 'Titre 1', 'author': 'Auteur 1', 'synopsis': 'Ligne A\nLigne B'}}
        )
        self.client.put(
            f"/api/integrations/audiobookshelf/packets/{packet['id']}/metadata",
            json={'filename': 'Livre-2.m4b', 'metadata': {'title': 'Titre 2', 'author': 'Auteur 2', 'synopsis': 'Bloc X\nBloc Y'}}
        )

        draft = self.client.post(f"/api/integrations/audiobookshelf/packets/{packet['id']}/changelog/draft")
        self.assertEqual(draft.status_code, 200)
        payload = draft.get_json()
        text = payload['draft']
        self.assertIn('Titre 1', text)
        self.assertIn('Titre 2', text)
        self.assertIn('synopsis: Ligne A Ligne B', text)
        self.assertIn('synopsis: Bloc X Bloc Y', text)

    def test_packets_changelog_draft_and_manual_update(self):
        (self.output_dir / "Livre-D.m4b").write_bytes(b"d")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-D.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']

        draft = self.client.post(f'/api/integrations/audiobookshelf/packets/{packet_id}/changelog/draft')
        self.assertEqual(draft.status_code, 200)
        draft_payload = draft.get_json()
        self.assertTrue(draft_payload['draft'])
        self.assertIn('source', draft_payload)

        edited = self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/changelog',
            json={'edited': 'Message édité manuellement'}
        )
        self.assertEqual(edited.status_code, 200)
        edited_payload = edited.get_json()
        self.assertEqual(edited_payload['packet']['changelog']['edited'], 'Message édité manuellement')


class TestSprint3PlanningAndBroadcastApi(unittest.TestCase):
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
        with web_app.packets_lock:
            web_app.upload_packets.clear()
            web_app.packet_schedule_jobs.clear()
        self.client = web_app.app.test_client()

    def tearDown(self):
        web_app.MEDIA_DIR = self.old_media_dir
        web_app.OUTPUT_DIR = self.old_output_dir
        web_app.TEMP_DIR = self.old_temp_dir
        web_app.CONFIG_PATH = self.old_config_path
        with web_app.packets_lock:
            web_app.upload_packets.clear()
            web_app.packet_schedule_jobs.clear()
        self.tmp.cleanup()

    def _prepare_ready_packet(self):
        (self.output_dir / "Livre-Sprint3.m4b").write_bytes(b"x")
        self.client.post('/api/integrations/audiobookshelf/packets', json={'output_files': ['Livre-Sprint3.m4b']})
        packet_id = self.client.get('/api/integrations/audiobookshelf/packets').get_json()['packets'][0]['id']
        self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/metadata',
            json={'filename': 'Livre-Sprint3.m4b', 'metadata': {'title': 'Titre Sprint3', 'author': 'Auteur Sprint3', 'synopsis': 'Résumé sprint3'}}
        )
        self.client.put(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/changelog',
            json={'edited': 'Changelog sprint 3'}
        )
        return packet_id

    def test_schedule_job_and_run_updates_status(self):
        packet_id = self._prepare_ready_packet()
        publish_at = int(web_app.time.time()) + 3600
        scheduled = self.client.post(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/schedule',
            json={'publish_at': publish_at, 'channels': ['discord']}
        )
        self.assertEqual(scheduled.status_code, 200)
        job_id = scheduled.get_json()['job']['id']

        jobs = self.client.get('/api/integrations/audiobookshelf/scheduler/jobs')
        self.assertEqual(jobs.status_code, 200)
        self.assertEqual(len(jobs.get_json()['jobs']), 1)

        run = self.client.post(f'/api/integrations/audiobookshelf/scheduler/jobs/{job_id}/run')
        self.assertEqual(run.status_code, 200)
        run_payload = run.get_json()
        self.assertEqual(run_payload['job']['status'], 'completed')
        self.assertEqual(run_payload['packet']['status'], 'publie')

    def test_schedule_force_publish_bypasses_metadata_validation(self):
        out = self.output_dir / 'Force.m4b'
        out.write_bytes(b'force')
        packet = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['Force.m4b'], 'name': 'Paquet Force'}
        ).get_json()['packet']
        publish_at = int(web_app.time.time()) + 3600
        scheduled = self.client.post(
            f"/api/integrations/audiobookshelf/packets/{packet['id']}/schedule",
            json={'publish_at': publish_at, 'channels': ['discord'], 'force_publish': True}
        )
        self.assertEqual(scheduled.status_code, 200)
        job_id = scheduled.get_json()['job']['id']
        run = self.client.post(f'/api/integrations/audiobookshelf/scheduler/jobs/{job_id}/run')
        self.assertEqual(run.status_code, 200)
        self.assertEqual(run.get_json()['packet']['status'], 'publie')

    def test_broadcast_reports_unconfigured_channels(self):
        packet_id = self._prepare_ready_packet()
        resp = self.client.post(
            f'/api/integrations/audiobookshelf/packets/{packet_id}/broadcast',
            json={'channels': ['discord', 'email']}
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.get_json()
        self.assertEqual(payload['deliveries'][0]['status'], 'skipped')
        self.assertEqual(payload['deliveries'][1]['status'], 'skipped')

    def test_cleanup_removes_packet_files_and_output_file(self):
        out = self.output_dir / 'Nettoyage.m4b'
        out.write_bytes(b'abc123')
        packet = self.client.post(
            '/api/integrations/audiobookshelf/packets',
            json={'output_files': ['Nettoyage.m4b'], 'name': 'Paquet Nettoyage'}
        ).get_json()['packet']

        cleanup = self.client.post(
            f"/api/integrations/audiobookshelf/packets/{packet['id']}/cleanup",
            json={'delete_output_files': True}
        )
        self.assertEqual(cleanup.status_code, 200)
        payload = cleanup.get_json()
        self.assertEqual(payload['packet']['file_count'], 0)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
