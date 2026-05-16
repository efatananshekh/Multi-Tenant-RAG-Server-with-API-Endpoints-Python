# Contributing to RAG Server

Thank you for your interest in contributing!

## Ways to Contribute

1. **Report bugs** - Open an issue with details
2. **Request features** - Open a feature request
3. **Add translations** - Add Bengali→English mappings
4. **Improve docs** - Fix typos or add examples
5. **Submit code** - Pull requests welcome

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/rag-server.git
cd rag-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to new functions
- Keep functions single-purpose

## Testing

```bash
# Test API endpoints
curl -X POST http://localhost:5555/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "test", "password": "test"}'
```

## Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit with clear messages
5. Push to your fork
6. Open a pull request

## Project Structure

```
src/
├── app.py          # Flask app + routes
├── config.py      # Configuration
├── auth.py        # Authentication
├── rag.py         # RAG Manager
├── chunking.py    # Text chunking
└── translation.py # Bengali translation
```

## Questions?

- Open an issue
- Check existing issues

**Thank you for contributing! 🎉**