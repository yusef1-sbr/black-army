from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    abort
)

import sqlite3
import os
import secrets
import hmac
import time

from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "black_army.db"
SECRET_FILE = BASE_DIR / ".secret_key"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)


# =========================================================
# SECRET KEY
# =========================================================

def load_secret_key():
    """
    کلید نشست‌ها را یک بار تولید می‌کند و داخل فایل محلی نگه می‌دارد.
    بنابراین با هر بار اجرای برنامه، session ها خراب نمی‌شوند.
    """

    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()

    key = secrets.token_hex(32)
    SECRET_FILE.write_text(key, encoding="utf-8")

    return key


app.secret_key = load_secret_key()

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# =========================================================
# ADMIN CONFIG
# =========================================================

DEFAULT_ADMIN_PASSWORD = os.environ.get(
    "BLACK_ARMY_ADMIN_PASSWORD",
    "1234"
)

ADMIN_USERNAME = "owner"


# =========================================================
# COMMAND STRUCTURE
# =========================================================

COMMAND_STRUCTURE = {
    "owners": [
        {
            "name": "امیر",
            "alias": "گاد گوجو",
            "rank": "Owner"
        },
        {
            "name": "یوسف",
            "alias": "سوبارو",
            "rank": "Owner"
        },
        {
            "name": "کیان",
            "alias": "والتر وایت",
            "rank": "Owner"
        }
    ],

    "leader_1": [
        {"name": "هری", "alias": "", "rank": "Leader 1"},
        {"name": "النا", "alias": "", "rank": "Leader 1"},
        {"name": "طاها", "alias": "", "rank": "Leader 1"}
    ],

    "leader_2": [
        {"name": "کیت کت", "alias": "", "rank": "Leader 2"},
        {"name": "آرتین", "alias": "هیتلر", "rank": "Leader 2"},
        {"name": "آرتین", "alias": "توجی", "rank": "Leader 2"},
        {"name": "ارسلان", "alias": "", "rank": "Leader 2"},
        {"name": "آیزن", "alias": "", "rank": "Leader 2"},
        {"name": "ساکوما", "alias": "", "rank": "Leader 2"},
        {"name": "اونیکس", "alias": "", "rank": "Leader 2"},
        {"name": "هل بلید", "alias": "", "rank": "Leader 2"}
    ],

    "leader_3": [
        {"name": "علی", "alias": "", "rank": "Leader 3"},
        {"name": "راکتور", "alias": "", "rank": "Leader 3"},
        {"name": "رها", "alias": "", "rank": "Leader 3"},
        {"name": "یوجی", "alias": "", "rank": "Leader 3"}
    ]
}


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():
    conn = get_db()

    # -------------------------
    # Admin users
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # News
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # Join requests
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS join_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            aparat_id TEXT,
            rubika_id TEXT,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # Anonymous messages
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS anonymous_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # Stats
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            wins INTEGER NOT NULL DEFAULT 2500,
            losses INTEGER NOT NULL DEFAULT 0,
            truces INTEGER NOT NULL DEFAULT 15
        )
    """)

    # -------------------------
    # Members
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            join_request_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            aparat_id TEXT,
            rubika_id TEXT,
            rank TEXT NOT NULL DEFAULT 'عضو',
            bio TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(join_request_id)
                REFERENCES join_requests(id)
                ON DELETE SET NULL
        )
    """)

    # -------------------------
    # Relations
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # Honors
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS honors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date_label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # History
    # -------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS history_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_label TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # DEFAULT ADMIN
    # =====================================================

    admin_exists = conn.execute(
        "SELECT id FROM admin_users WHERE username = ?",
        (ADMIN_USERNAME,)
    ).fetchone()

    if not admin_exists:
        conn.execute(
            """
            INSERT INTO admin_users (username, password_hash)
            VALUES (?, ?)
            """,
            (
                ADMIN_USERNAME,
                generate_password_hash(DEFAULT_ADMIN_PASSWORD)
            )
        )

    # =====================================================
    # DEFAULT STATS
    # =====================================================

    stats_exists = conn.execute(
        "SELECT id FROM stats WHERE id = 1"
    ).fetchone()

    if not stats_exists:
        conn.execute(
            """
            INSERT INTO stats (id, wins, losses, truces)
            VALUES (1, 2500, 0, 15)
            """
        )

    # =====================================================
    # DEFAULT RELATIONS
    # =====================================================

    relation_count = conn.execute(
        "SELECT COUNT(*) AS c FROM relations"
    ).fetchone()["c"]

    if relation_count == 0:

        alliances = [
            ("alliance", "Dikarin", "اتحاد"),
            ("alliance", "Motahedin", "اتحاد"),
            ("alliance", "Mobarezan Naboodgar", "اتحاد"),
            ("alliance", "Black Souls Army", "اتحاد"),
            ("alliance", "Death", "اتحاد")
        ]

        enemy = [
            ("enemy", "Tarman", "دشمن")
        ]

        for item in alliances + enemy:
            conn.execute(
                """
                INSERT INTO relations
                (kind, name, description)
                VALUES (?, ?, ?)
                """,
                item
            )

    conn.commit()
    conn.close()


