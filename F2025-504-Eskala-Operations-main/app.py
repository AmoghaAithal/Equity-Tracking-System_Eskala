
from db import run_query
# backend/app.py
import os
from pathlib import Path
from flask import Flask, send_from_directory, session, jsonify, redirect
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv

from auth import bp as auth_bp
from equity import bp as equity_bp
from admin import bp as admin_bp
from fx_rates import bp as fx_rates_bp
from reports import bp as reports_bp

load_dotenv()
PORT = int(os.getenv("PORT", 5000))
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

BACKEND_DIR = Path(__file__).resolve().parent
WEB_DIR = BACKEND_DIR / "flaskapp"  # CHANGED: Local path, not server path
UPLOADS_DIR = BACKEND_DIR / "uploads"

app = Flask(
    __name__,
    static_folder=str(WEB_DIR),
    static_url_path=""
)

# ✅ SECRET KEY
app.secret_key = os.getenv("SECRET_KEY", "eskala-dev-secret-key-change-in-production-2025")

# ✅ DATABASE CONFIGURATION - FROM ENVIRONMENT VARIABLES
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'user_management')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# ✅ SESSION CONFIGURATION
app.config['SESSION_COOKIE_NAME'] = 'eskala_session'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_PATH'] = '/'

print("=" * 70)
print("🔧 FLASK SESSION CONFIGURATION")
print(f"   Secret Key: {'SET' if app.secret_key else 'NOT SET'}")
print(f"   Session Cookie Name: {app.config.get('SESSION_COOKIE_NAME')}")
print(f"   Session SameSite: {app.config.get('SESSION_COOKIE_SAMESITE')}")
print(f"   Session Lifetime: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
print("=" * 70)
print("🗄️  DATABASE CONFIGURATION")
print(f"   MySQL Host: {app.config['MYSQL_HOST']}")
print(f"   MySQL User: {app.config['MYSQL_USER']}")
print(f"   MySQL DB: {app.config['MYSQL_DB']}")
print("=" * 70)

# ✅ CORS CONFIGURATION
CORS(app, 
     supports_credentials=True,
     origins=["http://127.0.0.1:5000", "http://localhost:5000", "https://budt748s04t03.rhsmith.umd.edu"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# ---- API blueprints ----
app.register_blueprint(auth_bp)
app.register_blueprint(equity_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(fx_rates_bp)
app.register_blueprint(reports_bp)

# ---- Static file routing ----
@app.route("/")
def root():
    # file is served as a static file at /web/Landing.html
    return send_from_directory(WEB_DIR / "web", "Landing.html")

@app.route("/<path:filename>")
def web_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.get("/uploads/<path:f>")
def uploads(f):
    return send_from_directory(str(UPLOADS_DIR), f)

@app.get("/health")
def health():
    return {"ok": True}

@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    if not session.get('is_authenticated'):
        return jsonify(ok=False, error="Not authenticated"), 401
    
    user_id = session.get('user_id')
    
    # Try to get staff profile first
    result = run_query("""
        SELECT sp.first_name, sp.last_name 
        FROM staff_profile sp 
        WHERE sp.user_id = :uid
    """, uid=user_id).first()
    
    if result:
        return jsonify(ok=True, first_name=result.first_name, last_name=result.last_name)
    
    # Try community rep profile
    result = run_query("""
        SELECT cr.first_name, cr.last_name 
        FROM community_rep_profile cr 
        WHERE cr.user_id = :uid
    """, uid=user_id).first()
    
    if result:
        return jsonify(ok=True, first_name=result.first_name, last_name=result.last_name)
    
    # Fallback to username
    return jsonify(ok=True, first_name=session.get('username'), last_name='')

@app.route('/api/user/role', methods=['GET'])
def get_user_role():
    """Get the role of the currently logged-in user"""
    if not session.get('is_authenticated'):
        return jsonify(ok=False, error="Not authenticated"), 401
    
    user_id = session.get('user_id')
    
    # Get user role
    result = run_query("""
        SELECT r.role_name 
        FROM user_roles ur
        JOIN roles r ON r.role_id = ur.role_id
        WHERE ur.user_id = :uid
        LIMIT 1
    """, uid=user_id).first()
    
    if result:
        return jsonify(ok=True, role=result.role_name)
    
    return jsonify(ok=False, error="Role not found"), 404


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 STARTING ESKALA BACKEND SERVER")
    print(f"   Host: 0.0.0.0")
    print(f"   Port: {PORT}")
    print(f"   Static folder: {app.static_folder}")
    print(f"   Debug mode: True")
    print("=" * 70)
    app.run(host="0.0.0.0", port=PORT, debug=True)