from __future__ import annotations

from keplermind.app.mcp.controller import MemoryController
from keplermind.app.mcp.stores import EpisodicLog, PreferenceStore, SemanticStore


def test_memory_commit_persists_candidates(tmp_path) -> None:
    controller = MemoryController(
        episodic_log=EpisodicLog(db_path=tmp_path / "events.sqlite"),
        semantic_store=SemanticStore(),
        preference_store=PreferenceStore(json_path=tmp_path / "prefs.json"),
    )

    controller.propose(
        [
            {
                "type": "preference",
                "content": "Preferred explanation style: bullet",
                "metadata": {"key": "style"},
                "scores": {"usefulness": 0.8, "generality": 0.6, "recency": 0.7, "stability": 0.5},
            },
            {
                "type": "anchor_fact",
                "content": "Key insight about topic",
                "metadata": {"skill": "Foundations"},
                "scores": {"usefulness": 0.7, "generality": 0.4, "recency": 0.6, "stability": 0.5},
            },
        ]
    )

    reviewed = controller.review(limit=2)
    assert len(reviewed) == 2

    committed = controller.commit("session-001")
    assert committed == ["pref:style", "doc_1"]

    preferences = controller.preference_store.as_dict()
    assert preferences["style"] == "Preferred explanation style: bullet"

    documents = controller.semantic_store.all()
    assert len(documents) == 1
    assert documents[0].metadata["skill"] == "Foundations"

    events = controller.episodic_log.fetch_all()
    assert len(events) == 2
