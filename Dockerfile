FROM python:3.11-slim

LABEL maintainer="RAG Server"
LABEL description="Multi-tenant RAG API server with ChromaDB"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p uploads rag_db

# Expose port
EXPOSE 5555

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=5555

# Run application
CMD ["python", "app.py"]