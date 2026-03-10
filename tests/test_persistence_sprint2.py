from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime, timedelta

HAS_SQLALCHEMY = importlib.util.find_spec("sqlalchemy") is not None

if HAS_SQLALCHEMY:
    from persistence.db import build_engine, build_session_factory, session_scope
    from persistence.models import Base, ProcessingJob
    from persistence.service import ProcessingStateService, RecoveryService


@unittest.skipUnless(HAS_SQLALCHEMY, "sqlalchemy is required for persistence tests")
class TestSprint2Recovery(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = build_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = build_session_factory(self.engine)

    def test_bootstrap_recovery_marks_orphans_retry_pending(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-r1", folder_id="folder-r")
            service.transition_job(job_id="job-r1", folder_id="folder-r", status="running")

        stale_now = datetime.utcnow() + timedelta(minutes=10)
        with session_scope(self.session_factory) as session:
            recovery = RecoveryService(session)
            summary = recovery.bootstrap_recovery(
                heartbeat_timeout_seconds=60,
                max_retries=3,
                now=stale_now,
            )
            self.assertEqual(summary["orphan_detected"], 1)
            self.assertEqual(summary["auto_retried"], 1)

        with session_scope(self.session_factory) as session:
            job = session.get(ProcessingJob, "job-r1")
            self.assertEqual(job.status, "retry_pending")
            self.assertEqual(job.recovery_status, "auto_retried")
            self.assertEqual(job.retry_count, 1)


    def test_bootstrap_recovery_is_idempotent_across_restarts(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-r3", folder_id="folder-restart")
            service.transition_job(job_id="job-r3", folder_id="folder-restart", status="running")

        stale_now = datetime.utcnow() + timedelta(minutes=10)
        with session_scope(self.session_factory) as session:
            recovery = RecoveryService(session)
            first = recovery.bootstrap_recovery(heartbeat_timeout_seconds=60, max_retries=3, now=stale_now)
            second = recovery.bootstrap_recovery(heartbeat_timeout_seconds=60, max_retries=3, now=stale_now)

        self.assertEqual(first["orphan_detected"], 1)
        self.assertEqual(second["orphan_detected"], 0)

    def test_create_job_enforces_idempotency_on_active_status(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-r4a", folder_id="folder-lock", idempotency_key="folder-lock")
            with self.assertRaises(ValueError):
                service.create_job(job_id="job-r4b", folder_id="folder-lock", idempotency_key="folder-lock")

        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.transition_job(job_id="job-r4a", folder_id="folder-lock", status="done")
            service.create_job(job_id="job-r4c", folder_id="folder-lock", idempotency_key="folder-lock")

    def test_bootstrap_recovery_marks_manual_after_max_retries(self) -> None:
        with session_scope(self.session_factory) as session:
            service = ProcessingStateService(session)
            service.create_job(job_id="job-r2", folder_id="folder-z")
            service.transition_job(job_id="job-r2", folder_id="folder-z", status="running")
            service.increment_retry_count(job_id="job-r2")

        stale_now = datetime.utcnow() + timedelta(minutes=10)
        with session_scope(self.session_factory) as session:
            recovery = RecoveryService(session)
            summary = recovery.bootstrap_recovery(
                heartbeat_timeout_seconds=60,
                max_retries=1,
                now=stale_now,
            )
            self.assertEqual(summary["manual_intervention"], 1)

        with session_scope(self.session_factory) as session:
            job = session.get(ProcessingJob, "job-r2")
            self.assertEqual(job.status, "failed")
            self.assertEqual(job.recovery_status, "manual_intervention")


if __name__ == "__main__":
    unittest.main()
