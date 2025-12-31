from flask import Flask, jsonify, request
import json
import gzip
import os
import subprocess

app = Flask(__name__)

DB_PATH = 'data/optimized_db.json.gz'
DB_URL = 'https://raw.githubusercontent.com/Yacoubs00/animetosho-attachments-viewer/main/data/optimized_db.json.gz'

def load_db():
    if not os.path.exists(DB_PATH):
        os.makedirs('data', exist_ok=True)
        print(f"Downloading latest DB from {DB_URL}...")
        subprocess.check_call(['curl', '-L', '-o', DB_PATH, DB_URL])

    print("Loading JSON database...")
    with gzip.open(DB_PATH, 'rt', encoding='utf-8') as f:
        return json.load(f)

db = load_db()

@app.route('/api/search')
def search():
    q = request.args.get('q', '').lower()
    lang = request.args.get('lang', '')
    limit = int(request.args.get('limit', 50))

    results = []
    for tid, info in db['torrents'].items():
        if q and q not in tid and q not in info['name'].lower():
            continue
        if lang and lang not in info['languages']:
            continue
        results.append({
            'nyaa_id': tid,
            'name': info['name'],
            'languages': info['languages'],
            'downloads': [s['url'] for sf in info['subtitle_files'] for s in sf['subs']]
        })
        if len(results) >= limit:
            break

    return jsonify({'results': results, 'count': len(results)})

@app.route('/api/languages')
def languages():
    return jsonify(list(db['languages'].keys()))

@app.route('/')
def home():
    return "AnimeTosho Subtitle API Live! Use /api/search?q=name&lang=eng"

if __name__ == '__main__':
    app.run()
