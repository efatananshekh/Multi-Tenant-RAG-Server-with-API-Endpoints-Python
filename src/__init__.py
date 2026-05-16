"""
RAG Server Package
=================

Main entry point and package exports.
"""

from src.app import app
from src.rag import RAGManager, rag_manager, init_rag_manager
from src.config import HOST, PORT, DEBUG
from src.translation import translate_query, is_bengali
from src.chunking import chunk_text, chunk_file

__all__ = [
    'app',
    'RAGManager',
    'rag_manager',
    'init_rag_manager',
    'HOST',
    'PORT',
    'DEBUG',
    'translate_query',
    'is_bengali',
    'chunk_text',
    'chunk_file',
]

__version__ = '1.0.0'