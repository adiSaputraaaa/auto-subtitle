# Menggunakan image base Python yang ringan
FROM python:3.12-slim

# Menginstall ffmpeg (sering dibutuhkan untuk memproses video & audio)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Menginstall uv (package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Menentukan working directory
WORKDIR /app

# Copy file dependency list
COPY pyproject.toml .
# Jika kamu sudah memiliki uv.lock hasil dari `uv add`, kamu bisa uncomment line di bawah:
# COPY uv.lock .

# Melakukan instalasi dependency menggunakan uv
RUN uv sync --no-dev

# Copy seluruh source code
COPY . .

# Default command saat container dijalankan
CMD ["uv", "run", "main.py"]
