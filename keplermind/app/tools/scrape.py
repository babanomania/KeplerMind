"""HTML scraping helpers used by the research node."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Callable

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover - fallback path
    requests = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency handling
    from readability import Document
except ImportError:  # pragma: no cover - fallback path
    Document = None  # type: ignore[assignment]


FetchFn = Callable[[str], str]


class ScrapeError(RuntimeError):
    """Raised when a document cannot be retrieved or parsed."""


@dataclass(frozen=True)
class ScrapeResult:
    url: str
    title: str
    text: str
    word_count: int


def _default_fetch(url: str) -> str:
    if requests is None:
        raise ScrapeError("requests library is not available in the environment")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


class _PlainTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:  # pragma: no cover - trivial
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return " ".join(self.parts)


def _to_text(markup: str) -> str:
    parser = _PlainTextExtractor()
    parser.feed(markup)
    parser.close()
    return parser.text()


def _extract_text(raw_html: str) -> tuple[str, str]:
    if Document is not None:
        try:
            doc = Document(raw_html)
            title = doc.short_title() or "Untitled"
            summary_html = doc.summary()
            text_content = _to_text(summary_html)
        except Exception:  # pragma: no cover - defensive fallback
            title, text_content = "Untitled", ""
    else:
        title = "Untitled"
        text_content = _to_text(raw_html)

    cleaned = re.sub(r"\s+", " ", text_content or "").strip()
    return title, cleaned


def scrape(
    url: str,
    *,
    fetcher: FetchFn | None = None,
    html_override: str | None = None,
    fallback_text: str | None = None,
) -> ScrapeResult:
    """Fetch a URL and return a readability-optimised text payload."""

    raw_html = html_override
    if raw_html is None:
        fetch = fetcher or _default_fetch
        try:
            raw_html = fetch(url)
        except Exception as exc:  # pragma: no cover - network dependent
            if fallback_text is None:
                raise ScrapeError(f"Failed to retrieve {url}: {exc}") from exc
            raw_html = f"<html><body><p>{fallback_text}</p></body></html>"

    title, text = _extract_text(raw_html)
    if not text and fallback_text:
        text = fallback_text.strip()

    word_count = len(text.split())
    return ScrapeResult(url=url, title=title or "Untitled", text=text, word_count=word_count)


__all__ = ["scrape", "ScrapeResult", "ScrapeError"]

