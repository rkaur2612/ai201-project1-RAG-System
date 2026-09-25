"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# city_guides documents are Markdown, one "# Title" line followed by several
# "## Heading" sections (Getting there, Eat and drink, ...). These numbers are
# picked to fit that structure, not config.py's generic ones, so the starter's
# fallback_split (and its CHUNK_SIZE / CHUNK_OVERLAP) stay a fair baseline to
# compare against in unit 2.
#
# Measured across all 84 sections in city_guides: the average is 310
# characters and the median 293. Only 7 sections exceed 500, and every one of
# those 7 already breaks into 2-3 blank-line-separated paragraphs (see the
# README's Chunking Strategy section for the numbers). So 500 is the point
# past which a section gets split further, on those paragraph breaks — not an
# arbitrary round number.
MAX_CHUNK_CHARS = 500

_TITLE_RE = re.compile(r"^#\s+(.+)")
_HEADING_RE = re.compile(r"(?m)^##\s+(.+?)\s*$")


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _split_sections(text: str) -> list[tuple[str, str]]:
    """
    Break one document's body into (heading, body) pairs on its "## " lines.

    Anything before the first "## " heading — the intro paragraph every town
    guide opens with ("Brightwater is a river town of...") — is kept too,
    labelled "Overview", instead of being silently dropped. The five
    cross-cutting guides (eating, seasons, walking, transport, accessibility)
    have no such intro; they jump straight into their first heading.
    """
    matches = list(_HEADING_RE.finditer(text))

    sections: list[tuple[str, str]] = []

    leading_end = matches[0].start() if matches else len(text)
    leading = text[:leading_end].strip()
    if leading:
        sections.append(("Overview", leading))

    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            sections.append((heading, body))

    return sections


def _split_oversized(heading: str, body: str) -> list[str]:
    """
    A section over MAX_CHUNK_CHARS splits on its paragraph breaks.

    Every oversized section in city_guides already breaks cleanly into 2-3
    paragraphs this way (each one a complete thought — often one town's entry
    in a section like "Straightforward" or "Difficult" in
    guide_accessibility.md). If a section has no paragraph break to split on,
    it's left whole rather than cut mid-sentence at a fixed character count —
    that's the exact problem this chunker replaces.
    """
    if len(heading) + 1 + len(body) <= MAX_CHUNK_CHARS:
        return [body]

    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        return [body]

    return paragraphs


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks, one per "## " section of the source Markdown.

    city_guides is 14 documents, each a "# Title" line followed by several
    "## Heading" sections (Getting there, Eat and drink, ...) — see
    corpora/README.md. A fixed 800-character window cuts straight through
    those headings, so the boundary here is the heading itself, not a
    character count.

    A section on its own doesn't say which town it's about — "Getting there"
    could be any of the nine towns — so every chunk gets its document's title
    prepended. A section longer than MAX_CHUNK_CHARS is split further on its
    own paragraph breaks (see _split_oversized).
    """
    chunks: list[Chunk] = []

    for doc in documents:
        first_line, _, rest = doc.text.partition("\n")
        title_match = _TITLE_RE.match(first_line.strip())
        if title_match:
            title = title_match.group(1).strip()
            body_text = rest
        else:
            # No "# Title" line — fall back to the filename rather than drop
            # the document.
            title = doc.source.rsplit(".", 1)[0].replace("_", " ")
            body_text = doc.text

        sections = _split_sections(body_text)
        if not sections:
            continue

        index = 0
        for heading, body in sections:
            for piece in _split_oversized(heading, body):
                chunks.append(
                    Chunk(
                        text=f"{title}\n\n{heading}\n{piece}",
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
