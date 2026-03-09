from __future__ import annotations

import importlib.util
import unittest

HAS_SQLALCHEMY = importlib.util.find_spec("sqlalchemy") is not None

if HAS_SQLALCHEMY:
    from persistence.db import build_engine, build_session_factory, session_scope
    from persistence.models import Base, OutboxEvent, ProcessingError, ProcessingJob
    from persistence.service import ProcessingStateService


@unittest.skipUnless(HAS_SQLALCHEMY, "sqlalchemy is required for persistence tests")
class TestSprint1Persistence(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = build_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = build_session_factory(self.engine)

    def test_create_and_transition_job(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-1", folder_id="folder-a")
            service.transition_job(job_id="job-1", folder_id="folder-a", status="running")
            service.transition_job(job_id="job-1", folder_id="folder-a", status="done")

        with session_scope(self.session_factory) as session:
            job = session.get(ProcessingJob, "job-1")
            self.assertIsNotNone(job)
            self.assertEqual(job.status, "done")
            events = session.query(OutboxEvent).all()
            self.assertEqual(len(events), 3)

    def test_record_error_marks_job_failed(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-2", folder_id="folder-b")
            service.record_error(
                job_id="job-2",
                folder_id="folder-b",
                error_code="ffmpeg_error",
                user_message="Conversion impossible",
                technical_message="exit code 1",
                retryable=True,
            )

        with session_scope(self.session_factory) as session:
            job = session.get(ProcessingJob, "job-2")
            self.assertEqual(job.status, "failed")
            errors = session.query(ProcessingError).all()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].retryable, "true")


if __name__ == "__main__":
    unittest.main()
