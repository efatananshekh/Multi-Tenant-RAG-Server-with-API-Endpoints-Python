"""
Configuration Module
==================

Central configuration for RAG server.
Copy to .env or adjust values here.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent

# ==================
# Server Settings
# ==================

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5555"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Flask
SECRET_KEY = os.getenv("SECRET_KEY", "") or os.urandom(24).hex()
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# ==================
# Paths
# ==================

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "rag_db"))
TENANTS_FILE = str(BASE_DIR / "tenants.json")
ANALYTICS_FILE = str(BASE_DIR / "analytics.json")

# ==================
# RAG Settings
# ==================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))

# Embedding models
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
FALLBACK_EMBEDDING = os.getenv("FALLBACK_EMBEDDING", "BAAI/bge-m3")

# ==================
# Search Settings
# ==================

EXACT_MATCH_SCORE = float(os.getenv("EXACT_MATCH_SCORE", "0.95"))
MIN_CHAR_OVERLAP = int(os.getenv("MIN_CHAR_OVERLAP", "2"))
MIN_MATCH_RATIO = float(os.getenv("MIN_MATCH_RATIO", "0.2"))

# ==================
# Initialize directories
# ==================

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)