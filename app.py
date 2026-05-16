#!/usr/bin/env python
"""
RAG Server Entry Point

Run: python app.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import app, HOST, PORT

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)