"""
Chunking Module
=============

Smart text chunking for RAG:
- Split by sections
- Sentence-aware splitting
- Semantic overlap between chunks
"""

import re
from typing import List

from src import config


def chunk_text(
    text: str,
    chunk_size: int = None,
    overlap: int = None
) -> List[str]:
    """
    Smart text chunking with semantic overlap.

    Args:
        text: Input text
        chunk_size: Maximum chunk size (default from config)
        overlap: Overlap between chunks (default from config)

    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if overlap is None:
        chunk_size = config.CHUNK_OVERLAP

    chunks = []

    # Split by section headers
    section_pattern = r'(?:\n\s*═+\s*\n|\n\s*বিষয়:\s*[^\n]+\n|\n\s*\d+\.\s+[^\n]+\n)'
    sections = re.split(section_pattern, text, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        # Split by numbered items or language markers
        sentence_delimiters = r'[।.!।?؟]'
        sub_sections = re.split(
            r'\n(?:\d+\.|[উদাহরণ|বাংলায়|ইংরেজি|Note])',
            section
        )

        for sub_section in sub_sections:
            if not sub_section.strip():
                continue

            sub_section = sub_section.strip()

            # Small text - just add as-is
            if len(sub_section) <= chunk_size:
                chunks.append(sub_section)
            else:
                # Split by sentences
                sentences = re.split(sentence_delimiters, sub_section)
                current = ""
                current_size = 0

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    if current_size + len(sentence) < chunk_size:
                        current += " " + sentence if current else sentence
                        current_size += len(sentence) + 1
                    else:
                        if current:
                            chunks.append(current.strip())
                        # Add overlap words from previous chunk
                        if overlap > 0 and current:
                            words = current.split()
                            overlap_words = words[-3:] if len(words) > 3 else words
                            current = " ".join(overlap_words) + " " + sentence
                            current_size = len(" ".join(overlap_words)) + len(sentence)
                        else:
                            current = sentence
                            current_size = len(sentence)

                if current.strip():
                    chunks.append(current.strip())

    # If text is small, add as single chunk
    if len(text) <= chunk_size * 3:
        chunks.append(text.strip())

    return [c for c in chunks if c and len(c) > 10]


def chunk_file(
    filepath: str,
    chunk_size: int = None,
    overlap: int = None
) -> List[str]:
    """
    Chunk a file based on its extension.

    Args:
        filepath: Path to file
        chunk_size: Maximum chunk size
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if overlap is None:
        overlap = config.CHUNK_OVERLAP

    ext = filepath.lower().split('.')[-1] if '.' in filepath else 'txt'

    # Read file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # Process based on extension
    if ext in ['txt', 'md', 'csv', 'log']:
        return chunk_text(text, chunk_size, overlap)
    elif ext in ['html', 'htm']:
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return chunk_text(text, chunk_size, overlap)
    elif ext == 'json':
        try:
            import json
            data = json.loads(text)
            text = json.dumps(data, ensure_ascii=False)
        except:
            pass
        return chunk_text(text, chunk_size, overlap)
    else:
        return chunk_text(text, chunk_size, overlap)