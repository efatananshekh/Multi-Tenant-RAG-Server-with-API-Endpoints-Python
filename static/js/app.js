/**
 * RAG Server - Dashboard JavaScript
 */

(function() {
    'use strict';

    // Global state
    let currentTenant = null;
    let currentApiKey = null;
    let baseURL = '';


    // ==================
    // Auth Functions
    // ==================

    /**
     * Login to the RAG server
     */
    async function login() {
        const tenantId = document.getElementById('tenantId');
        const password = document.getElementById('password');

        if (!tenantId.value.trim() || !password.value) {
            alert('Please fill in all fields');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tenant_id: tenantId.value.trim(),
                    password: password.value
                })
            });

            const data = await response.json();

            if (data.api_key) {
                currentTenant = data.tenant_id;
                currentApiKey = data.api_key;
                showDashboard();
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed: ' + error.message);
        }
    }


    /**
     * Logout and reload
     */
    function logout() {
        currentTenant = null;
        currentApiKey = null;
        location.reload();
    }


    /**
     * Get auth headers
     */
    function getAuthHeaders() {
        return {
            'tenant_id': currentTenant,
            'api_key': currentApiKey
        };
    }


    // ==================
    // Dashboard Functions
    // ==================

    /**
     * Show dashboard after login
     */
    function showDashboard() {
        const authScreen = document.getElementById('authScreen');
        const dashboard = document.getElementById('dashboard');
        const displayTenantId = document.getElementById('displayTenantId');
        const displayApiKey = document.getElementById('displayApiKey');

        if (authScreen && dashboard) {
            authScreen.classList.add('hidden');
            dashboard.classList.remove('hidden');
        }

        if (displayTenantId) {
            displayTenantId.textContent = currentTenant;
        }

        if (displayApiKey) {
            displayApiKey.textContent = currentApiKey;
        }

        // Load stats
        loadStats();
    }


    /**
     * Load document stats
     */
    async function loadStats() {
        try {
            const response = await fetch('/api/rag/count', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(getAuthHeaders())
            });

            const data = await response.json();

            const docCount = document.getElementById('docCount');
            if (docCount) {
                docCount.textContent = data.count || 0;
            }
        } catch (error) {
            console.error('Load stats error:', error);
        }
    }


    // ==================
    // File Upload
    // ==================

    /**
     * Upload knowledge file
     */
    async function uploadKnowledge() {
        const fileInput = document.getElementById('knowledgeFile');
        const loading = document.getElementById('uploadLoading');

        if (!fileInput || !fileInput.files[0]) {
            alert('Please select a file');
            return;
        }

        if (loading) {
            loading.classList.add('active');
        }

        try {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const response = await fetch('/api/rag/upload', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: formData
            });

            const data = await response.json();

            if (loading) {
                loading.classList.remove('active');
            }

            if (data.success) {
                alert('✅ Uploaded ' + data.chunks + ' chunks!');
                loadStats();
            } else {
                alert(data.error || 'Upload failed');
            }
        } catch (error) {
            if (loading) {
                loading.classList.remove('active');
            }
            console.error('Upload error:', error);
            alert('Upload failed: ' + error.message);
        }
    }


    // ==================
    // Query
    // ==================

    /**
     * Query the knowledge base
     */
    async function query() {
        const queryInput = document.getElementById('queryText');
        const loading = document.getElementById('queryLoading');
        const resultsContainer = document.getElementById('queryResults');

        if (!queryInput || !queryInput.value.trim()) {
            alert('Please enter a question');
            return;
        }

        if (loading) {
            loading.classList.add('active');
        }

        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }

        try {
            const response = await fetch('/api/rag/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({
                    query: queryInput.value.trim(),
                    top_k: 3
                })
            });

            const data = await response.json();

            if (loading) {
                loading.classList.remove('active');
            }

            if (resultsContainer) {
                if (data.results && data.results.length) {
                    resultsContainer.innerHTML = data.results.map(function(result) {
                        return '<div class="result">' +
                            '<div class="result-score">Score: ' + Math.round(result.score * 100) + '%</div>' +
                            '<div class="result-text">' + result.document + '</div>' +
                            '</div>';
                    }).join('');
                } else {
                    resultsContainer.innerHTML = '<p class="text-dim">No results found</p>';
                }
            }
        } catch (error) {
            if (loading) {
                loading.classList.remove('active');
            }
            console.error('Query error:', error);
            alert('Query failed: ' + error.message);
        }
    }


    // ==================
    // Danger Zone
    // ==================

    /**
     * Clear all knowledge
     */
    async function clearKB() {
        if (!confirm('⚠️ Are you sure you want to delete ALL knowledge?\n\nThis cannot be undone!')) {
            return;
        }

        try {
            const response = await fetch('/api/rag/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getAuthHeaders()
                },
                body: JSON.stringify({})
            });

            const data = await response.json();

            if (data.success) {
                alert('✅ Knowledge base cleared');
                loadStats();
            } else {
                alert(data.error || 'Clear failed');
            }
        } catch (error) {
            console.error('Clear error:', error);
            alert('Clear failed: ' + error.message);
        }
    }


    // ==================
    // Initialize
    // ==================

    /**
     * Initialize on DOM load
     */
    function init() {
        // Attach event listeners
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', login);
        }

        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
        }

        const uploadBtn = document.getElementById('uploadBtn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', uploadKnowledge);
        }

        const queryBtn = document.getElementById('queryBtn');
        if (queryBtn) {
            queryBtn.addEventListener('click', query);
        }

        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', clearKB);
        }

        // Enter key for login
        const tenantIdInput = document.getElementById('tenantId');
        const passwordInput = document.getElementById('password');

        if (tenantIdInput && passwordInput) {
            passwordInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    login();
                }
            });
        }

        // Enter key for query
        const queryInput = document.getElementById('queryText');
        if (queryInput) {
            queryInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    query();
                }
            });
        }
    }


    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();