# =========================================================
# CSRF
# =========================================================

def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


app.jinja_env.globals["csrf_token"] = get_csrf_token


def verify_csrf():
    session_token = session.get("csrf_token", "")
    form_token = request.form.get("csrf_token", "")

    if not session_token or not form_token:
        abort(400)

    if not hmac.compare_digest(session_token, form_token):
        abort(400)


# =========================================================
# AUTH HELPERS
# =========================================================

def is_owner():
    return bool(session.get("owner_logged_in"))


def owner_required():
    if not is_owner():
        return redirect(url_for("admin_login"))

    return None


# =========================================================
# LOGIN RATE LIMIT
# =========================================================

FAILED_LOGINS = {}

MAX_LOGIN_ATTEMPTS = 6
LOGIN_WINDOW = 300


def login_allowed(ip):
    now = time.time()

    attempts = FAILED_LOGINS.get(ip, [])

    attempts = [
        t for t in attempts
        if now - t < LOGIN_WINDOW
    ]

    FAILED_LOGINS[ip] = attempts

    return len(attempts) < MAX_LOGIN_ATTEMPTS


def register_failed_login(ip):
    FAILED_LOGINS.setdefault(ip, []).append(time.time())


# =========================================================
# TEMPLATE CONTEXT
# =========================================================

@app.context_processor
def inject_common():
    return {
        "command_structure": COMMAND_STRUCTURE,
        "owner_logged_in": is_owner()
    }


# =========================================================
# PUBLIC HOME
# =========================================================

@app.route("/")
def home():

    conn = get_db()

    news = conn.execute("""
        SELECT *
        FROM news
        ORDER BY id DESC
        LIMIT 12
    """).fetchall()

    stats = conn.execute("""
        SELECT *
        FROM stats
        WHERE id = 1
    """).fetchone()

    members = conn.execute("""
        SELECT *
        FROM members
        WHERE status = 'active'
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()

    alliances = conn.execute("""
        SELECT *
        FROM relations
        WHERE kind = 'alliance'
        ORDER BY id DESC
    """).fetchall()

    enemies = conn.execute("""
        SELECT *
        FROM relations
        WHERE kind = 'enemy'
        ORDER BY id DESC
    """).fetchall()

    honors = conn.execute("""
        SELECT *
        FROM honors
        ORDER BY id DESC
        LIMIT 12
    """).fetchall()

    history = conn.execute("""
        SELECT *
        FROM history_events
        ORDER BY id DESC
        LIMIT 15
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        news=news,
        stats=stats,
        members=members,
        alliances=alliances,
        enemies=enemies,
        honors=honors,
        history=history
    )


# =========================================================
# JOIN REQUEST
# =========================================================

