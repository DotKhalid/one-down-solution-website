"""OneDown Solution — Flask website and private enquiry inbox."""
import os
import re
import secrets
import sqlite3
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path
import click
from dotenv import load_dotenv
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

ROOT = Path(__file__).resolve().parent
SERVICES = ['Website development', 'Mobile app development', 'Custom software', 'Business systems', 'AI solutions', 'Chatbot development', 'Machine learning', 'Computer vision', 'Data science & analytics', 'Digital marketing', 'Other / help me choose']
STATUSES = ('New', 'In progress', 'Closed')

def create_app(test_config=None):
    load_dotenv(ROOT / '.env')
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY'), DATABASE=str(Path(app.instance_path) / 'onedown.sqlite3'), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('APP_ENV') == 'production', PERMANENT_SESSION_LIFETIME=timedelta(hours=2), MAX_CONTENT_LENGTH=32 * 1024)
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Run python setup.py first to create a local SECRET_KEY.')
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    CSRFProtect(app)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        if 'db' in g:
            g.pop('db').close()

    with app.app_context():
        db().executescript('''
          PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS enquiries (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, service TEXT NOT NULL, budget TEXT NOT NULL, message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'New', created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now')));
          CREATE TABLE IF NOT EXISTS attempts (scope TEXT NOT NULL, address TEXT NOT NULL, happened REAL NOT NULL);
          CREATE INDEX IF NOT EXISTS rate_lookup ON attempts(scope,address,happened);
        ''')
        db().commit()

    def limited(scope, count, seconds):
        # Uses the socket peer, never a client-controlled forwarding header.
        address = request.remote_addr or 'unknown'
        now = time.time()
        conn = db()
        conn.execute('BEGIN IMMEDIATE')
        conn.execute('DELETE FROM attempts WHERE happened < ?', (now - 3600,))
        seen = conn.execute('SELECT count(*) FROM attempts WHERE scope=? AND address=? AND happened>?', (scope, address, now-seconds)).fetchone()[0]
        if seen >= count:
            conn.commit()
            return True
        conn.execute('INSERT INTO attempts VALUES (?,?,?)', (scope, address, now))
        conn.commit()
        return False

    def admin_required(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not session.get('admin_id'):
                return redirect(url_for('login'))
            if not db().execute('SELECT id FROM admin WHERE id=?', (session['admin_id'],)).fetchone():
                session.clear()
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapped

    @app.context_processor
    def context():
        return dict(services=SERVICES, statuses=STATUSES)

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; font-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
        if request.path.startswith('/admin'):
            response.headers['Cache-Control'] = 'no-store'
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    @app.get('/')
    def home():
        return render_template('home.html', title='OneDown Solution | Software built around you', page='home')

    @app.get('/ankaboot-ai')
    def ai():
        return render_template('ai.html', title='Ankaboot.ai | Practical intelligence. Real possibilities.', page='ai')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        values = request.form if request.method == 'POST' else {'service': request.args.get('service', '')}
        errors = []
        if request.method == 'POST':
            if limited('contact', 5, 600):
                return render_template('error.html', code=429, message='Too many submissions. Please try again in 10 minutes or call us.'), 429
            if request.form.get('website'):
                abort(400)
            data = {k: request.form.get(k, '').strip() for k in ('name', 'email', 'phone', 'service', 'budget', 'message')}
            if not 2 <= len(data['name']) <= 100: errors.append('Enter your name (2–100 characters).')
            if len(data['email']) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', data['email']): errors.append('Enter a valid email address.')
            if data['phone'] and not re.fullmatch(r'[+\d() .-]{7,30}', data['phone']): errors.append('Enter a valid phone number, or leave it blank.')
            if data['service'] not in SERVICES: errors.append('Choose a service.')
            if data['budget'] not in ('Not sure yet', 'Under PKR 100,000', 'PKR 100,000–500,000', 'PKR 500,000+', 'Prefer to discuss'): errors.append('Choose a budget range.')
            if not 20 <= len(data['message']) <= 5000: errors.append('Describe your project in 20–5,000 characters.')
            if request.form.get('consent') != 'yes': errors.append('Please agree that we may contact you about this enquiry.')
            if not errors:
                db().execute('INSERT INTO enquiries(name,email,phone,service,budget,message) VALUES (:name,:email,:phone,:service,:budget,:message)', data)
                db().commit()
                flash('Thank you! Your enquiry has been saved. Muhammad Khalid will contact you using the details you provided.', 'success')
                return redirect(url_for('contact'))
        return render_template('contact.html', title='Start a project | OneDown Solution', page='contact', values=values, errors=errors), (400 if errors else 200)

    @app.get('/privacy')
    def privacy():
        return render_template('privacy.html', title='Privacy | OneDown Solution', page='privacy')

    @app.route('/admin/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if limited('login', 5, 900):
                return render_template('error.html', code=429, message='Too many sign-in attempts. Try again in 15 minutes.'), 429
            user = db().execute('SELECT * FROM admin WHERE username=?', (request.form.get('username', ''),)).fetchone()
            # Verify a dummy hash too, so an unknown username is not a fast path.
            hashed = user['password_hash'] if user else app.config.setdefault('DUMMY_HASH', generate_password_hash(secrets.token_hex(24)))
            valid = check_password_hash(hashed, request.form.get('password', ''))
            if user and valid:
                session.clear()
                session['admin_id'] = user['id']
                session.permanent = True
                return redirect(url_for('inbox'))
            error = 'Incorrect username or password.'
        return render_template('login.html', title='Admin sign in | OneDown Solution', page='admin', error=error)

    @app.get('/admin')
    @admin_required
    def inbox():
        status = request.args.get('status', '')
        query = request.args.get('q', '').strip()[:100]
        page_number = request.args.get('page', 1, type=int)
        page_number = max(1, page_number)
        where, args = ['1=1'], []
        if status in STATUSES:
            where.append('status=?'); args.append(status)
        if query:
            where.append('(name LIKE ? OR email LIKE ? OR message LIKE ?)'); args.extend(['%'+query+'%']*3)
        clause = ' AND '.join(where)
        total = db().execute('SELECT count(*) FROM enquiries WHERE '+clause, args).fetchone()[0]
        rows = db().execute('SELECT * FROM enquiries WHERE '+clause+' ORDER BY id DESC LIMIT 20 OFFSET ?', args+[(page_number-1)*20]).fetchall()
        counts = {s: db().execute('SELECT count(*) FROM enquiries WHERE status=?', (s,)).fetchone()[0] for s in STATUSES}
        return render_template('admin.html', title='Enquiry inbox | OneDown Solution', page='admin', rows=rows, counts=counts, total=total, current_status=status, query=query, number=page_number)

    @app.post('/admin/enquiries/<int:enquiry_id>/status')
    @admin_required
    def update_status(enquiry_id):
        status = request.form.get('status')
        if status not in STATUSES: abort(400)
        if not db().execute('SELECT id FROM enquiries WHERE id=?', (enquiry_id,)).fetchone(): abort(404)
        db().execute('UPDATE enquiries SET status=? WHERE id=?', (status, enquiry_id)); db().commit()
        flash('Enquiry status updated.', 'success')
        return redirect(url_for('inbox'))

    @app.post('/admin/logout')
    @admin_required
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.cli.command('create-admin')
    @click.option('--username', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def create_admin(username, password):
        """Create or reset an admin. Password is prompted, never logged."""
        if not 3 <= len(username) <= 80 or len(password) < 12:
            raise click.ClickException('Use a 3–80 character username and at least a 12-character password.')
        db().execute('INSERT INTO admin(username,password_hash) VALUES (?,?) ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash', (username, generate_password_hash(password)))
        db().commit()
        click.echo('Admin saved. Sign in at /admin. Existing sessions expire within two hours.')

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def error_handler(error):
        messages = {400:'This request could not be accepted. Reload the page and try again.',404:'This page could not be found.',413:'This submission is too large.'}
        return render_template('error.html', code=error.code, message=messages[error.code]), error.code
    return app
