"""Implementation of the Explanation Agent."""

from __future__ import annotations

from textwrap import dedent

from typing import Optional

from .base import LoggingAgent
from ..state import SessionState
from ..tools import LLMServiceError, OpenAIChatService, SimpleVectorStore


class ExplanationAgent(LoggingAgent):
    """Produce a textual explanation for the learner."""

    def __init__(
        self,
        vector_store: SimpleVectorStore,
        max_sections: int = 3,
        llm_service: Optional[OpenAIChatService] = None,
    ) -> None:
        super().__init__(name="explanation")
        self.vector_store = vector_store
        self.max_sections = max_sections
        self.llm_service = llm_service

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Drafting learner-facing explanation")
        topic = state.topic or "the topic"
        documents = self.vector_store.similarity_search(topic, k=self.max_sections)

        if not documents:
            state.explanation = dedent(
                f"""
                ## Understanding {topic}

                Source material is still being collected. Re-run the pipeline once research
                sources are available to generate a full explanation.
                """
            ).strip()
            return state

        if self.llm_service is not None:
            try:
                state.explanation = self.llm_service.generate_explanation(
                    topic=topic,
                    documents=documents,
                    profile=state.profile,
                )
                self._append_log(state, "Generated learner explanation with OpenAI")
                return state
            except LLMServiceError as exc:
                self._append_log(state, f"LLM explanation generation failed: {exc}")

        sections = []
        for document in documents:
            title = document.metadata.get("title", "Key Insight")
            sections.append(f"### {title}\n{document.content.strip()}")

        body = "\n\n".join(sections)

        state.explanation = dedent(
            f"""
            ## Understanding {topic}

            {body}
            """
        ).strip()
        return state
