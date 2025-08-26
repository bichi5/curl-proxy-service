# Use Alpine Linux with Python for minimal size
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install curl and other necessary packages
RUN apk add --no-cache curl

# Install Flask
RUN pip install --no-cache-dir flask

# Copy application code
COPY app.py .

# Create non-root user for security
RUN adduser -D -s /bin/sh appuser
USER appuser

# Expose port 5001
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

# Run the application
CMD ["python", "app.py"]