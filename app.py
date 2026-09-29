import os
import secrets
import requests
from flask import Flask, request, jsonify, Response, abort

app = Flask(__name__)

@app.before_request
def service_identity():
    if request.path == '/health':
        return None
    key = os.environ.get('SERVICE_KEY', '')
    if not key:
        abort(503)
    if not secrets.compare_digest(request.headers.get('X-Service-Key', ''), key):
        abort(401)

@app.get('/health')
def health():
    return {'status': 'ready'}

def call(service, path, method='POST', **kwargs):
    headers = {'X-Service-Key': os.environ['SERVICE_KEY']}
    for key in ('X-User-Id', 'X-Tenant-Id'):
        if request.headers.get(key):
            headers[key] = request.headers[key]
    base = os.environ.get(service.upper() + '_URL', 'http://' + service + ':8080')
    return requests.request(method, base + path, headers=headers, timeout=10, **kwargs)

from flask import redirect

@app.get('/handoff')
def handoff():
    destination = request.args.get('next', '/home')
    return redirect(destination, code=302)

@app.get('/home')
def home():
    return {'message': 'Meridian workspace'}

@app.get('/continue')
def continue_route():
    destination = request.args.get('next', '/home')
    if not destination.startswith('/') or destination.startswith('//') or '\\' in destination:
        abort(400)
    return redirect(destination, code=302)
