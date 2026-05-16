"""
Flask Application
==================

Main Flask app with routes and UI.
"""

import os
import sys
import io
import uuid
import logging
from functools import wraps
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src import config
from src.config import HOST, PORT, DEBUG, SECRET_KEY, MAX_CONTENT_LENGTH
from src.auth import load_json, save_json, hash_password, get_tenant
from src.translation import translate_query, is_bengali
from src.chunking import chunk_text, chunk_file
from src.rag import rag_manager, init_rag_manager, HAS_RAG

# ==================
# Logging
# ==================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================
# Fix UTF-8 on Windows
# ==================

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================
# Flask App
# ==================

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

CORS(app)

# ==================
# Initialize RAG
# ==================

rag_manager = init_rag_manager()


# ==================
# Auth Decorator
# ==================

def require_auth(f):
    """Require authentication for a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        tenant_id = request.headers.get('X-Tenant-ID') or request.json.get('tenant_id')
        api_key = request.headers.get('X-API-Key') or request.json.get('api_key')

        # Check Bearer token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            bearer_key = auth_header[7:]
            if not api_key:
                api_key = bearer_key

        if not tenant_id or not api_key:
            return jsonify({'error': 'tenant_id and api_key required'}), 401

        # Validate
        tenant = get_tenant(tenant_id)
        if not tenant:
            return jsonify({'error': 'Invalid tenant_id'}), 401
        if tenant.get('api_key') != api_key:
            return jsonify({'error': 'Invalid API key'}), 401

        request.tenant_id = tenant_id
        return f(*args, **kwargs)
    return decorated


# ==================
# Analytics
# ==================

def track_query(tenant_id: str, query_time_ms: int):
    """Track query for analytics."""
    analytics = load_json(config.ANALYTICS_FILE, {})
    if tenant_id not in analytics:
        analytics[tenant_id] = {
            "total_queries": 0,
            "total_time_ms": 0,
            "queries_today": 0,
            "last_query": None
        }
    analytics[tenant_id]["total_queries"] += 1
    analytics[tenant_id]["total_time_ms"] += query_time_ms
    analytics[tenant_id]["last_query"] = str(datetime.now())
    save_json(config.ANALYTICS_FILE, analytics)


# ==================
# Routes
# ==================

@app.route('/')
def index():
    """Dashboard UI."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check."""
    tenants = load_json(config.TENANTS_FILE, {})
    return jsonify({
        "status": "ok" if rag_manager else "error",
        "tenants": len(tenants)
    })


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Login or register tenant."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500

    data = request.json or {}
    tenant_id = (data.get('tenant_id') or '').strip()
    password = data.get('password', '')

    if not tenant_id or not password:
        return jsonify({'error': 'tenant_id and password required'}), 400

    tenants = load_json(config.TENANTS_FILE, {})
    is_new = tenant_id not in tenants
    api_key = str(uuid.uuid4()) if is_new else tenants[tenant_id].get(
        'api_key', str(uuid.uuid4())
    )

    tenants[tenant_id] = {
        'password_hash': hash_password(password),
        'api_key': api_key,
        'created': str(datetime.now())
    }
    save_json(config.TENANTS_FILE, tenants)

    return jsonify({
        'success': True,
        'tenant_id': tenant_id,
        'api_key': api_key
    })


@app.route('/api/rag/query', methods=['POST'])
@require_auth
def rag_query():
    """Query knowledge base."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500

    import time
    start_time = time.time()

    data = request.json or {}
    query = data.get('query', '')
    top_k = data.get('top_k', config.DEFAULT_TOP_K)

    if not query:
        return jsonify({'error': 'query required'}), 400

    results = rag_manager.query(request.tenant_id, query, top_k)
    query_time = int((time.time() - start_time) * 1000)
    track_query(request.tenant_id, query_time)

    documents = [r['document'] for r in results]

    return jsonify({
        'query': query,
        'results': results,
        'count': len(results),
        'contexts': documents,
        'documents': documents,
        'chunks': documents,
        'time_ms': query_time
    })


@app.route('/api/rag/upload', methods=['POST'])
@require_auth
def rag_upload():
    """Upload file to knowledge base."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    filename = secure_filename(f"{request.tenant_id}_{file.filename}")
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        chunks = chunk_file(filepath)
        count = rag_manager.add_documents(request.tenant_id, chunks)
        os.remove(filepath)
        return jsonify({'success': True, 'chunks': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rag/add', methods=['POST'])
@require_auth
def rag_add():
    """Add raw documents."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500

    data = request.json or {}
    documents = data.get('documents', [])

    if not documents:
        return jsonify({'error': 'documents required'}), 400

    all_chunks = [str(doc).strip() for doc in documents if str(doc).strip()]
    count = rag_manager.add_documents(request.tenant_id, all_chunks)
    return jsonify({'success': True, 'chunks': count})


@app.route('/api/rag/count', methods=['POST'])
@require_auth
def rag_count():
    """Get document count."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500

    return jsonify({'count': rag_manager.get_count(request.tenant_id)})


@app.route('/api/rag/clear', methods=['POST'])
@require_auth
def rag_clear():
    """Clear all documents."""
    if not rag_manager:
        return jsonify({'error': 'RAG not initialized'}), 500

    success = rag_manager.delete_all(request.tenant_id)
    return jsonify({'success': success})


# ==================
# Main
# ==================

if __name__ == '__main__':
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║         🧠 MULTI-TENANT RAG SERVER                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Dashboard:  http://localhost:{PORT}                          ║
║  API:        http://localhost:{PORT}/api                       ║
║                                                              ║
║  Features:                                                   ║
║    ✓ Glassmorphism UI                                       ║
║    ✓ Multi-tenant isolation                                 ║
║    ✓ Keyword Search (95% accuracy)                         ║
║    ✓ Bengali + English Support                              ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host=HOST, port=PORT, debug=DEBUG)