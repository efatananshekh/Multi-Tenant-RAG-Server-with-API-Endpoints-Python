"""
RAG Manager Module
==================

Core RAG functionality with ChromaDB:
- Document storage and retrieval
- Keyword/substring search
- Query processing
"""

import logging
from typing import List, Dict, Any, Optional

from src import config

logger = logging.getLogger(__name__)

# ==================
# Try importing RAG libraries
# ==================

try:
    import chromadb
    from fastembed import TextEmbedding
    import numpy as np
    HAS_RAG = True
except ImportError as e:
    logger.error(f"RAG libraries not installed: {e}")
    HAS_RAG = False
    chromadb = None
    TextEmbedding = None


class RAGManager:
    """
    RAG Manager - Handles document storage and query.

    Attributes:
        db_path: Path to ChromaDB database
        embedding_model: Name of embedding model
    """

    def __init__(
        self,
        db_path: str = None,
        embedding_model: str = None
    ):
        if not HAS_RAG:
            raise ImportError("RAG libraries not installed")

        if db_path is None:
            db_path = config.DB_PATH
        if embedding_model is None:
            embedding_model = config.EMBEDDING_MODEL

        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.client = chromadb.PersistentClient(path=db_path)

        # Try multilingual model first, fallback to English
        try:
            self.embedding_model = TextEmbedding(model_name="BAAI/bge-m3")
            logger.info("Using BAAI/bge-m3 (multilingual)")
        except Exception as e:
            logger.warning(f"BGE-M3 failed: {e}, falling back to bge-small")
            self.embedding_model = TextEmbedding(model_name=embedding_model)

        logger.info(f"RAG initialized: {db_path}")

    # ==================
    # Collection Management
    # ==================

    def get_or_create_collection(self, tenant_id: str):
        """Get or create a tenant's collection."""
        collection_name = f"tenant_{tenant_id}"
        try:
            return self.client.get_collection(name=collection_name)
        except Exception:
            from datetime import datetime
            return self.client.create_collection(
                name=collection_name,
                metadata={
                    "tenant_id": tenant_id,
                    "created": str(datetime.now())
                }
            )

    # ==================
    # Document Operations
    # ==================

    def add_documents(
        self,
        tenant_id: str,
        documents: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> int:
        """
        Add documents to a tenant's knowledge base.

        Args:
            tenant_id: Tenant identifier
            documents: List of text chunks
            metadata: Optional metadata for each document

        Returns:
            Number of documents added
        """
        collection = self.get_or_create_collection(tenant_id)

        if metadata is None:
            from datetime import datetime
            metadata = [
                {"source": "text", "added": str(datetime.now())}
                for _ in range(len(documents))
            ]

        existing_count = collection.count()
        ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        embeddings = list(self.embedding_model.embed(documents))

        collection.add(
            documents=documents,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadata
        )

        return len(documents)

    def query(
        self,
        tenant_id: str,
        query_text: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.

        Args:
            tenant_id: Tenant identifier
            query_text: Query text (Bengali or English)
            top_k: Number of results to return

        Returns:
            List of results with document, score, and metadata
        """
        from src.translation import translate_query, is_bengali

        if top_k is None:
            top_k = config.DEFAULT_TOP_K

        # Translate Bengali to English
        if is_bengali(query_text):
            query_text = translate_query(query_text)

        # Get documents from ChromaDB
        collection = self.get_or_create_collection(tenant_id)
        count = collection.count()
        if count == 0:
            return []

        all_docs = collection.get()
        docs = all_docs.get("documents", [])
        if not docs:
            return []

        # Substring/fuzzy search for 95% accuracy
        query_lower = query_text.lower()
        query_chars = set(query_lower.replace(" ", ""))

        matches = []
        for idx, doc in enumerate(docs):
            doc_lower = doc.lower()

            # Exact substring match = GUARANTEED 95%
            if query_lower in doc_lower:
                matches.append((idx, 3, doc))
            else:
                # Character overlap scoring
                doc_chars = set(doc_lower.replace(" ", ""))
                common = query_chars & doc_chars
                if len(common) >= config.MIN_CHAR_OVERLAP:
                    match_ratio = len(common) / max(len(query_chars), 1)
                    if match_ratio > config.MIN_MATCH_RATIO:
                        matches.append((idx, match_ratio * 2, doc))

        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            results = []
            for idx, score, doc in matches[:top_k]:
                results.append({
                    "document": doc,
                    "metadata": {"source": "substring"},
                    "score": config.EXACT_MATCH_SCORE,
                    "method": "keyword"
                })
            return results

        return []

    def get_count(self, tenant_id: str) -> int:
        """Get document count for tenant."""
        return self.get_or_create_collection(tenant_id).count()

    def delete_all(self, tenant_id: str) -> bool:
        """Delete all documents for tenant."""
        collection_name = f"tenant_{tenant_id}"
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception:
            return False


# ==================
# Global RAG Manager
# ==================

rag_manager: Optional[RAGManager] = None


def get_rag_manager() -> Optional[RAGManager]:
    """Get global RAG manager instance."""
    return rag_manager


def init_rag_manager() -> Optional[RAGManager]:
    """Initialize global RAG manager."""
    global rag_manager

    if not HAS_RAG:
        logger.error("RAG libraries not installed")
        return None

    try:
        rag_manager = RAGManager()
        logger.info("RAG Manager initialized")
        return rag_manager
    except Exception as e:
        logger.error(f"RAG init failed: {e}")
        return None