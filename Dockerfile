FROM python:3.12-slim

# Install system dependencies needed for compiling python packages (like ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /app

# Create a non-root user for Hugging Face Spaces security compliance
RUN useradd -m -u 1000 user

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files and assign ownership to the non-root user
COPY --chown=user:user . .

# Ensure the database and temp upload directories are writeable by the user
RUN mkdir -p data/temp db && chown -R user:user /app

# Switch to the non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose port 7860 (Hugging Face Spaces default port)
EXPOSE 7860

# Command to:
# 1. Run the database ingestion script to embed transcripts and write to local ChromaDB
# 2. Start the Uvicorn FastAPI server on port 7860
CMD ["sh", "-c", "python ingest.py && uvicorn main:app --host 0.0.0.0 --port 7860"]
