
# auth.py
"""
Authentication routes with:
- User registration (with email verification)
- Login (with approval check)
- Password reset
- Email verification
- Session management
"""

import os
import re
import secrets
from datetime import datetime, timedelta

import bcrypt
from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from db import SessionLocal, run_query

# ============================================
# EMAIL CONFIGURATION
# ============================================
# For production, use a real email service (SendGrid, AWS SES, etc.)
# For development/testing, emails are logged to console

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Environment variables for email (set these in your server)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_FROM = os.environ.get('SMTP_FROM', 'noreply@eskala.org')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

# Set to True to actually send emails, False to just log them
SEND_EMAILS = bool(SMTP_USER and SMTP_PASS)


def send_email(to_email: str, subject: str, html_body: str, text_body: str = None):
    """Send an email. Falls back to console logging if SMTP not configured."""
    if not text_body:
        text_body = html_body.replace('<br>', '\n').replace('</p>', '\n')
    
    if not SEND_EMAILS:
        # Log to console for development
        print("\n" + "="*60)
        print(f"📧 EMAIL TO: {to_email}")
        print(f"📧 SUBJECT: {subject}")
        
        # Determine preview type from subject
        preview_type = None
        subject_lower = subject.lower()
        if "approved" in subject_lower and "not" not in subject_lower:
            preview_type = "approval"
        elif "not approved" in subject_lower or "no aprobada" in subject_lower:
            preview_type = "rejection"
        elif "welcome" in subject_lower or "bienvenido" in subject_lower:
            preview_type = "invite"
        elif "verify" in subject_lower or "verifica" in subject_lower:
            preview_type = "verification"
        elif "reset" in subject_lower or "restablecer" in subject_lower:
            preview_type = "password-reset"
        elif "changed" in subject_lower or "cambiada" in subject_lower:
            preview_type = "password-changed"
        
        if preview_type:
            print(f"📧 PREVIEW: {BASE_URL}/api/admin/email-preview/{preview_type}")
        
        # Extract and display links for easy clicking
        links = re.findall(r'href="([^"]+)"', html_body)
        if links:
            print("📧 LINKS:")
            for link in links:
                if link != "#":
                    print(f"   🔗 {link}")
        
        print("="*60 + "\n")
        return True
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM
        msg['To'] = to_email
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def email_template(title, content, button_text=None, button_url=None, button_color="#166534"):
    """Generate consistent email HTML template with Eskala branding - simplified for email clients"""
    button_html = ""
    if button_text and button_url:
        button_html = f'''
        <tr>
          <td align="center" style="padding: 30px 0;">
            <a href="{button_url}" 
               style="background-color: {button_color}; color: white; padding: 14px 36px; 
                      text-decoration: none; border-radius: 8px; display: inline-block;
                      font-weight: 600; font-size: 16px;">
                {button_text}
            </a>
          </td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #f5f5f5;">
      <table role="presentation" cellspacing="0" cellpadding="0" align="center" style="max-width: 500px; width: 100%; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden;">
        <!-- Orange Header -->
        <tr>
          <td style="background-color: #f48434; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px; font-weight: 700;">{title}</h1>
          </td>
        </tr>
        <!-- Content -->
        <tr>
          <td style="padding: 40px 30px;">
            {content}
          </td>
        </tr>
        <!-- Button -->
        {button_html}
        <!-- Footer -->
        <tr>
          <td style="background-color: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
            <p style="color: #9ca3af; font-size: 12px; margin: 0;">© Eskala Operations</p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    '''


bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Separate blueprint for /api/user/* routes (used by dashboard)
user_bp = Blueprint("user", __name__, url_prefix="/api/user")


def _hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _check_pw(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except:
        return False


def _generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def generate_unique_username(session, base_username):
    """Generate a unique username by appending numbers if needed"""
    # First check if base username is available
    exists = session.execute(text(
        "SELECT 1 FROM users WHERE username = :u LIMIT 1"
    ), {"u": base_username}).first()
    
    if not exists:
        return base_username
    
    # Find the next available number
    counter = 2
    while counter < 1000:  # Safety limit
        candidate = f"{base_username}{counter}"
        exists = session.execute(text(
            "SELECT 1 FROM users WHERE username = :u LIMIT 1"
        ), {"u": candidate}).first()
        if not exists:
            return candidate
        counter += 1
    
    # Fallback: use timestamp
    import time
    return f"{base_username}_{int(time.time())}"


def friendly_error(e):
    """Convert technical SQL errors to user-friendly messages"""
    err_str = str(e).lower()
    if "duplicate entry" in err_str or "unique constraint" in err_str:
        if "email" in err_str:
            return "This email address is already registered."
        elif "username" in err_str:
            return "This username is already taken."
        elif "rtn" in err_str:
            return "This RTN number is already in use."
        return "This record already exists."
    return "An error occurred. Please try again."


# ============================================
# CHECK SESSION
# ============================================
@bp.get("/check-session")
def check_session():
    """Check if user is currently authenticated - used by forms for autosave and role-based UI"""
    if session.get('is_authenticated'):
        return jsonify(
            is_authenticated=True,
            user_id=session.get('user_id'),
            email=session.get('email'),
            username=session.get('username'),
            role=session.get('role')
        )
    return jsonify(is_authenticated=False)


# ============================================
# SIGNUP (with email verification)
# ============================================
@bp.post("/signup")
def signup():
    """
    Register a new user account.
    - Creates user with is_approved=False and email_verified=False
    - Sends verification email
    """
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    acct = (body.get("account_type") or "COMMUNITY_REP").upper()
    prof = body.get("profile") or {}
    
    # Base username from email
    base_username = email.split("@")[0] if email else ""
    
    # Validation
    if not email or not base_username or len(password) < 8:
        return jsonify(ok=False, error="Email, username, and password (min 8 chars) required"), 400
    if acct not in ("STAFF", "COMMUNITY_REP"):
        return jsonify(ok=False, error="Invalid account type"), 400
    
    # Check if email already exists
    existing_email = run_query("SELECT 1 FROM users WHERE email = :e LIMIT 1", e=email).first()
    if existing_email:
        return jsonify(ok=False, error="This email address is already registered."), 409
    
    # Check RTN uniqueness for partners
    rtn = (prof.get("rtn_number") or "").strip()
    if acct == "COMMUNITY_REP" and rtn:
        if run_query("SELECT 1 FROM community_rep_profile WHERE rtn_number=:r LIMIT 1", r=rtn).first():
            return jsonify(ok=False, error="This RTN number is already in use."), 409
    
    # Generate verification token
    verification_token = _generate_token()
    token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    try:
        with SessionLocal() as s, s.begin():
            # Generate unique username
            username = generate_unique_username(s, base_username)
            
            # Create user (is_approved=False, email_verified=False by default)
            uid = s.execute(text("""
                INSERT INTO users (email, username, password_hash, is_active, is_approved, 
                                   email_verified, verification_token, verification_token_expiry)
                VALUES (:e, :u, :h, TRUE, FALSE, FALSE, :vt, :vte)
            """), {
                "e": email,
                "u": username,
                "h": _hash_pw(password),
                "vt": verification_token,
                "vte": token_expiry
            }).lastrowid
            
            # Assign role
            rid = s.execute(text("SELECT role_id FROM roles WHERE role_name=:n"),
                            {"n": acct}).scalar_one()
            s.execute(text("INSERT INTO user_roles (user_id, role_id) VALUES (:u,:r)"),
                      {"u": uid, "r": rid})
            
            # Create profile
            if acct == "COMMUNITY_REP":
                s.execute(text("""
                    INSERT INTO community_rep_profile
                    (user_id, first_name, last_name, title, bank_name, rtn_number)
                    VALUES (:u, :fn, :ln, :t, :b, :rtn)
                """), {
                    "u": uid,
                    "fn": prof.get("first_name") or None,
                    "ln": prof.get("last_name") or None,
                    "t": prof.get("title") or None,
                    "b": prof.get("bank_name") or None,
                    "rtn": rtn or None
                })
            else:
                s.execute(text("""
                    INSERT INTO staff_profile (user_id, first_name, last_name)
                    VALUES (:u, :fn, :ln)
                """), {
                    "u": uid,
                    "fn": prof.get("first_name") or None,
                    "ln": prof.get("last_name") or None
                })
        
        # Send verification email
        verify_url = f"{BASE_URL}/web/verify-email.html?token={verification_token}"
        
        content = '''
        <div style="text-align: center;">
          <div style="background: #dbeafe; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">✉️</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            Thank you for signing up! Please verify your email address by clicking the button below.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
            ¡Gracias por registrarte! Por favor verifica tu correo electrónico haciendo clic en el botón.
          </p>
          <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin: 20px 0;">
            <p style="color: #92400e; font-size: 14px; margin: 0;">
              ⏰ This link expires in 24 hours / Este enlace expira en 24 horas
            </p>
          </div>
          <div style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 16px; margin-top: 20px; text-align: left; border-radius: 4px;">
            <p style="color: #1e40af; font-size: 14px; margin: 0;">
              <strong>Note:</strong> After verifying your email, an administrator will need to approve your account before you can log in.<br><br>
              <strong>Nota:</strong> Después de verificar tu correo, un administrador deberá aprobar tu cuenta antes de que puedas iniciar sesión.
            </p>
          </div>
        </div>
        '''
        
        send_email(
            to_email=email,
            subject="Eskala - Verify Your Email / Verifica tu correo",
            html_body=email_template(
                title="Verify Your Email / Verifica tu correo",
                content=content,
                button_text="Verify Email / Verificar correo",
                button_url=verify_url
            )
        )
        
        return jsonify(
            ok=True, 
            user_id=uid,
            message="Account created! Please check your email to verify your address."
        )
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify(ok=False, error=friendly_error(e)), 500


# ============================================
# EMAIL VERIFICATION
# ============================================
@bp.post("/verify-email")
def verify_email():
    """Verify user's email address using the token"""
    body = request.get_json(silent=True) or {}
    token = (body.get("token") or "").strip()
    
    if not token:
        return jsonify(ok=False, error="Verification token required"), 400
    
    try:
        with SessionLocal() as s, s.begin():
            # Find user with this token and get their role
            user = s.execute(text("""
                SELECT u.user_id, u.email, u.email_verified, u.verification_token_expiry, r.role_name
                FROM users u
                LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                LEFT JOIN roles r ON r.role_id = ur.role_id
                WHERE u.verification_token = :t
            """), {"t": token}).first()
            
            if not user:
                return jsonify(ok=False, error="Invalid or expired verification link"), 400
            
            # Check if already verified
            if user.email_verified:
                return jsonify(ok=True, message="Email already verified", role=user.role_name)
            
            # Check expiry
            if user.verification_token_expiry and user.verification_token_expiry < datetime.utcnow():
                return jsonify(ok=False, error="Verification link has expired. Please request a new one."), 400
            
            # Mark as verified
            s.execute(text("""
                UPDATE users 
                SET email_verified = TRUE, 
                    verification_token = NULL, 
                    verification_token_expiry = NULL 
                WHERE user_id = :uid
            """), {"uid": user.user_id})
            
            user_role = user.role_name
        
        return jsonify(ok=True, message="Email verified successfully! Please wait for admin approval.", role=user_role)
        
    except Exception as e:
        print(f"❌ Email verification error: {e}")
        return jsonify(ok=False, error="Verification failed. Please try again."), 500


@bp.post("/resend-verification")
def resend_verification():
    """Resend verification email"""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    
    if not email:
        return jsonify(ok=False, error="Email required"), 400
    
    try:
        with SessionLocal() as s, s.begin():
            user = s.execute(text("""
                SELECT user_id, email_verified FROM users WHERE email = :e
            """), {"e": email}).first()
            
            if not user:
                # Don't reveal if email exists
                return jsonify(ok=True, message="If this email is registered, a verification link will be sent.")
            
            if user.email_verified:
                return jsonify(ok=False, error="Email is already verified"), 400
            
            # Generate new token
            new_token = _generate_token()
            token_expiry = datetime.utcnow() + timedelta(hours=24)
            
            s.execute(text("""
                UPDATE users 
                SET verification_token = :t, verification_token_expiry = :exp 
                WHERE user_id = :uid
            """), {"t": new_token, "exp": token_expiry, "uid": user.user_id})
        
        # Send email
        verify_url = f"{BASE_URL}/web/verify-email.html?token={new_token}"
        
        content = '''
        <div style="text-align: center;">
          <div style="background: #dbeafe; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">✉️</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            Please click the button below to verify your email address.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
            Por favor haz clic en el botón para verificar tu correo electrónico.
          </p>
          <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin-top: 20px;">
            <p style="color: #92400e; font-size: 14px; margin: 0;">
              ⏰ This link expires in 24 hours / Este enlace expira en 24 horas
            </p>
          </div>
        </div>
        '''
        
        send_email(
            to_email=email,
            subject="Eskala - Verify Your Email / Verifica tu correo",
            html_body=email_template(
                title="Verify Your Email / Verifica tu correo",
                content=content,
                button_text="Verify Email / Verificar correo",
                button_url=verify_url
            )
        )
        
        return jsonify(ok=True, message="Verification email sent")
        
    except Exception as e:
        print(f"❌ Resend verification error: {e}")
        return jsonify(ok=False, error="Failed to resend verification email"), 500


# ============================================
# LOGIN (Staff - by email/username)
# ============================================
@bp.post("/login")
def login():
    """Staff login by email or username"""
    body = request.get_json(silent=True) or {}
    identifier = (body.get("email") or body.get("username") or body.get("email_or_username") or "").strip().lower()
    password = body.get("password") or ""
    
    if not identifier or not password:
        return jsonify(ok=False, error="Email/username and password required"), 400
    
    try:
        # Find user by email or username
        user = run_query("""
            SELECT u.user_id, u.email, u.username, u.password_hash, 
                   u.is_active, u.is_approved, u.email_verified
            FROM users u
            WHERE (u.email = :id OR u.username = :id)
        """, id=identifier).first()
        
        if not user:
            return jsonify(ok=False, error="Invalid credentials"), 401
        
        # Check if password is placeholder (invite pending)
        if user.password_hash == "INVITE_PENDING":
            return jsonify(ok=False, error="Please check your email and set your password first."), 401
        
        # Check password
        if not _check_pw(password, user.password_hash):
            return jsonify(ok=False, error="Invalid credentials"), 401
        
        # Check email verified
        if not user.email_verified:
            return jsonify(ok=False, error="Please verify your email address first."), 403
        
        # Check approval
        if not user.is_approved:
            return jsonify(ok=False, error="Your account is pending admin approval."), 403
        
        # Check active
        if not user.is_active:
            return jsonify(ok=False, error="Your account has been deactivated. Please contact support."), 403
        
        # Get role
        role_row = run_query("""
            SELECT r.role_name FROM roles r
            JOIN user_roles ur ON ur.role_id = r.role_id
            WHERE ur.user_id = :uid
        """, uid=user.user_id).first()
        
        role = role_row.role_name if role_row else None
        
        # Create session
        session.clear()
        session['user_id'] = user.user_id
        session['email'] = user.email
        session['username'] = user.username
        session['role'] = role
        session['is_authenticated'] = True
        
        return jsonify(ok=True, user={
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "role": role
        })
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify(ok=False, error="Login failed. Please try again."), 500


# ============================================
# LOGIN (Partner - by RTN)
# ============================================
@bp.post("/login-partner")
def login_partner():
    """Partner login by RTN number"""
    body = request.get_json(silent=True) or {}
    rtn = (body.get("rtn") or "").strip()
    password = body.get("password") or ""
    
    if not rtn or not password:
        return jsonify(ok=False, error="RTN and password required"), 400
    
    try:
        # Find user by RTN
        user = run_query("""
            SELECT u.user_id, u.email, u.username, u.password_hash,
                   u.is_active, u.is_approved, u.email_verified,
                   cr.bank_name, cr.rtn_number
            FROM users u
            JOIN community_rep_profile cr ON cr.user_id = u.user_id
            WHERE cr.rtn_number = :rtn
        """, rtn=rtn).first()
        
        if not user:
            return jsonify(ok=False, error="Invalid RTN or password"), 401
        
        # Check if password is placeholder (invite pending)
        if user.password_hash == "INVITE_PENDING":
            return jsonify(ok=False, error="Please check your email and set your password first."), 401
        
        # Check password
        if not _check_pw(password, user.password_hash):
            return jsonify(ok=False, error="Invalid RTN or password"), 401
        
        # Check email verified
        if not user.email_verified:
            return jsonify(ok=False, error="Please verify your email address first."), 403
        
        # Check approval
        if not user.is_approved:
            return jsonify(ok=False, error="Your account is pending admin approval."), 403
        
        # Check active
        if not user.is_active:
            return jsonify(ok=False, error="Your account has been deactivated. Please contact support."), 403
        
        # Create session
        session.clear()
        session['user_id'] = user.user_id
        session['email'] = user.email
        session['username'] = user.username
        session['role'] = 'COMMUNITY_REP'
        session['bank_name'] = user.bank_name
        session['rtn'] = user.rtn_number
        session['is_authenticated'] = True
        
        return jsonify(ok=True, user={
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "role": "COMMUNITY_REP",
            "bank_name": user.bank_name
        })
        
    except Exception as e:
        print(f"❌ Partner login error: {e}")
        return jsonify(ok=False, error="Login failed. Please try again."), 500


# ============================================
# LOGOUT
# ============================================
@bp.post("/logout")
def logout():
    """Clear user session"""
    session.clear()
    return jsonify(ok=True)


# ============================================
# GET CURRENT USER
# ============================================
@bp.get("/me")
def get_me():
    """Get current logged-in user info"""
    if 'user_id' not in session:
        return jsonify(ok=False, error="Not logged in"), 401
    
    return jsonify(ok=True, user={
        "user_id": session.get('user_id'),
        "email": session.get('email'),
        "username": session.get('username'),
        "role": session.get('role')
    })


# ============================================
# GET USER ROLE (for dashboard)
# ============================================
@user_bp.get("/role")
def get_role():
    """Get current user's role - used by dashboard to show/hide features"""
    if 'user_id' not in session:
        return jsonify(ok=False, error="Not logged in"), 401
    
    return jsonify(ok=True, role=session.get('role'))


# ============================================
# GET USER INFO (for dashboard welcome message)
# ============================================
@user_bp.get("/info")
def get_info():
    """Get current user's profile info"""
    if 'user_id' not in session:
        return jsonify(ok=False, error="Not logged in"), 401
    
    user_id = session.get('user_id')
    role = session.get('role')
    
    try:
        # Get profile info based on role
        if role == 'STAFF':
            profile = run_query("""
                SELECT first_name, last_name FROM staff_profile WHERE user_id = :uid
            """, uid=user_id).first()
        else:
            profile = run_query("""
                SELECT first_name, last_name, bank_name FROM community_rep_profile WHERE user_id = :uid
            """, uid=user_id).first()
        
        if profile:
            return jsonify(
                ok=True,
                first_name=profile.first_name,
                last_name=profile.last_name,
                bank_name=getattr(profile, 'bank_name', None),
                role=role
            )
        else:
            return jsonify(ok=True, first_name=None, last_name=None, role=role)
            
    except Exception as e:
        print(f"❌ Get user info error: {e}")
        return jsonify(ok=False, error="Failed to get user info"), 500


# ============================================
# PASSWORD RESET
# ============================================
@bp.post("/forgot-password")
def forgot_password():
    """Request a password reset link"""
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    
    if not email:
        return jsonify(ok=False, error="Email required"), 400
    
    try:
        with SessionLocal() as s, s.begin():
            user = s.execute(text("""
                SELECT user_id, email FROM users WHERE email = :e
            """), {"e": email}).first()
            
            if not user:
                # Don't reveal if email exists (security best practice)
                return jsonify(ok=True, message="If this email is registered, a reset link will be sent.")
            
            # Generate reset token
            reset_token = _generate_token()
            token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            s.execute(text("""
                UPDATE users 
                SET reset_token = :t, reset_token_expiry = :exp 
                WHERE user_id = :uid
            """), {"t": reset_token, "exp": token_expiry, "uid": user.user_id})
        
        # Send reset email
        reset_url = f"{BASE_URL}/web/reset-password.html?token={reset_token}"
        
        content = '''
        <div style="text-align: center;">
          <div style="background: #fef3c7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">🔑</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            You requested a password reset for your Eskala account. Click the button below to create a new password.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
            Solicitaste restablecer tu contraseña de Eskala. Haz clic en el botón para crear una nueva contraseña.
          </p>
          <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin: 20px 0;">
            <p style="color: #92400e; font-size: 14px; margin: 0;">
              ⏰ This link expires in 1 hour / Este enlace expira en 1 hora
            </p>
          </div>
          <p style="color: #9ca3af; font-size: 12px; margin-top: 20px;">
            If you didn't request this, please ignore this email. Your password will remain unchanged.<br>
            Si no solicitaste esto, ignora este correo. Tu contraseña no cambiará.
          </p>
        </div>
        '''
        
        send_email(
            to_email=email,
            subject="Eskala - Reset Your Password / Restablecer contraseña",
            html_body=email_template(
                title="Password Reset / Restablecer contraseña",
                content=content,
                button_text="Reset Password / Restablecer contraseña",
                button_url=reset_url
            )
        )
        
        return jsonify(ok=True, message="If this email is registered, a reset link will be sent.")
        
    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return jsonify(ok=False, error="Failed to process request. Please try again."), 500


@bp.post("/reset-password")
def reset_password():
    """Reset password using the token"""
    body = request.get_json(silent=True) or {}
    token = (body.get("token") or "").strip()
    new_password = body.get("password") or ""
    
    if not token:
        return jsonify(ok=False, error="Reset token required"), 400
    if len(new_password) < 8:
        return jsonify(ok=False, error="Password must be at least 8 characters"), 400
    
    try:
        with SessionLocal() as s, s.begin():
            # Get user info including role
            user = s.execute(text("""
                SELECT u.user_id, u.email, u.reset_token_expiry, r.role_name
                FROM users u
                LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                LEFT JOIN roles r ON r.role_id = ur.role_id
                WHERE u.reset_token = :t
            """), {"t": token}).first()
            
            if not user:
                return jsonify(ok=False, error="Invalid or expired reset link"), 400
            
            # Check expiry
            if user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow():
                return jsonify(ok=False, error="Reset link has expired. Please request a new one."), 400
            
            # Update password and clear token
            s.execute(text("""
                UPDATE users 
                SET password_hash = :h, 
                    reset_token = NULL, 
                    reset_token_expiry = NULL 
                WHERE user_id = :uid
            """), {"h": _hash_pw(new_password), "uid": user.user_id})
            
            user_role = user.role_name
            user_email = user.email
        
        # Send confirmation email
        content = '''
        <div style="text-align: center;">
          <div style="background: #dcfce7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">🔒</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            Your password has been successfully changed. You can now log in with your new password.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
            Tu contraseña ha sido cambiada exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña.
          </p>
          <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; margin-top: 20px; text-align: left; border-radius: 4px;">
            <p style="color: #991b1b; font-size: 14px; margin: 0;">
              <strong>⚠️ Security Notice:</strong> If you didn't make this change, contact support immediately.<br><br>
              <strong>⚠️ Aviso de seguridad:</strong> Si no realizaste este cambio, contacta a soporte inmediatamente.
            </p>
          </div>
        </div>
        '''
        
        send_email(
            to_email=user_email,
            subject="Eskala - Password Changed / Contraseña cambiada",
            html_body=email_template(
                title="Password Changed / Contraseña cambiada",
                content=content
            )
        )
        
        # Return role so frontend can redirect to appropriate login page
        return jsonify(ok=True, message="Password reset successfully! You can now log in.", role=user_role)
        
    except Exception as e:
        print(f"❌ Reset password error: {e}")
        return jsonify(ok=False, error="Failed to reset password. Please try again."), 500


@bp.get("/validate-reset-token")
def validate_reset_token():
    """Check if a reset token is valid (for frontend validation)"""
    token = request.args.get("token", "").strip()
    
    if not token:
        return jsonify(valid=False)
    
    try:
        user = run_query("""
            SELECT user_id, reset_token_expiry FROM users WHERE reset_token = :t
        """, t=token).first()
        
        if not user:
            return jsonify(valid=False)
        
        # Check expiry
        if user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow():
            return jsonify(valid=False)
        
        return jsonify(valid=True)
        
    except Exception as e:
        print(f"❌ Token validation error: {e}")
        return jsonify(valid=False)