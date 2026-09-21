import os,sqlite3,random
from datetime import datetime
from flask import Flask,render_template,request,jsonify,session
app=Flask(__name__); app.secret_key=os.getenv("SECRET_KEY","change-me"); DB=os.getenv("DB_PATH","data/foxy.db")
os.makedirs(os.path.dirname(DB) or ".",exist_ok=True)
LEVELS=[(1,0),(2,300),(3,700),(4,1200),(5,2000),(6,3000),(7,4500),(8,6500),(9,9000),(10,12000)]
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.execute("CREATE TABLE IF NOT EXISTS players(id TEXT PRIMARY KEY,skill TEXT DEFAULT '',xp INTEGER DEFAULT 0,hours REAL DEFAULT 0,streak INTEGER DEFAULT 0,last_day TEXT DEFAULT '',sessions INTEGER DEFAULT 0,chats INTEGER DEFAULT 0)")
 c.commit(); return c
def pid():
 if "pid" not in session: session["pid"]=os.urandom(16).hex()
 return session["pid"]
def player():
 c=db(); p=c.execute("SELECT * FROM players WHERE id=?",(pid(),)).fetchone()
 if not p: c.execute("INSERT INTO players(id) VALUES(?)",(pid(),)); c.commit(); p=c.execute("SELECT * FROM players WHERE id=?",(pid(),)).fetchone()
 d=dict(p); c.close(); return d
def level(x):
 n=1
 for a,b in LEVELS:
  if x>=b:n=a
 return n
def fox(t,e="😎"): return f"🦊 **Фокси** {e}: {t}"
@app.route("/")
def home(): return render_template("index.html")
@app.get("/health")
def health(): return jsonify(status="ok")
@app.get("/api/state")
def state():
 p=player(); p["level"]=level(p["xp"]); return jsonify(p)
@app.post("/api/skill")
def skill():
 s=(request.json or {}).get("skill","").strip()[:120]
 if not s:return jsonify(message=fox("Назови навык — и я достану карту приключения!","👀")),400
 c=db(); c.execute("UPDATE players SET skill=? WHERE id=?",(s,pid())); c.commit(); c.close()
 return jsonify(message=fox(f"Ого! «{s}» — наша новая миссия. Разложим её на маленькие победы!","🤩"))
@app.post("/api/session")
def practice():
 c=db(); p=c.execute("SELECT * FROM players WHERE id=?",(pid(),)).fetchone(); today=datetime.now().date().isoformat()
 bonus=25 if p["last_day"]!=today else 0; streak=p["streak"]+(p["last_day"]!=today); gained=100+bonus
 c.execute("UPDATE players SET xp=xp+?,sessions=sessions+1,streak=?,last_day=? WHERE id=?",(gained,streak,today,pid())); c.commit(); c.close()
 return jsonify(message=fox(f"СЕССИЯ ЗАВЕРШЕНА! +{gained} XP! Я даже очки уронил! 🤓💥","🥳"))
@app.post("/api/hours")
def hours():
 try:h=float((request.json or {}).get("hours",0))
 except:h=0
 if not 0<h<=8:return jsonify(message=fox("Введи от 0.1 до 8 часов.","🤨")),400
 c=db(); c.execute("UPDATE players SET hours=hours+?,xp=xp+100 WHERE id=?",(h,pid())); c.commit(); c.close()
 return jsonify(message=fox(f"+{h:g} ч практики и +100 XP!","😎"))
@app.post("/api/task")
def task():
 c=db(); c.execute("UPDATE players SET xp=xp+50 WHERE id=?",(pid(),)); c.commit(); c.close()
 return jsonify(message=fox("Задание выполнено! +50 XP. Чистая работа! 🦊","😏"))
@app.get("/api/plan")
def plan():
 s=player()["skill"] or "твой навык"; return jsonify(message=fox(f"План для «{s}»: база → ошибки → практика → реальные мини-задачи → финальный челлендж. Всего 20 часов.","🧠"))
@app.get("/api/boss")
def boss():
 s=player()["skill"] or "твой навык"; return jsonify(message=fox(f"МИНИ-БОСС: за 15 минут сделай маленький результат по «{s}» без подсказок.","⚔️"))
@app.post("/api/chat")
def chat():
 c=db(); c.execute("UPDATE players SET chats=chats+1 WHERE id=?",(pid(),)); c.commit(); c.close()
 return jsonify(reply=fox(random.choice(["Давай разобьём задачу на один маленький шаг.","Начни с 20 минут практики.","Сделал → получил обратную связь → поправил → повторил. 🦊","Ошибка — это карта, где спрятан следующий XP!"]),"🧠"))
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")))
