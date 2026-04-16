from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sqlite3
import os
import socket
import asyncio
import json

load_dotenv()

def get_instance_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'unknown'

# ── App Setup ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'aws-portal-secret-2026'

# ── Login Manager Setup ────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ── Database Setup ─────────────────────────────────────────
DB = 'database.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'user'
        )
    ''')
    # Create default admin if not exists
    admin_pw = generate_password_hash('admin123')
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
              ('admin', admin_pw, 'admin'))
    conn.commit()
    conn.close()

# ── User Class ─────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id       = id
        self.username = username
        self.role     = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[2])
    return None

# ── Routes ─────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row and check_password_hash(row[2], password):
            user = User(row[0], row[1], row[3])
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', instance_ip=get_instance_ip())

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()
    conn.close()
    return render_template('dashboard.html', users=users, instance_ip=get_instance_ip())

@app.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role     = request.form.get('role', 'user')
        hashed   = generate_password_hash(password)
        try:
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, hashed, role))
            conn.commit()
            conn.close()
            flash(f'User "{username}" added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash(f'Username "{username}" already exists.', 'error')
    return render_template('add_user.html')

@app.route('/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        username     = request.form['username']
        new_password = request.form['new_password']
        hashed       = generate_password_hash(new_password)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
        updated = c.rowcount
        conn.commit()
        conn.close()
        if updated:
            flash(f'Password for "{username}" reset successfully!', 'success')
        else:
            flash(f'User "{username}" not found.', 'error')
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ── GitHub MCP ─────────────────────────────────────────────

async def fetch_github_repos(username):
    token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN', '')
    # On Windows, npx is npx.cmd — subprocess needs the full extension
    npx_cmd = 'npx.cmd' if os.name == 'nt' else 'npx'
    server_params = StdioServerParameters(
        command=npx_cmd,
        args=['-y', '@modelcontextprotocol/server-github'],
        env={**os.environ, 'GITHUB_PERSONAL_ACCESS_TOKEN': token}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                'search_repositories',
                {'query': f'user:{username}', 'per_page': 10}
            )
            raw = result.content[0].text
            data = json.loads(raw)
            repos = data.get('items', data) if isinstance(data, dict) else data
            repos = sorted(repos, key=lambda r: r.get('updated_at', ''), reverse=True)
            return [
                {
                    'name':        r.get('name', ''),
                    'description': r.get('description') or 'No description',
                    'stars':       r.get('stargazers_count', 0),
                    'language':    r.get('language') or 'N/A',
                    'url':         r.get('html_url', ''),
                    'updated_at':  r.get('updated_at', '')[:10],
                }
                for r in repos
            ]

@app.route('/github-repos')
@login_required
def github_repos():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'error': 'GitHub username is required'}), 400
    try:
        loop = asyncio.ProactorEventLoop()
        try:
            repos = loop.run_until_complete(fetch_github_repos(username))
        finally:
            loop.close()
        return jsonify({'repos': repos})
    except BaseException as e:
        # Unwrap asyncio ExceptionGroup to get the real error
        if hasattr(e, 'exceptions') and e.exceptions:
            msg = str(e.exceptions[0])
        else:
            msg = str(e.__cause__ or e)
        return jsonify({'error': msg}), 500

# ── Run ────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=True)