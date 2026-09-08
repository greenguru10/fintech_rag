"""Section-aware semantic financial chunker."""

import re
from typing import List, Dict, Any
from app.ingestion.cleaner import clean_document_text
from app.nlp.normalizer import normalize_text


class RawChunk:
    def __init__(
        self,
        raw_text: str,
        section: str | None,
        page_start: int | None,
        page_end: int | None,
        token_count: int,
    ):
        self.raw_text = raw_text
        self.normalized_text = normalize_text(raw_text)
        self.section = section
        self.page_start = page_start
        self.page_end = page_end
        self.token_count = token_count


class FinancialChunker:
    def __init__(
        self,
        min_words: int = 40,
        soft_target_words: int = 140,
        max_words: int = 280,
    ):
        self.min_words = min_words
        self.soft_target_words = soft_target_words
        self.max_words = max_words

        # Heading detection pattern
        self.heading_pattern = re.compile(
            r"^(?:#{1,4}\s+|[0-9]{1,2}[\.\)]\s+|[A-Z\s]{4,}:?|[A-Z][a-zA-Z0-9\s\?]{3,60}:?\??)$",
            re.MULTILINE,
        )

    def is_heading(self, line: str) -> bool:
        line_clean = line.strip()
        if not line_clean or len(line_clean) > 80:
            return False
        if line_clean.startswith(("#", "Q.", "Q:", "Question", "FAQ", "Chapter", "Section")):
            return True
        if line_clean.endswith("?") and len(line_clean) < 80:
            return True
        if line_clean.isupper() and len(line_clean) > 3:
            return True
        return False

    def chunk_document_pages(
        self,
        pages: List[Any],  # ParsedPage objects
    ) -> List[RawChunk]:
        chunks: List[RawChunk] = []
        current_section = "General Overview"
        current_paras: List[str] = []
        current_word_count = 0
        current_page_start = None
        current_page_end = None

        def flush_chunk():
            nonlocal current_paras, current_word_count, current_page_start, current_page_end
            if not current_paras:
                return
            combined_text = "\n\n".join(current_paras).strip()
            if not combined_text:
                return

            words = combined_text.split()
            chunks.append(
                RawChunk(
                    raw_text=combined_text,
                    section=current_section,
                    page_start=current_page_start,
                    page_end=current_page_end,
                    token_count=len(words),
                )
            )
            current_paras = []
            current_word_count = 0

        for page in pages:
            cleaned_page = clean_document_text(page.text)
            paragraphs = cleaned_page.split("\n\n")

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                lines = para.split("\n")
                first_line = lines[0].strip()

                # Check if paragraph starts with a heading
                if self.is_heading(first_line):
                    # If we have accumulated enough text, flush previous chunk
                    if current_word_count >= self.min_words:
                        flush_chunk()
                    current_section = first_line.lstrip("#").strip()
                    if len(lines) > 1:
                        para = "\n".join(lines[1:]).strip()
                    else:
                        continue  # Heading-only paragraph

                para_words = para.split()
                para_word_count = len(para_words)

                if current_page_start is None:
                    current_page_start = page.page_number
                current_page_end = page.page_number

                # Check if adding this paragraph exceeds maximum words
                if current_word_count + para_word_count > self.max_words and current_word_count >= self.min_words:
                    flush_chunk()
                    current_page_start = page.page_number
                    current_page_end = page.page_number

                current_paras.append(para)
                current_word_count += para_word_count

                # If reached target size, flush
                if current_word_count >= self.soft_target_words:
                    flush_chunk()
                    current_page_start = None
                    current_page_end = None

        flush_chunk()
        return chunks
