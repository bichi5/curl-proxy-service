from flask import Flask, request, jsonify
import subprocess
import json
import sys

app = Flask(__name__)

@app.route('/proxy', methods=['GET'])
def proxy():
    """
    Proxy endpoint that executes curl commands on the server
    Usage: GET /proxy?url=<target_url>
    """
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({
            'error': 'Missing required parameter: url',
            'usage': '/proxy?url=<target_url>'
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
                    'url': target_url
                })
            except json.JSONDecodeError:
                return jsonify({
                    'success': True,
                    'data': result.stdout.strip(),
                    'url': target_url
                })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Curl command failed',
                'url': target_url
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Request timeout',
            'url': target_url
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'url': target_url
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'curl-proxy'
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
        'example': '/proxy?url=https://ipinfo.io/ip'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)