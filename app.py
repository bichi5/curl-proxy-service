from flask import Flask, request, jsonify
import subprocess
import json
import sys
import time
from collections import defaultdict, deque
import threading

app = Flask(__name__)

# Rate limiting: 1 request per 10 seconds per IP
RATE_LIMIT_WINDOW = 10  # seconds
RATE_LIMIT_MAX_REQUESTS = 1
rate_limit_storage = defaultdict(deque)
rate_limit_lock = threading.Lock()

def check_rate_limit(client_ip):
    """
    Check if client IP is within rate limit
    Returns (allowed: bool, retry_after: float)
    """
    current_time = time.time()
    
    with rate_limit_lock:
        # Get client's request history
        client_requests = rate_limit_storage[client_ip]
        
        # Remove requests outside the time window
        while client_requests and client_requests[0] <= current_time - RATE_LIMIT_WINDOW:
            client_requests.popleft()
        
        # Check if limit is exceeded
        if len(client_requests) >= RATE_LIMIT_MAX_REQUESTS:
            # Calculate when the next request can be made
            oldest_request = client_requests[0]
            retry_after = oldest_request + RATE_LIMIT_WINDOW - current_time
            return False, retry_after
        
        # Add current request
        client_requests.append(current_time)
        return True, 0

@app.route('/proxy', methods=['GET'])
def proxy():
    """
    Proxy endpoint that executes curl commands on the server
    Usage: GET /proxy?url=<target_url>
    Rate limited to 1 request per second per IP
    """
    # Get client IP (handle proxy headers)
    client_ip = request.headers.get('X-Forwarded-For', 
                                   request.headers.get('X-Real-IP', 
                                                      request.remote_addr))
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
    else:
        client_ip = request.remote_addr or 'unknown'
    
    # Check rate limit
    allowed, retry_after = check_rate_limit(client_ip)
    if not allowed:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Maximum 1 request per 10 seconds allowed',
            'retry_after': f'{retry_after:.2f} seconds',
            'client_ip': client_ip
        }), 429
    
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({
            'error': 'Missing required parameter: url',
            'usage': '/proxy?url=<target_url>',
            'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
        }), 400
    
    # Additional security: validate URL format
    if not (target_url.startswith('http://') or target_url.startswith('https://')):
        return jsonify({
            'error': 'Invalid URL format',
            'message': 'URL must start with http:// or https://',
            'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
        }), 400
    
    try:
        # Execute curl command with security considerations
        result = subprocess.run([
            'curl', 
            '-s',  # Silent mode
            '-L',  # Follow redirects
            '--max-time', '10',  # Timeout after 10 seconds
            '--max-redirs', '5',  # Max 5 redirects
            target_url
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Try to parse as JSON, fallback to plain text
            try:
                response_data = json.loads(result.stdout)
                return jsonify({
                    'success': True,
                    'data': response_data,
                    'url': target_url,
                    'client_ip': client_ip,
                    'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
                })
            except json.JSONDecodeError:
                return jsonify({
                    'success': True,
                    'data': result.stdout.strip(),
                    'url': target_url,
                    'client_ip': client_ip,
                    'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
                })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Curl command failed',
                'url': target_url,
                'client_ip': client_ip,
                'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Request timeout',
            'url': target_url,
            'client_ip': client_ip,
            'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'url': target_url,
            'client_ip': client_ip,
            'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'curl-proxy',
        'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)',
        'security': 'enabled'
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with usage information"""
    return jsonify({
        'service': 'Curl Proxy Service',
        'usage': {
            'proxy': '/proxy?url=<target_url>',
            'health': '/health'
        },
        'example': '/proxy?url=https://ipinfo.io/ip',
        'rate_limit': f'{RATE_LIMIT_MAX_REQUESTS} request per {RATE_LIMIT_WINDOW} second(s)',
        'security_features': [
            'Rate limiting per IP',
            'URL validation',
            'Request timeouts',
            'Redirect limits'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)