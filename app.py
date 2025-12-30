from flask import Flask, jsonify, request
import pickle
import gzip
import os
import subprocess
import sys

app = Flask(__name__)

DB_PATH = 'data/optimized_db.pkl.gz'
DB_URL = 'https://raw.githubusercontent.com/Yacoubs00/animetosho-attachments-viewer/main/data/optimized_db.pkl.gz'

def load_db():
    if not os.path.exists(DB_PATH):
        os.makedirs('data', exist_ok=True)
        print(f"Database not found. Downloading from {DB_URL}...")
        subprocess.check_call(['curl', '-L', '-o', DB_PATH, DB_URL])
    
    print("Loading database into memory...")
    with gzip.open(DB_PATH, 'rb') as f:
        return pickle.load(f)

db = load_db()

@app.route('/api/search')
def search():
    query = request.args.get('q', '').lower()
    lang = request.args.get('lang', '')
    limit = int(request.args.get('limit', 50))

    results = []
    for tid, info in db['torrents'].items():
        if query and query not in tid and query not in info['name'].lower():
            continue
        if lang and lang not in info['languages']:
            continue
        downloads = []
        for sf in info['subtitle_files']:
            for sub in sf['subs']:
                downloads.append(sub['url'])
        results.append({
            'nyaa_id': tid,
            'name': info['name'],
            'languages': info['languages'],
            'downloads': downloads
        })
        if len(results) >= limit:
            break

    return jsonify({'results': results, 'total': len(results), 'cached': True})

@app.route('/api/languages')
def languages():
    return jsonify({'languages': sorted(db['languages'].keys())})

@app.route('/api/stats')
def stats():
    return jsonify(db.get('stats', {}))

@app.route('/')
def home():
    return "AnimeTosho Subtitle Search API - Live! Use /api/search?q=query&lang=eng"

if __name__ == '__main__':
    app.run()
