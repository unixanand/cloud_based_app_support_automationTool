FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health checks (minimal, as you have)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy app code
COPY . .

# Create non-root user for security (ECS best practice)
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (matches CMD)
EXPOSE 8080

# Healthcheck using curl (integrates with ECS task/TG health checks)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1

# Run Streamlit (your flags are good; added --server.headless true for container env)
CMD ["streamlit", "run", "support_automation.py", \
     "--server.port", "8080", \
     "--server.address", "0.0.0.0", \
     "--server.enableCORS", "false", \
     "--server.enableXsrfProtection", "false", \
     "--browser.gatherUsageStats", "false", \
     "--server.headless", "true"]