@app.route("/join", methods=["POST"])
def join_request():

    verify_csrf()

    name = request.form.get("name", "").strip()
    aparat_id = request.form.get("aparat_id", "").strip()
    rubika_id = request.form.get("rubika_id", "").strip()
    description = request.form.get("description", "").strip()

    if not name or not description:
        return redirect(url_for("home") + "#join")

    if len(name) > 80:
        return redirect(url_for("home") + "#join")

    if len(aparat_id) > 120 or len(rubika_id) > 120:
        return redirect(url_for("home") + "#join")

    if len(description) > 1200:
        return redirect(url_for("home") + "#join")

    conn = get_db()

    conn.execute(
        """
        INSERT INTO join_requests
        (name, aparat_id, rubika_id, description)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            aparat_id,
            rubika_id,
            description
        )
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home", joined="1") + "#join")


# =========================================================
# ANONYMOUS MESSAGE
# =========================================================

@app.route("/anonymous", methods=["POST"])
def anonymous_message():

    verify_csrf()

    message = request.form.get("message", "").strip()

    if not message:
        return redirect(url_for("home") + "#anonymous")

    if len(message) > 3000:
        return redirect(url_for("home") + "#anonymous")

    conn = get_db()

    conn.execute(
        """
        INSERT INTO anonymous_messages
        (message)
        VALUES (?)
        """,
        (message,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("home", sent="1") + "#anonymous"
    )


# =========================================================
# PUBLIC NEWS API
# =========================================================

@app.route("/api/public/news")
def public_news_api():

    conn = get_db()

    news = conn.execute("""
        SELECT id, title, content, created_at
        FROM news
        ORDER BY id DESC
        LIMIT 8
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "id": item["id"],
            "title": item["title"],
            "content": item["content"],
            "created_at": item["created_at"]
        }
        for item in news
    ])


# =========================================================
# PUBLIC LATEST NEWS API
# =========================================================

