"""Implementation of the Questioning Agent."""

from __future__ import annotations

from itertools import islice
import re

from .base import LoggingAgent
from ..state import SessionState
from ..tools import SimpleVectorStore


class QuestioningAgent(LoggingAgent):
    """Generate formative assessment questions."""

    def __init__(self, vector_store: SimpleVectorStore, max_questions: int = 5) -> None:
        super().__init__(name="questioning")
        self.vector_store = vector_store
        self.max_questions = max_questions

    @staticmethod
    def _extract_focus(text: str) -> str:
        sentences = re.split(r"[.!?]", text)
        for sentence in sentences:
            cleaned = sentence.strip()
            if cleaned:
                return cleaned
        return text.strip()

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Generating diagnostic questions")
        topic = state.topic or "the subject"
        documents = self.vector_store.similarity_search(topic, k=self.max_questions)
        generated: list[str] = []

        for document in documents:
            title = document.metadata.get("title") or "this concept"
            focus = self._extract_focus(document.content)
            generated.append(
                f"How does {title.lower()} illustrate {topic.lower()} in practice?"
            )
            generated.append(
                f"What evidence from the research shows that '{focus}' is important for {topic.lower()}?"
            )

        generated = list(dict.fromkeys(generated))  # preserve order while deduplicating
        state.questions = list(islice(generated, self.max_questions))

        if len(state.questions) < self.max_questions:
            fallback = [
                f"What is the core definition of {topic}?",
                f"Which misconceptions often arise when learning {topic}?",
                f"Describe a challenge that {topic} helps resolve.",
                f"How would you teach {topic} to a peer?",
            ]
            for question in fallback:
                if len(state.questions) >= self.max_questions:
                    break
                if question not in state.questions:
                    state.questions.append(question)

        self._append_log(state, f"Prepared {len(state.questions)} questions")
        return state
