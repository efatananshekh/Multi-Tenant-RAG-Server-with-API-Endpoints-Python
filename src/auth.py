"""
Authentication Module
==================

Handles tenant authentication, password hashing,
and credential storage.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional

from src import config


def load_json(filepath: str, default: Any = None) -> Dict:
    """Load JSON from file."""
    if default is None:
        default = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json(filepath: str, data: Dict) -> None:
    """Save JSON to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def hash_password(password: str) -> str:
    """Hash password with secret key."""
    salt = config.SECRET_KEY
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == password_hash


def get_tenant(tenant_id: str) -> Optional[Dict]:
    """Get tenant by ID."""
    tenants = load_json(config.TENANTS_FILE, {})
    return tenants.get(tenant_id)


def create_tenant(tenant_id: str, password: str, api_key: str) -> Dict:
    """Create or update tenant."""
    tenants = load_json(config.TENANTS_FILE, {})
    from datetime import datetime

    tenants[tenant_id] = {
        'password_hash': hash_password(password),
        'api_key': api_key,
        'created': str(datetime.now())
    }
    save_json(config.TENANTS_FILE, tenants)
    return tenants[tenant_id]


def delete_tenant(tenant_id: str) -> bool:
    """Delete tenant."""
    tenants = load_json(config.TENANTS_FILE, {})
    if tenant_id in tenants:
        del tenants[tenant_id]
        save_json(config.TENANTS_FILE, tenants)
        return True
    return False