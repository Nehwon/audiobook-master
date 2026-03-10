import os
import tempfile
import unittest
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

from persistence.db import build_engine, build_session_factory, session_scope
from persistence.models import Base, OutboxEvent, ProcessingError, ValidationResult
from web import app as web_app


@unittest.skipUnless(web_app.HAS_SQLALCHEMY, "sqlalchemy not available")
class TestWebApiSprint3(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "sprint3.sqlite"
        self.database_url = f"sqlite+pysqlite:///{self.db_path}"

        self.old_db_url = os.environ.get("AUDIOBOOK_DATABASE_URL")
        os.environ["AUDIOBOOK_DATABASE_URL"] = self.database_url

        web_app._persistence_bootstrap_done = False
        web_app._persistence_session_factory = None

        engine = build_engine(self.database_url)
        Base.metadata.create_all(engine)
        self.session_factory = build_session_factory(engine)

        with session_scope(self.session_factory) as session:
            session.add(
                ProcessingError(
                    job_id="job-1",
                    folder_id="Folder A",
                    error_code="conversion_failed",
                    user_message="Erreur utilisateur",
                    technical_message="stack detail",
                    retryable=False,
                )
            )
            session.add(
                ValidationResult(
                    folder_id="Folder A",
                    validation_key="archive.validate",
                    status="ok",
                    payload={"valid": True},
                )
            )
            session.add(
                OutboxEvent(
                    aggregate_type="job",
                    aggregate_id="job-1",
                    event_type="job.updated",
                    payload={"job_id": "job-1", "status": "running"},
                )
            )

        self.client = web_app.app.test_client()

    def tearDown(self):
        if self.old_db_url is None:
            os.environ.pop("AUDIOBOOK_DATABASE_URL", None)
        else:
            os.environ["AUDIOBOOK_DATABASE_URL"] = self.old_db_url
        web_app._persistence_bootstrap_done = False
        web_app._persistence_session_factory = None
        self.tmp.cleanup()

    def test_folder_errors_contract(self):
        response = self.client.get("/api/folders/errors?folder_id=Folder%20A&limit=10")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertTrue(payload["ok"])
        self.assertIn("data", payload)
        self.assertIn("meta", payload)
        self.assertEqual(payload["meta"]["total"], 1)
        self.assertEqual(payload["data"][0]["folder_id"], "Folder A")

    def test_folder_validations_contract(self):
        response = self.client.get("/api/folders/validations?folder_id=Folder%20A&validation_key=archive.validate")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["meta"]["total"], 1)
        self.assertEqual(payload["data"][0]["status"], "ok")
        self.assertEqual(payload["data"][0]["payload"], {"valid": True})

    def test_events_stream_from_outbox(self):
        response = self.client.get("/api/events/stream?since_id=0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/event-stream")
        body = response.get_data(as_text=True)

        self.assertIn("event: job.updated", body)
        self.assertIn('"aggregate_type": "job"', body)
        self.assertIn("event: heartbeat", body)


if __name__ == "__main__":
    unittest.main()
