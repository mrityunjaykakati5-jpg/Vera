from flask import Flask, request
import sqlite3, os
app=Flask(__name__)
DB="vera_gudam.db"
def init_db():
    if not os.path.exists(DB):
        db=sqlite3.connect(DB)
        db.execute("CREATE TABLE pages (title TEXT, content TEXT)")
        pages=[("Assam","Assam is a state in northeastern India along Brahmaputra valley. Capital Dispur, largest city Guwahati. Known for tea, silk, rhino, Bihu."),("Bihu","Bihu is festival of Assam - Rongali, Kongali, Bhogali."),("Guwahati","Guwahati is largest city of Assam, gateway to Northeast. Kamakhya Temple here."),("Kaziranga","Kaziranga National Park home to one-horned rhino. UNESCO site.")]
        db.executemany("INSERT INTO pages VALUES (?,?)", pages)
        db.commit()
init_db()
def search(q):
    db=sqlite3.connect(DB)
    return db.execute("SELECT title, content FROM pages WHERE title LIKE ? OR content LIKE ? LIMIT 10", (f"%{q}%",f"%{q}%")).fetchall()
@app.route("/")
def home():
    q=request.args.get("q","")
    r=search(q) if q else []
    h=f"<html><head><meta name='viewport' content='width=device-width'><style>body{{font-family:arial;margin:15px}}.logo{{font-size:50px;text-align:center;color:#4285F4}}span{{color:#EA4335}}b{{color:#FBBC05}}i{{color:#4285F4}}.box{{text-align:center}}input{{width:90%;max-width:500px;padding:12px;border-radius:25px;border:1px solid #ccc}}.res{{max-width:700px;margin:20px auto}}.title{{color:#1a0dab;font-size:18px;font-weight:bold}}a.title{{display:block}}.link{{color:green;font-size:12px}}.sn{{color:#444}}</style></head><body><div class='logo'>V<span>e</span><b>r</b><i>a</i></div><div class='box'><form><input name='q' value='{q}'><br><br><button>Search</button></form></div>"
    for t,c in r: h+=f"<div class='res'><div class='link'>https://vera.com > {t}</div><a class='title' href='/page?q={t}'>{t}</a><div class='sn'>{c[:160]}...</div></div>"
    return h+"</body></html>"
@app.route("/page")
def page():
    q=request.args.get("q","");db=sqlite3.connect(DB);row=db.execute("SELECT title, content FROM pages WHERE title=?",(q,)).fetchone()
    if not row: return "Not found"
    t,c=row;return f"<html><body><a href='/'>← Vera</a><h1>{t}</h1><p>{c}</p></body></html>"
app.run(host="0.0.0.0",port=5000)
