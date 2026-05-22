"""
parsers.py — Day 1
Extracts clean text from syllabus PDFs and lecture transcripts (.pdf or .txt).
"""

import re
import pymupdf  # PyMuPDF


# ── PDF parser ────────────────────────────────────────────────────────────────

def parse_pdf(path: str) -> list[str]:
    """
    Open a PDF and return a list of strings, one per page.
    Empty or whitespace-only pages are skipped.

    Args:
        path: Filepath to a .pdf file.

    Returns:
        List of page text strings.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file has no extractable text (e.g. scanned image PDF).
    """
    doc = pymupdf.open(path)
    pages = []

    for page in doc:
        text = page.get_text("text")          # plain text, preserves line breaks
        cleaned = _clean_text(text)
        if cleaned:
            pages.append(cleaned)

    doc.close()

    if not pages:
        raise ValueError(
            f"No text could be extracted from '{path}'. "
            "The PDF may be a scanned image — try running it through an OCR tool first."
        )

    return pages


def parse_pdf_as_string(path: str) -> str:
    """Convenience wrapper — returns all pages joined as one string."""
    return "\n\n".join(parse_pdf(path))


# ── Transcript parser ─────────────────────────────────────────────────────────

def parse_transcript(path: str) -> str:
    """
    Parse a lecture transcript from a .txt or .pdf file.
    Strips timestamps (common in auto-generated YouTube captions) and
    speaker labels like 'Professor:' or '[Speaker 1]'.

    Args:
        path: Filepath to a .txt or .pdf file.

    Returns:
        Cleaned transcript as a single string.

    Raises:
        ValueError: For unsupported file types or empty content.
    """
    path_lower = path.lower()

    if path_lower.endswith(".txt"):
        raw = _read_txt(path)
    elif path_lower.endswith(".pdf"):
        raw = parse_pdf_as_string(path)
    else:
        raise ValueError(f"Unsupported file type for '{path}'. Use .txt or .pdf.")

    cleaned = _strip_transcript_noise(raw)

    if not cleaned.strip():
        raise ValueError(f"Transcript at '{path}' appears to be empty after cleaning.")

    return cleaned


# ── Internal helpers ──────────────────────────────────────────────────────────

def _read_txt(path: str) -> str:
    """Read a plain text file, trying UTF-8 then latin-1 as fallback."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            return f.read()


def _clean_text(text: str) -> str:
    """
    General-purpose text cleaner for PDF output:
    - Collapses runs of whitespace/newlines
    - Removes page numbers (lone digits on a line)
    - Strips leading/trailing whitespace
    """
    # Remove lone page numbers (a line that's only digits)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _strip_transcript_noise(text: str) -> str:
    """
    Remove common transcript artifacts:
    - Timestamps like [00:01:23] or 0:01:23 or 00:01:23,456
    - Speaker labels like 'Professor Smith:' or '[Speaker 1]'
    - WebVTT/SRT header lines
    - Filler lines like 'WEBVTT', 'NOTE', sequence numbers
    """
    # WebVTT / SRT metadata
    text = re.sub(r"^WEBVTT.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^NOTE\s.*$", "", text, flags=re.MULTILINE)

    # SRT sequence numbers (lone integers on their own line)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)

    # Timestamps: 00:00:00,000 --> 00:00:00,000  or  [00:01:23]  or  (0:01)
    text = re.sub(r"\d{1,2}:\d{2}(:\d{2})?(,\d+)?\s*-->\s*\d{1,2}:\d{2}(:\d{2})?(,\d+)?", "", text)
    text = re.sub(r"[\[\(]\d{1,2}:\d{2}(:\d{2})?[\]\)]", "", text)

    # Speaker labels: "Professor:", "[Speaker 1]", "TA Smith:"
    text = re.sub(r"^\[.*?\]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[A-Z][a-zA-Z\s\.]+:\s*", "", text, flags=re.MULTILINE)

    return _clean_text(text)


# ── Quick smoke test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python parsers.py <syllabus.pdf> <transcript.pdf|.txt>")
        sys.exit(1)

    syllabus_path, transcript_path = sys.argv[1], sys.argv[2]

    print("=== SYLLABUS (first 500 chars) ===")
    syllabus_text = parse_pdf_as_string(syllabus_path)
    print(syllabus_text[:500])
    print(f"\n→ Total characters: {len(syllabus_text)}")

    print("\n=== TRANSCRIPT (first 500 chars) ===")
    transcript_text = parse_transcript(transcript_path)
    print(transcript_text[:500])
    print(f"\n→ Total characters: {len(transcript_text)}")
