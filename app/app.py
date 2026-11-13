"""
MyMiniCloud - Application Backend Server (Flask API)

Endpoints:
  GET  /                 -> danh sach endpoint
  GET  /health           -> health check
  GET  /hello            -> {"message": "Hello from App Server!"}
  GET  /secure           -> yeu cau Bearer token (OIDC - Keycloak)
  GET  /student          -> danh sach sinh vien tu file students.json      (mo rong 2)
  GET  /notes            -> du lieu bang minicloud.notes (MariaDB)
  GET  /students-db      -> danh sach sinh vien tu MariaDB studentdb      (mo rong 3)
  GET  /students-db/<id> -> 1 sinh vien
  POST /students-db      -> them sinh vien  (JSON body)
  PUT  /students-db/<id> -> cap nhat sinh vien
  DELETE /students-db/<id> -> xoa sinh vien

Neu request tu trinh duyet (Accept: text/html) thi /student va /students-db
tra ve bang HTML; con lai (curl, Postman, ?format=json) tra ve JSON.
"""
import html
import json
import os
import socket
import time

import pymysql
import requests
from flask import Flask, jsonify, request
from jose import jwt

# ---------------------------------------------------------------- cau hinh ---
# ISSUER noi bo (dung de lay JWKS qua Docker network)
ISSUER = os.getenv(
    "OIDC_ISSUER",
    "http://authentication-identity-server:8080/auth/realms/realm_sv001",
)
REALM = os.getenv("OIDC_REALM", ISSUER.rstrip("/").rsplit("/", 1)[-1])
AUDIENCE = os.getenv("OIDC_AUDIENCE", "flask-app")
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

DB_HOST = os.getenv("DB_HOST", "relational-database-server")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")
DB_NAME = os.getenv("DB_NAME", "studentdb")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")

app = Flask(__name__)
app.json.ensure_ascii = False  # giu nguyen tieng Viet trong JSON
app.json.sort_keys = False

# ------------------------------------------------------------------- JWKS ---
_JWKS_CACHE = {}
KC_BASE_URL = os.getenv(
    "KC_BASE_URL",
    "http://authentication-identity-server:8080/auth",
)
ALLOWED_REALMS = {"realm_sv001", "realm_52300262", "master", REALM}


def get_jwks(realm=REALM, force=False):
    """Lay bo khoa cong khai cua Keycloak theo realm, cache 10 phut."""
    now = time.time()
    cached = _JWKS_CACHE.get(realm)
    if force or not cached or now - cached[1] > 600:
        url = f"{KC_BASE_URL.rstrip('/')}/realms/{realm}/protocol/openid-connect/certs"
        data = requests.get(url, timeout=5).json()
        _JWKS_CACHE[realm] = (data, now)
        return data
    return cached[0]


def find_signing_key(token, realm=REALM):
    kid = jwt.get_unverified_header(token).get("kid")
    for force in (False, True):  # thu lai 1 lan neu Keycloak da xoay khoa
        for key in get_jwks(realm, force).get("keys", []):
            if key.get("kid") == kid and key.get("use", "sig") == "sig":
                return key
    raise ValueError("Khong tim thay signing key phu hop (kid=%s, realm=%s)" % (kid, realm))


# ------------------------------------------------------------------ helper ---
def wants_html():
    if request.args.get("format") == "json":
        return False
    if request.args.get("format") == "html":
        return True
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "text/html" and request.accept_mimetypes["text/html"] > request.accept_mimetypes["application/json"]


