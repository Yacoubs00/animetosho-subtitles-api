from flask import Flask, jsonify, request
import pickle
import gzip
import os

app = Flask(__name__)

# Load DB once at startup
DB_PATH = 'data/optimized_db.pkl.gz'
db = None

with gzip.open(DB_PATH, 'rb') as f:
    db = pickle.load(f)

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
        results.append({
            'nyaa_id': tid,
            'name': info['name'],
            'languages': info['languages'],
            'downloads': [sub['url'] for sf in info['subtitle_files'] for sub in sf['subs']]
        })
        if len(results) >= limit:
            break

    return jsonify({'results': results, 'total': len(results)})

@app.route('/api/languages')
def languages():
    return jsonify({'languages': list(db['languages'].keys())})

@app.route('/')
def home():
    return "AnimeTosho Subtitle Search API - Live!"

if __name__ == '__main__':
    app.run()
