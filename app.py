
from flask import Flask, request, jsonify, Response
import sqlite3, os

app = Flask(__name__)
DB="vera_gudam.db"

def init_db():
    if not os.path.exists(DB):
        db=sqlite3.connect(DB)
        db.execute("CREATE TABLE pages (title TEXT, content TEXT)")
        pages=[
            ("Assam","Assam is a state in northeastern India, known for tea and Brahmaputra river."),
            ("Guwahati","Guwahati is the largest city of Assam, gateway to Northeast India."),
            ("EveryoneOS","EveryoneOS is an open OS concept for everyone."),
            ("Vera Search","Vera is a search engine by EveryoneOS."),
        ]
        db.executemany("INSERT INTO pages VALUES (?,?)", pages)
        db.commit()

init_db()

def search(q):
    db=sqlite3.connect(DB)
    return db.execute("SELECT title, content FROM pages WHERE title LIKE ? OR content LIKE ?", (f"%{q}%", f"%{q}%")).fetchall()

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vera - Everyone Search</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#000000">
<link rel="icon" href="https://cdn-icons-png.flaticon.com/512/122/122932.png">
<style>
body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui;padding:0}
.header{padding:25px 15px;text-align:center}
.search-box{margin:25px auto;max-width:600px;display:flex;gap:8px;padding:0 15px}
input{flex:1;padding:16px 20px;border-radius:30px;border:0;font-size:17px}
button{padding:16px 26px;border-radius:30px;border:0;background:#fff;color:#000;font-weight:900}
.results{max-width:700px;margin:0 auto;text-align:left;padding:10px 20px}
.res{background:#1a1a1a;padding:15px;border-radius:15px;margin-bottom:12px}
a{color:#fff;text-decoration:none}
</style>
</head>
<body>
<div class="header">
<h1>VERA</h1>
<p style="color:#888">Everyone Search</p>
<div class="search-box">
<input id="q" value="{q}" placeholder="Search anything..." onkeydown="if(event.key==='Enter')doSearch()">
<button onclick="doSearch()">Search</button>
</div>
</div>
<div class="results">{results_html}</div>
<script>
function doSearch(){let q=document.getElementById('q').value; if(!q) return; location.href='/?q='+encodeURIComponent(q);}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    q=request.args.get("q","")
    r=search(q) if q else []
    results_html=""
    for t,c in r: results_html+=f"<a href='/page?q={t}'><div class='res'><b>{t}</b><p>{c}</p></div></a>"
    if not q: results_html="<div style='text-align:center;color:#666;margin-top:30px'>Type something to search...</div>"
    if q and not r: results_html=f"<div class='res'><b>No results for '{q}'</b></div>"
    return HTML_BASE.format(q=q, results_html=results_html)

@app.route('/page')
def page():
    q=request.args.get("q","")
    db=sqlite3.connect(DB)
    row=db.execute("SELECT title, content FROM pages WHERE title=?", (q,)).fetchone()
    if not row: return "Not found <a href='/'>Home</a>"
    t,c=row
    return f"<html><head><meta name='viewport' content='width=device-width'><style>body{{background:#000;color:#fff;font-family:system-ui;padding:20px}}a{{color:#fff}}</style></head><body><a href='/'>Back</a><h1>{t}</h1><p>{c}</p></body></html>"

@app.route('/manifest.json')
def manifest():
    return jsonify({"name":"Vera - Everyone Search","short_name":"Vera","start_url":"/","display":"standalone","background_color":"#000000","theme_color":"#000000","icons":[{"src":"https://cdn-icons-png.flaticon.com/512/122/122932.png","sizes":"192x192","type":"image/png"},{"src":"https://cdn-icons-png.flaticon.com/512/122/122932.png","sizes":"512x512","type":"image/png"}]})

@app.route('/sw.js')
def sw():
    return Response("self.addEventListener('install', e=>self.skipWaiting());self.addEventListener('activate', e=>self.clients.claim());", mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
