"""Citation constructor ensuring transparent attribution."""

from typing import List, Dict, Any


class CitationBuilder:
    def build_citations(self, selected_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        citations: List[Dict[str, Any]] = []
        seen_chunks = set()

        for idx, ev in enumerate(selected_evidence, start=1):
            chunk_id = ev["chunk_id"]
            if chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk_id)

            citations.append({
                "citation_id": len(citations) + 1,
                "document_id": ev.get("document_id"),
                "chunk_id": chunk_id,
                "title": ev.get("title", "Financial Regulatory Guideline"),
                "source_name": ev.get("source_name", "Official Authority"),
                "authority_level": ev.get("authority_level", "A"),
                "section": ev.get("section") or "General Section",
                "page_number": ev.get("page_number"),
                "url": ev.get("source_url"),
                "last_updated": ev.get("last_updated"),
                "excerpt": ev["sentence_text"],
            })

        return citations
