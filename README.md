# Curl Proxy Service

A lightweight Python Flask service that acts as a proxy to execute curl commands on the server. This service allows you to make HTTP requests through a containerized environment with curl capabilities.

**Coded by** bichi5@gmail.com

## Features

- 🐍 **Minimal Python Alpine image** - Small footprint (~50MB)
- 🔒 **Security-focused** - Rate limiting, URL validation, non-root user
- ⏱️ **Rate limiting** - Maximum 1 request per 10 seconds per IP address
- 🚀 **Easy deployment** - Docker and Docker Compose ready
- 💡 **Simple API** - RESTful endpoint with JSON responses
- 🏥 **Health checks** - Built-in health monitoring
- ⚡ **Fast responses** - Optimized for quick curl operations

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd curl-proxy-service

# Build and run
docker-compose up -d

# Check if it's running
curl http://localhost:5001/health
```

### Using Docker

```bash
# Build the image
docker build -t curl-proxy .

# Run the container
docker run -d -p 5001:5001 --name curl-proxy-service curl-proxy

# Test the service
curl http://localhost:5001/health
```

## API Usage

### Proxy Endpoint

Make HTTP requests through the proxy:

```bash
# Basic usage
curl "http://localhost:5001/proxy?url=https://ipinfo.io/ip"

# Another example
curl "http://localhost:5001/proxy?url=https://httpbin.org/json"
```

**Response format:**
```json
{
  "success": true,
  "data": "your-ip-address",
  "url": "https://ipinfo.io/ip",
  "client_ip": "192.168.1.100",
  "rate_limit": "1 request per 10 second(s)"
}
```

**Rate limiting response (HTTP 429):**
```json
{
  "error": "Rate limit exceeded",
  "message": "Maximum 1 request per 10 seconds allowed", 
  "retry_after": "7.25 seconds",
  "client_ip": "192.168.1.100"
}
```

### Health Check

```bash
curl http://localhost:5001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "curl-proxy",
  "rate_limit": "1 request per 10 second(s)",
  "security": "enabled"
}
```

### Service Information

```bash
curl http://localhost:5001/
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/proxy` | GET | Execute curl request to specified URL |
| `/health` | GET | Service health check |
| `/` | GET | Service information and usage |

### Parameters

- `url` (required): Target URL for the curl request

### Security Features

- **Rate limiting**: 1 request per 10 seconds per IP address
- **URL validation**: Only http:// and https:// URLs allowed
- **Request timeout**: 15 seconds maximum
- **Curl timeout**: 10 seconds maximum
- **Maximum redirects**: 5 redirects
- **Non-root user**: Runs as non-privileged user
- **Input validation**: Validates all input parameters

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployments

### Port Configuration

The service runs on port `5001` by default. You can change this in:
- `docker-compose.yml`: Update the port mapping
- `Dockerfile`: Update the EXPOSE directive
- `app.py`: Update the Flask app configuration

## Development

### Local Development

```bash
# Install dependencies
pip install flask

# Run locally
python app.py
```

### Building Custom Image

```bash
# Build with custom tag
docker build -t your-username/curl-proxy:latest .

# Push to registry
docker push your-username/curl-proxy:latest
```

## Troubleshooting

### Service Not Responding

```bash
# Check container logs
docker-compose logs curl-proxy

# Check if container is running
docker-compose ps
```

### Health Check Failing

```bash
# Manual health check
curl -v http://localhost:5001/health

# Check container health
docker inspect curl-proxy-service --format='{{.State.Health.Status}}'
```

### Common Issues

1. **Port already in use**: Change the port mapping in `docker-compose.yml`
2. **Permission denied**: Ensure Docker has proper permissions
3. **Network issues**: Check if the target URL is accessible from the container
4. **Rate limit errors**: Wait 10 seconds between requests from the same IP
5. **Invalid URL**: Ensure URLs start with http:// or https://

## Production Deployment

### Docker Compose Production

```bash
# Run in production mode
docker-compose -f docker-compose.yml up -d

# Monitor logs
docker-compose logs -f curl-proxy
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security Notice

This service executes curl commands on the server with built-in security measures:

- **Rate limiting**: 1 request per 10 seconds per IP address prevents abuse
- **URL validation**: Only valid HTTP/HTTPS URLs are accepted
- **Timeout controls**: Prevents hanging requests
- **Non-root execution**: Container runs with limited privileges

Additional recommendations for production:
- Network segmentation
- Firewall rules
- Request logging and monitoring
- Reverse proxy with additional rate limiting
- SSL/TLS termination

## Support

If you encounter any issues or have questions, please open an issue on GitHub.