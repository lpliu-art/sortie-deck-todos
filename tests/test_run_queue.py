from __future__ import annotations

import time

from sortie_deck.run_queue import SqliteRunQueue


def test_run_queue_lease_exclusive(tmp_path):
    q = SqliteRunQueue(tmp_path / "runs.sqlite", lease_seconds=30)
    j1 = q.enqueue("ini_a", kind="start")
    j2 = q.enqueue("ini_a", kind="start")
    assert j1 != j2
    claimed = q.claim("worker-1")
    assert claimed is not None
    assert claimed.initiative_id == "ini_a"
    # Same initiative locked — second claim should skip until complete
    other = q.claim("worker-2")
    assert other is None or other.initiative_id != "ini_a"
    q.complete(claimed.id)
    next_job = q.claim("worker-2")
    assert next_job is not None
    assert next_job.initiative_id == "ini_a"
    q.complete(next_job.id)


def test_run_queue_expired_lease_reclaim(tmp_path):
    q = SqliteRunQueue(tmp_path / "runs.sqlite", lease_seconds=1)
    q.enqueue("ini_b", kind="start")
    first = q.claim("worker-1")
    assert first is not None
    # Force expire
    q._conn.execute(
        "UPDATE run_jobs SET lease_until=? WHERE id=?",
        (time.time() - 10, first.id),
    )
    q._conn.execute(
        "UPDATE initiative_locks SET lease_until=? WHERE initiative_id=?",
        (time.time() - 10, "ini_b"),
    )
    q._conn.commit()
    second = q.claim("worker-2")
    assert second is not None
    assert second.id == first.id
    q.complete(second.id)