@app.route("/api/public/latest")
def public_latest():

    conn = get_db()

    item = conn.execute("""
        SELECT id, title, content, created_at
        FROM news
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    if not item:
        return jsonify({"news": None})

    return jsonify({
        "news": {
            "id": item["id"],
            "title": item["title"],
            "content": item["content"],
            "created_at": item["created_at"]
        }
    })


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if is_owner():
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":

        verify_csrf()

        ip = request.remote_addr or "unknown"

        if not login_allowed(ip):
            return render_template(
                "admin_login.html",
                error="تعداد تلاش‌های ورود زیاد است. چند دقیقه بعد دوباره امتحان کن."
            )

        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM admin_users
            WHERE username = ?
            """,
            (ADMIN_USERNAME,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):
            FAILED_LOGINS.pop(ip, None)

            session.clear()

            session["owner_logged_in"] = True
            session["owner_username"] = ADMIN_USERNAME
            session["csrf_token"] = secrets.token_urlsafe(32)

            return redirect(url_for("admin_dashboard"))

        register_failed_login(ip)

        return render_template(
            "admin_login.html",
            error="رمز عبور اشتباه است."
        )

    return render_template(
        "admin_login.html",
        error=None
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    required = owner_required()

    if required:
        return required

    conn = get_db()

    news = conn.execute("""
        SELECT *
        FROM news
        ORDER BY id DESC
    """).fetchall()

    joins = conn.execute("""
        SELECT *
        FROM join_requests
        ORDER BY id DESC
    """).fetchall()

    messages = conn.execute("""
        SELECT *
        FROM anonymous_messages
        ORDER BY id DESC
    """).fetchall()

    members = conn.execute("""
        SELECT *
        FROM members
        ORDER BY id DESC
    """).fetchall()

    alliances = conn.execute("""
        SELECT *
        FROM relations
        WHERE kind = 'alliance'
        ORDER BY id DESC
    """).fetchall()

    enemies = conn.execute("""
        SELECT *
        FROM relations
        WHERE kind = 'enemy'
        ORDER BY id DESC
    """).fetchall()

    honors = conn.execute("""
        SELECT *
        FROM honors
        ORDER BY id DESC
    """).fetchall()

    history = conn.execute("""
        SELECT *
        FROM history_events
        ORDER BY id DESC
    """).fetchall()

    stats = conn.execute("""
        SELECT *
        FROM stats
        WHERE id = 1
    """).fetchone()

    pending_joins = conn.execute("""
        SELECT COUNT(*) AS c
        FROM join_requests
        WHERE status = 'pending'
    """).fetchone()["c"]

    unread_messages = conn.execute("""
        SELECT COUNT(*) AS c
        FROM anonymous_messages
        WHERE is_read = 0
    """).fetchone()["c"]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        news=news,
        joins=joins,
        messages=messages,
        members=members,
        alliances=alliances,
        enemies=enemies,
        honors=honors,
        history=history,
        stats=stats,
        pending_joins=pending_joins,
        unread_messages=unread_messages
    )


# =========================================================
# ADMIN ADD NEWS
# =========================================================

@app.route("/admin/news/add", methods=["POST"])
def add_news():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        return redirect(
            url_for("admin_dashboard") + "#news-admin"
        )

    if len(title) > 200 or len(content) > 10000:
        return redirect(
            url_for("admin_dashboard") + "#news-admin"
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO news
        (title, content)
        VALUES (?, ?)
        """,
        (title, content)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#news-admin"
    )


# =========================================================
# ADMIN DELETE NEWS
# =========================================================

@app.route(
    "/admin/news/delete/<int:news_id>",
    methods=["POST"]
)
def delete_news(news_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        "DELETE FROM news WHERE id = ?",
        (news_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#news-admin"
    )


# =========================================================
# ADMIN UPDATE STATS
# =========================================================

@app.route("/admin/stats/update", methods=["POST"])
def update_stats():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    wins = request.form.get("wins", type=int)
    losses = request.form.get("losses", type=int)
    truces = request.form.get("truces", type=int)

    if wins is None or losses is None or truces is None:
        return redirect(
            url_for("admin_dashboard") + "#stats-admin"
        )

    if wins < 0 or losses < 0 or truces < 0:
        return redirect(
            url_for("admin_dashboard") + "#stats-admin"
        )

    conn = get_db()

    conn.execute(
        """
        UPDATE stats
        SET wins = ?, losses = ?, truces = ?
        WHERE id = 1
        """,
        (
            wins,
            losses,
            truces
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#stats-admin"
    )


# =========================================================
# ADMIN JOIN REQUEST STATUS
# =========================================================

@app.route(
    "/admin/join/status/<int:request_id>",
    methods=["POST"]
)
def update_join_status(request_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    status = request.form.get("status", "").strip()

    if status not in {
        "pending",
        "approved",
        "rejected"
    }:
        return redirect(
            url_for("admin_dashboard") + "#join-admin"
        )

    conn = get_db()

    join = conn.execute(
        """
        SELECT *
        FROM join_requests
        WHERE id = ?
        """,
        (request_id,)
    ).fetchone()

    if join:

        conn.execute(
            """
            UPDATE join_requests
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                request_id
            )
        )

        # اگر درخواست تایید شد،
        # کاربر وارد جدول اعضا می‌شود.
        if status == "approved":

            existing = conn.execute(
                """
                SELECT id
                FROM members
                WHERE join_request_id = ?
                """,
                (request_id,)
            ).fetchone()

            if not existing:
                conn.execute(
                    """
                    INSERT INTO members
                    (
                        join_request_id,
                        name,
                        aparat_id,
                        rubika_id,
                        rank,
                        bio,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        request_id,
                        join["name"],
                        join["aparat_id"],
                        join["rubika_id"],
                        "عضو",
                        join["description"],
                        "active"
                    )
                )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#join-admin"
    )


# =========================================================
# ADMIN DELETE JOIN REQUEST
# =========================================================

@app.route(
    "/admin/join/delete/<int:request_id>",
    methods=["POST"]
)
def delete_join(request_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM join_requests
        WHERE id = ?
        """,
        (request_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#join-admin"
    )


# =========================================================
# ADMIN MARK MESSAGE READ
# =========================================================

@app.route(
    "/admin/message/read/<int:message_id>",
    methods=["POST"]
)
def mark_message_read(message_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        UPDATE anonymous_messages
        SET is_read = 1
        WHERE id = ?
        """,
        (message_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#messages-admin"
    )


# =========================================================
# ADMIN DELETE MESSAGE
# =========================================================

@app.route(
    "/admin/message/delete/<int:message_id>",
    methods=["POST"]
)
def delete_message(message_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM anonymous_messages
        WHERE id = ?
        """,
        (message_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#messages-admin"
    )


# =========================================================
# ADMIN ADD MEMBER
# =========================================================

@app.route(
    "/admin/member/add",
    methods=["POST"]
)
def add_member():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    name = request.form.get("name", "").strip()
    aparat_id = request.form.get("aparat_id", "").strip()
    rubika_id = request.form.get("rubika_id", "").strip()
    rank = request.form.get("rank", "").strip()
    bio = request.form.get("bio", "").strip()

    if not name:
        return redirect(
            url_for("admin_dashboard") + "#members-admin"
        )

    if not rank:
        rank = "عضو"

    conn = get_db()

    conn.execute(
        """
        INSERT INTO members
        (
            name,
            aparat_id,
            rubika_id,
            rank,
            bio,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            aparat_id,
            rubika_id,
            rank,
            bio,
            "active"
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#members-admin"
    )


# =========================================================
# ADMIN UPDATE MEMBER
# =========================================================

@app.route(
    "/admin/member/update/<int:member_id>",
    methods=["POST"]
)
def update_member(member_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    name = request.form.get("name", "").strip()
    rank = request.form.get("rank", "").strip()
    status = request.form.get("status", "").strip()
    bio = request.form.get("bio", "").strip()

    if status not in {
        "active",
        "inactive"
    }:
        status = "active"

    if not rank:
        rank = "عضو"

    conn = get_db()

    conn.execute(
        """
        UPDATE members
        SET name = ?,
            rank = ?,
            status = ?,
            bio = ?
        WHERE id = ?
        """,
        (
            name,
            rank,
            status,
            bio,
            member_id
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#members-admin"
    )


# =========================================================
# ADMIN DELETE MEMBER
# =========================================================

@app.route(
    "/admin/member/delete/<int:member_id>",
    methods=["POST"]
)
def delete_member(member_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM members
        WHERE id = ?
        """,
        (member_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#members-admin"
    )


# =========================================================
# ADMIN ADD RELATION
# =========================================================

@app.route(
    "/admin/relation/add",
    methods=["POST"]
)
def add_relation():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    kind = request.form.get("kind", "").strip()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if kind not in {
        "alliance",
        "enemy"
    }:
        return redirect(
            url_for("admin_dashboard") + "#relations-admin"
        )

    if not name:
        return redirect(
            url_for("admin_dashboard") + "#relations-admin"
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO relations
        (kind, name, description)
        VALUES (?, ?, ?)
        """,
        (
            kind,
            name,
            description
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#relations-admin"
    )


# =========================================================
# ADMIN DELETE RELATION
# =========================================================

@app.route(
    "/admin/relation/delete/<int:relation_id>",
    methods=["POST"]
)
def delete_relation(relation_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM relations
        WHERE id = ?
        """,
        (relation_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#relations-admin"
    )


# =========================================================
# ADMIN ADD HONOR
# =========================================================

@app.route(
    "/admin/honor/add",
    methods=["POST"]
)
def add_honor():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    date_label = request.form.get("date_label", "").strip()

    if not title:
        return redirect(
            url_for("admin_dashboard") + "#honors-admin"
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO honors
        (title, description, date_label)
        VALUES (?, ?, ?)
        """,
        (
            title,
            description,
            date_label
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#honors-admin"
    )


# =========================================================
# ADMIN DELETE HONOR
# =========================================================

@app.route(
    "/admin/honor/delete/<int:honor_id>",
    methods=["POST"]
)
def delete_honor(honor_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM honors
        WHERE id = ?
        """,
        (honor_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#honors-admin"
    )


# =========================================================
# ADMIN ADD HISTORY
# =========================================================

@app.route(
    "/admin/history/add",
    methods=["POST"]
)
def add_history():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    year_label = request.form.get("year_label", "").strip()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not year_label or not title or not content:
        return redirect(
            url_for("admin_dashboard") + "#history-admin"
        )

    conn = get_db()

    conn.execute(
        """
        INSERT INTO history_events
        (year_label, title, content)
        VALUES (?, ?, ?)
        """,
        (
            year_label,
            title,
            content
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#history-admin"
    )


# =========================================================
# ADMIN DELETE HISTORY
# =========================================================

@app.route(
    "/admin/history/delete/<int:event_id>",
    methods=["POST"]
)
def delete_history(event_id):

    required = owner_required()

    if required:
        return required

    verify_csrf()

    conn = get_db()

    conn.execute(
        """
        DELETE FROM history_events
        WHERE id = ?
        """,
        (event_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#history-admin"
    )


# =========================================================
# ADMIN CHANGE PASSWORD
# =========================================================

@app.route(
    "/admin/password",
    methods=["POST"]
)
def change_password():

    required = owner_required()

    if required:
        return required

    verify_csrf()

    old_password = request.form.get(
        "old_password",
        ""
    )

    new_password = request.form.get(
        "new_password",
        ""
    )

    if len(new_password) < 8:
        return redirect(
            url_for("admin_dashboard") + "#security-admin"
        )

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM admin_users
        WHERE username = ?
        """,
        (ADMIN_USERNAME,)
    ).fetchone()

    if not user:
        conn.close()

        return redirect(
            url_for("admin_dashboard") + "#security-admin"
        )

    if not check_password_hash(
        user["password_hash"],
        old_password
    ):
        conn.close()

        return redirect(
            url_for("admin_dashboard") + "#security-admin"
        )

    new_hash = generate_password_hash(
        new_password
    )

    conn.execute(
        """
        UPDATE admin_users
        SET password_hash = ?
        WHERE username = ?
        """,
        (
            new_hash,
            ADMIN_USERNAME
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard") + "#security-admin"
    )


# =========================================================
# ADMIN NOTIFICATIONS API
# =========================================================

@app.route("/api/admin/notifications")
def admin_notifications():

    if not is_owner():
        return jsonify({
            "error": "unauthorized"
        }), 401

    conn = get_db()

    pending_joins = conn.execute("""
        SELECT COUNT(*) AS c
        FROM join_requests
        WHERE status = 'pending'
    """).fetchone()["c"]

    unread_messages = conn.execute("""
        SELECT COUNT(*) AS c
        FROM anonymous_messages
        WHERE is_read = 0
    """).fetchone()["c"]

    latest_join = conn.execute("""
        SELECT id, name, created_at
        FROM join_requests
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    latest_message = conn.execute("""
        SELECT id, created_at
        FROM anonymous_messages
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    conn.close()

    return jsonify({

        "pending_joins": pending_joins,

        "unread_messages": unread_messages,

        "latest_join": (
            {
                "id": latest_join["id"],
                "name": latest_join["name"],
                "created_at": latest_join["created_at"]
            }
            if latest_join
            else None
        ),

        "latest_message": (
            {
                "id": latest_message["id"],
                "created_at": latest_message["created_at"]
            }
            if latest_message
            else None
        )

    })


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# =========================================================
# SERVICE WORKER
# =========================================================

@app.route("/sw.js")
def service_worker():

    return app.send_static_file("sw.js")


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(400)
def bad_request(error):

    return (
        "درخواست نامعتبر است.",
        400
    )


@app.errorhandler(404)
def not_found(error):

    return (
        "صفحه پیدا نشد.",
        404
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    init_db()

    print("")
    print("========================================")
    print("       BLACK ARMY WEBSITE")
    print("========================================")
    print("Public : http://127.0.0.1:5000")
    print("Admin  : http://127.0.0.1:5000/admin")
    print("========================================")
    print("")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