def html_table(title, rows, columns, color="#4f46e5"):
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in columns) + "</tr>"
        for r in rows
    )
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#f5f6fb;margin:40px;color:#1f2937}}
h2{{color:{color}}} table{{border-collapse:collapse;min-width:640px;background:#fff;
box-shadow:0 4px 18px rgba(0,0,0,.08);border-radius:10px;overflow:hidden}}
th{{background:{color};color:#fff;text-align:left;padding:10px 16px}}
td{{padding:9px 16px;border-bottom:1px solid #eee}} tr:nth-child(even) td{{background:#fafafa}}
small{{color:#6b7280}}</style></head><body>
<h2>{html.escape(title)}</h2><table><tr>{head}</tr>{body}</table>
<p><small>Served by container <b>{html.escape(socket.gethostname())}</b> &middot;
Them <code>?format=json</code> de xem JSON</small></p></body></html>"""


def db_conn(database=DB_NAME):
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD,
        database=database, charset="utf8mb4", connect_timeout=5,
        cursorclass=pymysql.cursors.DictCursor, autocommit=True,
    )


def serialize(row):
    out = {}
    for k, v in row.items():
        out[k] = v.isoformat() if hasattr(v, "isoformat") else v
    return out


# ------------------------------------------------------------------ routes ---
@app.get("/")
def index():
    return jsonify(
        service="application-backend-server",
        container=socket.gethostname(),
        endpoints=["/hello", "/secure", "/student", "/notes", "/students-db",
                   "/students-db/<id> (GET, PUT, DELETE)", "POST /students-db", "/health"],
    )


@app.get("/health")
def health():
    return jsonify(status="ok", time=int(time.time()))


@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")


@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ", 1)[1]
    try:
        unverified_claims = jwt.get_unverified_claims(token)
        iss = unverified_claims.get("iss", "")
        token_realm = iss.rstrip("/").rsplit("/", 1)[-1] if "/realms/" in iss else REALM
        if token_realm not in ALLOWED_REALMS:
            return jsonify(error=f"Invalid issuer realm: {iss}"), 401
        key = find_signing_key(token, token_realm)
        payload = jwt.decode(
            token, key, algorithms=["RS256"],
            options={"verify_iss": False, "verify_aud": False},
        )
        return jsonify(
            message="Secure resource OK",
            preferred_username=payload.get("preferred_username"),
            realm=token_realm,
            issuer=iss,
            audience=payload.get("aud"),
            expires_at=payload.get("exp"),
        )
    except requests.RequestException as e:
        return jsonify(error=f"Khong ket noi duoc Keycloak: {e}"), 503
    except Exception as e:  # token sai / het han / sai audience
        return jsonify(error=str(e)), 401


@app.get("/student")
@app.get("/student/")
def student():
    with open(STUDENTS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    if wants_html():
        return html_table("Danh sách sinh viên (JSON)", data, ["id", "name", "major", "gpa"])
    return jsonify(data)


@app.get("/notes")
def notes():
    try:
        with db_conn("minicloud") as conn, conn.cursor() as cur:
            cur.execute("SELECT id, title, created_at FROM notes ORDER BY id")
            rows = [serialize(r) for r in cur.fetchall()]
        return jsonify(rows)
    except Exception as e:
        return jsonify(error=str(e)), 500


COLUMNS = ["id", "student_id", "fullname", "dob", "major"]


@app.get("/students-db")
@app.get("/students-db/")
def students_db_list():
    try:
        with db_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT id, student_id, fullname, dob, major FROM students ORDER BY id")
            rows = [serialize(r) for r in cur.fetchall()]
    except Exception as e:
        return jsonify(error=f"Database error: {e}"), 500
    if wants_html():
        return html_table("Danh sách sinh viên (MariaDB)", rows, COLUMNS, color="#16a34a")
    return jsonify(rows)


@app.get("/students-db/<int:sid>")
def students_db_get(sid):
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, student_id, fullname, dob, major FROM students WHERE id=%s", (sid,))
        row = cur.fetchone()
    if not row:
        return jsonify(error="Not found"), 404
    return jsonify(serialize(row))


@app.post("/students-db")
def students_db_create():
    d = request.get_json(force=True, silent=True) or {}
    missing = [k for k in ("student_id", "fullname") if not d.get(k)]
    if missing:
        return jsonify(error=f"Thieu truong: {', '.join(missing)}"), 400
    with db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO students(student_id, fullname, dob, major) VALUES (%s,%s,%s,%s)",
            (d["student_id"], d["fullname"], d.get("dob"), d.get("major")),
        )
        new_id = cur.lastrowid
    return jsonify(message="Created", id=new_id), 201


@app.put("/students-db/<int:sid>")
def students_db_update(sid):
    d = request.get_json(force=True, silent=True) or {}
    fields = {k: d[k] for k in ("student_id", "fullname", "dob", "major") if k in d}
    if not fields:
        return jsonify(error="Khong co truong nao de cap nhat"), 400
    sets = ", ".join(f"{k}=%s" for k in fields)
    with db_conn() as conn, conn.cursor() as cur:
        n = cur.execute(f"UPDATE students SET {sets} WHERE id=%s", (*fields.values(), sid))
    if n == 0:
        return jsonify(error="Not found or unchanged"), 404
    return jsonify(message="Updated", id=sid)


@app.delete("/students-db/<int:sid>")
def students_db_delete(sid):
    with db_conn() as conn, conn.cursor() as cur:
        n = cur.execute("DELETE FROM students WHERE id=%s", (sid,))
    if n == 0:
        return jsonify(error="Not found"), 404
    return jsonify(message="Deleted", id=sid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, threaded=True)
