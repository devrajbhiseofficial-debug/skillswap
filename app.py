import os
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from questions import QUESTIONS

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///skillswap.db")
db = SQLAlchemy(app)
TEACH_MIN, LEARN_MAX = 80, 50  # score >= 80 can teach, < 50 wants to learn

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    college = db.Column(db.String(120), default="")
    pw = db.Column(db.String(255), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    subject = db.Column(db.String(40))
    score = db.Column(db.Integer)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

class Req(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    to_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    teach = db.Column(db.String(40), default="")
    learn = db.Column(db.String(40), default="")
    status = db.Column(db.String(10), default="pending")

try:
    with app.app_context():
        db.create_all()
except Exception as e:  # another worker may have created tables already
    print("db init:", e)

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("uid"):
            return jsonify(error="Please log in"), 401
        return f(*a, **k)
    return w

def scores_of(uid):
    return {s.subject: s.score for s in Score.query.filter_by(user_id=uid)}

def band(pct):
    """Subject points: 0% -> 0, 1-19% -> 5, 20-39% -> 10, 40-59% -> 15, 60-79% -> 20, 80-100% -> 25."""
    return 0 if pct <= 0 else 5 if pct < 20 else 10 if pct < 40 else 15 if pct < 60 else 20 if pct < 80 else 25

def level(sc):
    return "Expert" if sc >= TEACH_MIN else "Intermediate" if sc >= 50 else "Beginner"

@app.get("/")
def index():
    return app.send_static_file("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post("/api/register")
def register():
    d = request.get_json(force=True)
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower(), d.get("password") or ""
    if not name or "@" not in email or len(pw) < 6:
        return jsonify(error="Enter name, valid email and password (min 6 chars)"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 409
    u = User(name=name, email=email, college=(d.get("college") or "").strip(), pw=generate_password_hash(pw))
    db.session.add(u); db.session.commit()
    session["uid"] = u.id
    return jsonify(ok=True)

@app.post("/api/login")
def login():
    d = request.get_json(force=True)
    u = User.query.filter_by(email=(d.get("email") or "").strip().lower()).first()
    if not u or not check_password_hash(u.pw, d.get("password") or ""):
        return jsonify(error="Wrong email or password"), 401
    session["uid"] = u.id
    return jsonify(ok=True)

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

@app.get("/api/me")
@login_required
def me():
    u = db.session.get(User, session["uid"])
    sc = scores_of(u.id)
    return jsonify(id=u.id, name=u.name, college=u.college,
                   scores=[{"subject": k, "score": v, "level": level(v)} for k, v in sc.items()],
                   subjects=list(QUESTIONS))

@app.get("/api/quiz/<subject>")
@login_required
def quiz(subject):
    if subject not in QUESTIONS:
        return jsonify(error="Unknown subject"), 404
    return jsonify([{"q": q, "options": o} for q, o, _ in QUESTIONS[subject]])

@app.post("/api/quiz/<subject>/submit")
@login_required
def submit(subject):
    if subject not in QUESTIONS:
        return jsonify(error="Unknown subject"), 404
    ans = (request.get_json(force=True).get("answers") or [])
    qs = QUESTIONS[subject]
    correct = sum(1 for i, (_, _, a) in enumerate(qs) if i < len(ans) and ans[i] == a)
    pct = round(100 * correct / len(qs))
    s = Score.query.filter_by(user_id=session["uid"], subject=subject).first()
    if s: s.score, s.taken_at = pct, datetime.utcnow()
    else: db.session.add(Score(user_id=session["uid"], subject=subject, score=pct))
    db.session.commit()
    return jsonify(score=pct, correct=correct, total=len(qs), level=level(pct),
                   answers=[a for _, _, a in qs])

@app.get("/api/matches")
@login_required
def matches():
    uid = session["uid"]
    mine, out = scores_of(uid), []
    for o in User.query.filter(User.id != uid):
        th = scores_of(o.id)
        i_teach = [s for s in mine if mine[s] >= TEACH_MIN and s in th and th[s] < LEARN_MAX]
        they_teach = [s for s in th if th[s] >= TEACH_MIN and s in mine and mine[s] < LEARN_MAX]
        if i_teach or they_teach:
            out.append(dict(id=o.id, name=o.name, college=o.college, i_teach=i_teach,
                            they_teach=they_teach, mutual=bool(i_teach and they_teach)))
    out.sort(key=lambda m: (not m["mutual"], -(len(m["i_teach"]) + len(m["they_teach"]))))
    return jsonify(out)

@app.route("/api/requests", methods=["GET", "POST"])
@login_required
def requests_():
    uid = session["uid"]
    if request.method == "POST":
        d = request.get_json(force=True)
        to = db.session.get(User, d.get("to_id"))
        if not to or to.id == uid:
            return jsonify(error="Invalid user"), 400
        pair = ((Req.from_id == uid) & (Req.to_id == to.id)) | ((Req.from_id == to.id) & (Req.to_id == uid))
        if Req.query.filter(pair, Req.status == "accepted").first():
            return jsonify(error="You're already connected with " + to.name), 409
        if Req.query.filter_by(from_id=uid, to_id=to.id, status="pending").first():
            return jsonify(error="Request already sent. Wait for " + to.name + " to respond."), 409
        if Req.query.filter_by(from_id=to.id, to_id=uid, status="pending").first():
            return jsonify(error=to.name + " already sent you a request. Accept it in Requests."), 409
        db.session.add(Req(from_id=uid, to_id=to.id, teach=d.get("teach", ""), learn=d.get("learn", "")))
        db.session.commit()
        return jsonify(ok=True)
    def view(r, other_id):
        o = db.session.get(User, other_id)
        return dict(id=r.id, name=o.name, teach=r.teach, learn=r.learn, status=r.status,
                    email=o.email if r.status == "accepted" else None)
    inc = [view(r, r.from_id) for r in Req.query.filter_by(to_id=uid).order_by(Req.id.desc())]
    outg = [view(r, r.to_id) for r in Req.query.filter_by(from_id=uid).order_by(Req.id.desc())]
    return jsonify(incoming=inc, outgoing=outg)

@app.put("/api/requests/<int:rid>")
@login_required
def respond(rid):
    r = db.session.get(Req, rid)
    status = request.get_json(force=True).get("status")
    if not r or r.to_id != session["uid"] or status not in ("accepted", "declined"):
        return jsonify(error="Not allowed"), 400
    r.status = status; db.session.commit()
    return jsonify(ok=True)

@app.get("/api/leaderboard")
@login_required
def leaderboard():
    out = []
    for u in User.query:
        tg = extra.taught(u.id)
        if tg:
            out.append(dict(id=u.id, name=u.name, taught=tg, quizzes=len(tg),
                            avg=round(sum(t["total"] for t in tg) / len(tg), 1)))
    out.sort(key=lambda d: (-d["avg"], -d["quizzes"], d["name"].lower()))
    return jsonify(out[:10])

import extra  # noqa: E402,F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
